"""
Nodo del grafo: Codificar combinado (validación + evaluación + identificación).

Este nodo optimizado combina las tres operaciones en una sola llamada GPT,
reduciendo el costo y la latencia en ~70% comparado con los nodos separados.
"""
import json
import re
import time
from typing import Any, Dict, List, Set, Tuple

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from ..graph.state import EstadoCodificacion
from ..prompts import load_prompt
from ....config import OPENAI_API_KEY, supports_temperature
from ...utils import (
    extraer_tokens,
    normalizar_texto,
    normalizar_marca_nombre,
    es_marca_o_nombre_propio,
    detectar_codigo_especial,
)

# Constante para limitar códigos existentes en el prompt
MAX_CODIGOS_EXISTENTES = 150


def _reparar_json_llm(texto: str) -> str:
    """
    Intenta reparar JSON malformado de la salida del LLM.
    
    Args:
        texto: Texto JSON potencialmente malformado
        
    Returns:
        Texto JSON reparado
    """
    # Quedarse con el primer bloque que abre y cierra llaves
    if "{" in texto and "}" in texto:
        inicio = texto.find("{")
        fin = texto.rfind("}")
        texto = texto[inicio : fin + 1]

    # Quitar comas antes de cierre
    texto = re.sub(r",\s*([}\]])", r"\1", texto)

    # Intentar comillas dobles coherentes
    texto = texto.replace("'", '"')

    # Añadir comillas a claves no citadas sencillas (palabras alfanuméricas)
    texto = re.sub(r'(?m)^\s*([A-Za-z0-9_]+)\s*:', r'"\1":', texto)
    texto = re.sub(r'([{,]\s*)([A-Za-z0-9_]+)\s*:', r'\1"\2":', texto)
    return texto


def _preparar_respuestas(state: EstadoCodificacion) -> Tuple[List[str], Dict[int, int], Dict[int, bool]]:
    """
    Prepara las respuestas del batch para procesamiento.
    
    Returns:
        Tupla con (respuestas_formateadas, respuestas_especiales, respuestas_rechazadas)
    """
    respuestas = []
    respuestas_especiales: Dict[int, int] = {}
    respuestas_rechazadas_automatico: Dict[int, bool] = {}
    
    for i, resp in enumerate(state["batch_respuestas"]):
        resp_id = i + 1
        texto = resp["texto"]
        
        texto_limpio = str(texto).strip() if texto else ""
        if not texto_limpio or texto_limpio == "-" or texto_limpio == "---" or texto_limpio.replace("-", "").replace(" ", "") == "":
            respuestas_rechazadas_automatico[resp_id] = True
            continue
        
        codigo_esp = detectar_codigo_especial(texto)
        if codigo_esp is not None:
            respuestas_especiales[resp_id] = codigo_esp
        respuestas.append(f"{resp_id}. {texto}")
    
    return respuestas, respuestas_especiales, respuestas_rechazadas_automatico


def _preparar_catalogo(state: EstadoCodificacion) -> str:
    """
    Prepara el catálogo histórico como string para el prompt.
    
    Returns:
        String con el catálogo formateado
    """
    if state["catalogo"]:
        codigos_normales = [c for c in state["catalogo"]]
        return "\n".join([f"  {c['codigo']}. {c['descripcion']}" for c in codigos_normales[:50]])
    return "No hay catálogo histórico disponible."


def _preparar_codigos_existentes(state: EstadoCodificacion) -> str:
    """
    Prepara los códigos ya creados en batches anteriores como string para el prompt.
    Limita a los últimos MAX_CODIGOS_EXISTENTES para evitar prompts muy grandes.
    
    Returns:
        String con los códigos existentes formateados
    """
    codigos_ya_creados: Dict[int, str] = {}
    if state.get("codificaciones"):
        # Recopilar todos los códigos
        todos_codigos: List[Tuple[int, str]] = []
        for cod in state["codificaciones"]:
            for nuevo in cod.get("codigos_nuevos", []):
                cid = nuevo.get("codigo")
                desc = nuevo.get("descripcion", "")
                if cid and desc:
                    todos_codigos.append((cid, desc))
        
        # Ordenar por código (más recientes = códigos más altos) y tomar los últimos N
        todos_codigos.sort(key=lambda x: x[0])
        codigos_recientes = todos_codigos[-MAX_CODIGOS_EXISTENTES:] if len(todos_codigos) > MAX_CODIGOS_EXISTENTES else todos_codigos
        
        for cid, desc in codigos_recientes:
            codigos_ya_creados[cid] = desc
    
    if codigos_ya_creados:
        codigos_existentes_str = "\n**CÓDIGOS NUEVOS YA CREADOS EN BATCHES ANTERIORES:**\n"
        for cid in sorted(codigos_ya_creados.keys()):
            codigos_existentes_str += f"  {cid}: {codigos_ya_creados[cid]}\n"
        codigos_existentes_str += "\n**IMPORTANTE:** Si encuentras un concepto similar a uno de estos, NO crees un código nuevo.\n"
        if len(codigos_ya_creados) >= MAX_CODIGOS_EXISTENTES:
            codigos_existentes_str += f"\n**NOTA:** Se muestran solo los últimos {MAX_CODIGOS_EXISTENTES} códigos creados para mantener el prompt manejable.\n"
        return codigos_existentes_str
    return "No hay códigos nuevos creados en batches anteriores."


def _normalizar_concepto(desc: str) -> str:
    """
    Normaliza un concepto para comparación, manejando marcas/nombres propios.
    
    Args:
        desc: Descripción del concepto
        
    Returns:
        Descripción normalizada
    """
    if not desc:
        return ""
    if es_marca_o_nombre_propio(desc):
        return normalizar_texto(normalizar_marca_nombre(desc))
    return normalizar_texto(desc)


def _filtrar_conceptos_nuevos(
    resultado: Dict[str, Any],
    state: EstadoCodificacion,
    respuestas_norm: List[str]
) -> List[Dict[str, Any]]:
    """
    Filtra conceptos nuevos para eliminar duplicados e inventados.
    
    Args:
        resultado: Resultado del LLM
        state: Estado actual del grafo
        respuestas_norm: Respuestas normalizadas del batch
        
    Returns:
        Lista de análisis filtrados
    """
    def _marca_aparece_en_respuestas(desc: str) -> bool:
        desc_norm = normalizar_texto(normalizar_marca_nombre(desc))
        return any(desc_norm and desc_norm in resp for resp in respuestas_norm)
    
    # Construir conjunto de conceptos ya existentes (catálogo + batches previos)
    conceptos_existentes_norm: Set[str] = set()
    for c in state.get("catalogo", []):
        conceptos_existentes_norm.add(_normalizar_concepto(c.get("descripcion", "")))
    for codif in state.get("codificaciones", []):
        for nuevo in codif.get("codigos_nuevos", []):
            conceptos_existentes_norm.add(_normalizar_concepto(nuevo.get("descripcion", "")))
    
    # Filtrar conceptos nuevos inventados/duplicados (especialmente marcas/nombres)
    analisis_filtrado: List[Dict[str, Any]] = []
    for analisis_data in resultado.get("analisis", []):
        conceptos_filtrados: List[Dict[str, Any]] = []
        vistos_batch: Set[str] = set()
        
        for c in analisis_data.get("conceptos_nuevos", []):
            desc = c.get("descripcion", "")
            desc_norm = _normalizar_concepto(desc)
            if not desc_norm:
                continue
            
            # Si es marca/nombre, solo aceptar si aparece en las respuestas
            if es_marca_o_nombre_propio(desc) and not _marca_aparece_en_respuestas(desc):
                continue
            
            # Evitar duplicados contra catálogo, batches previos y este batch
            if desc_norm in conceptos_existentes_norm or desc_norm in vistos_batch:
                continue
            
            vistos_batch.add(desc_norm)
            conceptos_filtrados.append(c)
        
        analisis_filtrado.append({
            **analisis_data,
            "conceptos_nuevos": conceptos_filtrados,
        })
    
    return analisis_filtrado


def nodo_codificar_combinado(state: EstadoCodificacion) -> EstadoCodificacion:
    """
    Nodo optimizado que combina validación + evaluación + identificación en UNA sola llamada GPT.
    Reduce el costo y la latencia en ~70% comparado con los 3 nodos separados.
    
    Args:
        state: Estado actual del grafo
        
    Returns:
        Estado actualizado con validaciones, evaluaciones y cobertura del batch
    """
    print("\n🚀 Codificando batch (validación + evaluación + identificación combinadas)...")
    
    # Preparar respuestas
    respuestas, respuestas_especiales, respuestas_rechazadas_automatico = _preparar_respuestas(state)
    
    if not respuestas:
        print("   ⚠️  Sin respuestas válidas para procesar")
        return {
            **state,
            "validaciones_batch": [],
            "evaluaciones_batch": [],
            "cobertura_batch": [],
            "respuestas_especiales": respuestas_especiales,
        }
    
    # Preparar contexto para el prompt
    catalogo_str = _preparar_catalogo(state)
    codigos_existentes_str = _preparar_codigos_existentes(state)
    codigo_base = state.get("proximo_codigo_nuevo", 1)
    
    # Cargar prompt combinado
    prompt_template = load_prompt("codificar_combinado")
    prompt = ChatPromptTemplate.from_messages([("system", prompt_template)])
    
    # Configurar LLM
    llm_kwargs = {"model": state["modelo_gpt"], "api_key": OPENAI_API_KEY}
    if supports_temperature(state["modelo_gpt"]):
        llm_kwargs["temperature"] = 0.1
    llm = ChatOpenAI(**llm_kwargs)
    chain = prompt | llm
    
    # Llamar a GPT (UNA SOLA VEZ)
    inicio_tiempo = time.time()
    try:
        respuesta_llm = chain.invoke({
            "pregunta": state["pregunta"],
            "catalogo": catalogo_str,
            "codigos_existentes": codigos_existentes_str,
            "respuestas": "\n".join(respuestas),
            "codigo_base": codigo_base,
        })
    except Exception as e:
        error_msg = str(e)
        # Mejorar mensajes de error comunes de OpenAI
        if "rate limit" in error_msg.lower() or "429" in error_msg:
            raise RuntimeError("Límite de velocidad de la API de OpenAI alcanzado. Por favor, espera unos momentos e intenta de nuevo.")
        elif "invalid_api_key" in error_msg.lower() or "401" in error_msg:
            raise RuntimeError("Clave de API de OpenAI inválida o no configurada correctamente.")
        elif "insufficient_quota" in error_msg.lower():
            raise RuntimeError("Cuota de OpenAI insuficiente. Por favor, verifica tu cuenta.")
        elif "timeout" in error_msg.lower():
            raise RuntimeError("Tiempo de espera agotado al comunicarse con OpenAI. Intenta de nuevo.")
        else:
            raise RuntimeError(f"Error al comunicarse con OpenAI: {error_msg}")
    
    tiempo_llamada = time.time() - inicio_tiempo
    
    prompt_tokens, completion_tokens, _total = extraer_tokens(respuesta_llm)
    print(f"   ✅ Respuesta recibida en {tiempo_llamada:.1f}s ({prompt_tokens + completion_tokens} tokens)")
    
    # Parsear respuesta JSON
    try:
        contenido = respuesta_llm.content
        # Limpiar markdown code blocks si existen
        if "```json" in contenido:
            contenido = contenido.split("```json")[1].split("```")[0].strip()
        elif "```" in contenido:
            contenido = contenido.split("```")[1].split("```")[0].strip()
        try:
            resultado = json.loads(contenido)
        except Exception:
            contenido_reparado = _reparar_json_llm(contenido)
            resultado = json.loads(contenido_reparado)
    except Exception as e:
        raise RuntimeError(f"Error al parsear la salida combinada: {e}\nContenido: {respuesta_llm.content}")
    
    # Filtrar conceptos nuevos
    respuestas_norm = [
        normalizar_texto(str(r.get("texto", ""))) for r in state["batch_respuestas"]
    ]
    analisis_filtrado = _filtrar_conceptos_nuevos(resultado, state, respuestas_norm)
    
    # Procesar validaciones
    validaciones: List[Dict[str, Any]] = []
    idx_llm = 0
    for i, _resp in enumerate(state["batch_respuestas"]):
        rid = i + 1
        if rid in respuestas_rechazadas_automatico:
            validaciones.append({
                "respuesta_id": rid,
                "es_valida": False,
                "razon": "Respuesta vacía o solo contiene guiones",
            })
        elif rid in respuestas_especiales:
            validaciones.append({
                "respuesta_id": rid,
                "es_valida": True,
                "razon": f"Código especial {respuestas_especiales[rid]} detectado automáticamente",
            })
        else:
            if idx_llm < len(resultado.get("validaciones", [])):
                validaciones.append(resultado["validaciones"][idx_llm])
            else:
                validaciones.append({
                    "respuesta_id": rid,
                    "es_valida": True,
                    "razon": "Válida (sin validación específica)",
                })
            idx_llm += 1
    
    # Procesar evaluaciones
    evaluaciones: List[Dict[str, Any]] = []
    for ev_data in resultado.get("evaluaciones", []):
        evaluaciones.append({
            "respuesta_id": ev_data.get("respuesta_id"),
            "evaluaciones": ev_data.get("evaluaciones", []),
        })
    
    # Procesar análisis de cobertura
    cobertura: List[Dict[str, Any]] = []
    for analisis_data in analisis_filtrado:
        cobertura.append({
            "respuesta_id": analisis_data.get("respuesta_id"),
            "respuesta_cubierta_completamente": analisis_data.get("respuesta_cubierta_completamente", False),
            "conceptos_nuevos": analisis_data.get("conceptos_nuevos", []),
        })
    
    validas = sum(1 for v in validaciones if v["es_valida"])
    matches = sum(
        1
        for ev in evaluaciones
        for cod in ev.get("evaluaciones", [])
        if cod.get("aplica") and cod.get("confianza", 0) >= 0.85
    )
    conceptos_nuevos = sum(len(c.get("conceptos_nuevos", [])) for c in cobertura)
    
    print(f"   ✅ Válidas: {validas}/{len(validaciones)}")
    print(f"   ✅ Matches catálogo: {matches}")
    print(f"   ✅ Conceptos nuevos: {conceptos_nuevos}")
    
    total_prompt = state.get("prompt_tokens", 0) + prompt_tokens
    total_completion = state.get("completion_tokens", 0) + completion_tokens
    total_tokens = state.get("total_tokens", 0) + prompt_tokens + completion_tokens
    
    return {
        **state,
        "validaciones_batch": validaciones,
        "evaluaciones_batch": evaluaciones,
        "cobertura_batch": cobertura,
        "respuestas_especiales": respuestas_especiales,
        "prompt_tokens": total_prompt,
        "completion_tokens": total_completion,
        "total_tokens": total_tokens,
    }

