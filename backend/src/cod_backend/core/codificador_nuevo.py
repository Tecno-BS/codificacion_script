"""
Codificador nuevo basado en el Grafo V3 (evaluación booleana) del notebook 06.

Implementa la misma lógica que el grafo de LangGraph, pero empaquetada
como un servicio de backend. Utiliza LangChain + LangGraph y carga los
prompts desde archivos .md para mantener el código limpio.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, TypedDict
from datetime import datetime
import re
import time

import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from pydantic import BaseModel

from ..config import OPENAI_API_KEY, calcular_costo, supports_temperature
from ..utils import load_data, save_data

# Imports de la nueva estructura modular
from .utils import extraer_tokens, normalizar_texto, son_conceptos_similares, detectar_codigo_especial
from .models import (
    ValidacionItem,
    ResultadoValidacion,
    EvaluacionCodigo,
    EvaluacionRespuesta,
    ResultadoEvaluacion,
    ConceptoNuevo,
    AnalisisCobertura,
    ResultadoCobertura,
)
from .codificacion.prompts import load_prompt as _load_prompt
from .codificacion.graph.state import EstadoCodificacion


# ========= Utilidades específicas del notebook =========


def detectar_categoria_desde_texto(texto: str) -> Optional[str]:
    """
    Detecta automáticamente la categoría basándose en el texto del marcador.
    
    Busca palabras clave como "negativa", "neutral", "positiva" en el texto,
    sin importar el formato (1-2 Negativas, 3-Neutras, 4-5 Positivas, etc.).
    
    Retorna: "negativas", "neutrales", "positivas", o None si no se detecta.
    """
    texto_normalizado = normalizar_texto(texto)
    
    # Palabras clave para cada categoría (en singular y plural)
    palabras_negativas = ["negativa", "negativas", "negativo", "negativos"]
    palabras_neutrales = ["neutral", "neutrales", "neutra", "neutras"]
    palabras_positivas = ["positiva", "positivas", "positivo", "positivos"]
    
    # Buscar coincidencias
    for palabra in palabras_negativas:
        if palabra in texto_normalizado:
            return "negativas"
    
    for palabra in palabras_neutrales:
        if palabra in texto_normalizado:
            return "neutrales"
    
    for palabra in palabras_positivas:
        if palabra in texto_normalizado:
            return "positivas"
    
    return None


# ========= Estado del grafo =========
# Estado movido a core.codificacion.graph.state
    pregunta: str
    modelo_gpt: str
    batch_size: int
    respuestas: List[Dict[str, Any]]
    catalogo: List[Dict[str, Any]]
    catalogo_por_categoria: Dict[str, List[Dict[str, Any]]]  # 🆕 Catálogo agrupado por categoría
    batch_actual: int
    batch_respuestas: List[Dict[str, Any]]
    codificaciones: List[Dict[str, Any]]
    validaciones_batch: List[Dict[str, Any]]
    evaluaciones_batch: List[Dict[str, Any]]
    cobertura_batch: List[Dict[str, Any]]
    proximo_codigo_nuevo: int
    respuestas_especiales: Dict[int, int]
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    # 🆕 Configuración de dato auxiliar
    config_auxiliar: Optional[Dict[str, Any]]  # {"usar": bool, "categorizacion": {"negativas": [], "neutrales": [], "positivas": []}}


# ========= Nodos del grafo =========


def nodo_preparar_batch(state: EstadoCodificacion) -> EstadoCodificacion:
    inicio = state["batch_actual"] * state["batch_size"]
    fin = inicio + state["batch_size"]
    batch = state["respuestas"][inicio:fin]
    print(f"\n📦 Preparando batch {state['batch_actual'] + 1}: filas {inicio + 1} a {min(fin, len(state['respuestas']))} de {len(state['respuestas'])}")
    return {**state, "batch_respuestas": batch}


# Funciones movidas a módulos de utilidades y configuración
# _extraer_tokens -> core.utils.token_utils.extraer_tokens
# _supports_temperature -> config.models.supports_temperature


def nodo_validar(state: EstadoCodificacion) -> EstadoCodificacion:
    print("\n✅ Validando respuestas...")
    prompt_template = _load_prompt("validar")

    respuestas = []
    respuestas_especiales: Dict[int, int] = {}
    respuestas_rechazadas_automatico: Dict[int, bool] = {}

    for i, resp in enumerate(state["batch_respuestas"]):
        resp_id = i + 1
        texto = resp["texto"]
        
        # 🆕 MEJORA: Rechazar automáticamente respuestas vacías o solo con "-"
        texto_limpio = str(texto).strip() if texto else ""
        if not texto_limpio or texto_limpio == "-" or texto_limpio == "---" or texto_limpio.replace("-", "").replace(" ", "") == "":
            respuestas_rechazadas_automatico[resp_id] = True
            continue  # No incluir en la lista para el LLM
        
        codigo_esp = detectar_codigo_especial(texto)
        if codigo_esp is not None:
            respuestas_especiales[resp_id] = codigo_esp
        respuestas.append(f"{resp_id}. {texto}")

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", prompt_template),
            ("user", "PREGUNTA:\n{pregunta}\n\nRESPUESTAS:\n{respuestas}"),
        ]
    )

    # Temperature: 0.1 para modelos que lo soportan, sin especificar para GPT-5/O1 (usan 1 por defecto)
    # Igual que el sistema anterior (gpt_hibrido.py)
    llm_kwargs = {"model": state["modelo_gpt"], "api_key": OPENAI_API_KEY}
    if supports_temperature(state["modelo_gpt"]):
        llm_kwargs["temperature"] = 0.1
    llm = ChatOpenAI(**llm_kwargs)

    # Usar LLM directo para capturar tokens y luego parsear JSON estructurado
    chain = prompt | llm
    respuesta_llm = chain.invoke(
        {
            "pregunta": state["pregunta"],
            "respuestas": "\n".join(respuestas),
        }
    )

    prompt_tokens, completion_tokens, _total = extraer_tokens(respuesta_llm)

    # Parsear a modelo estructurado
    try:
        resultado = ResultadoValidacion.model_validate_json(respuesta_llm.content)
    except Exception as e:
        raise RuntimeError(f"Error al parsear la salida de validación: {e}\nContenido: {respuesta_llm.content}")

    validaciones: List[Dict[str, Any]] = []
    idx_llm = 0
    for i, _resp in enumerate(state["batch_respuestas"]):
        rid = i + 1
        # 🆕 MEJORA: Rechazar automáticamente respuestas vacías o solo con "-"
        if rid in respuestas_rechazadas_automatico:
            validaciones.append(
                {
                    "respuesta_id": rid,
                    "es_valida": False,
                    "razon": "Respuesta vacía o solo contiene guiones",
                }
            )
        elif rid in respuestas_especiales:
            validaciones.append(
                {
                    "respuesta_id": rid,
                    "es_valida": True,
                    "razon": f"Código especial {respuestas_especiales[rid]} detectado automáticamente",
                }
            )
        else:
            validaciones.append(resultado.validaciones[idx_llm].model_dump())
            idx_llm += 1

    validas = sum(1 for v in validaciones if v["es_valida"])
    print(f"   ✅ Válidas: {validas}/{len(validaciones)}")

    total_prompt = state.get("prompt_tokens", 0) + prompt_tokens
    total_completion = state.get("completion_tokens", 0) + completion_tokens
    total_tokens = state.get("total_tokens", 0) + prompt_tokens + completion_tokens

    return {
        **state,
        "validaciones_batch": validaciones,
        "respuestas_especiales": respuestas_especiales,
        "prompt_tokens": total_prompt,
        "completion_tokens": total_completion,
        "total_tokens": total_tokens,
    }


def nodo_evaluar_catalogo(state: EstadoCodificacion) -> EstadoCodificacion:
    validas = [
        (i, resp)
        for i, (resp, val) in enumerate(
            zip(state["batch_respuestas"], state["validaciones_batch"])
        )
        if val["es_valida"]
    ]

    if not validas:
        print("   ⚠️  Sin respuestas válidas")
        return {**state, "evaluaciones_batch": []}

    # 🆕 Verificar si se usa dato auxiliar y si hay catálogo por categoría
    config_auxiliar = state.get("config_auxiliar")
    usar_auxiliar = config_auxiliar and config_auxiliar.get("usar", False)
    categorizacion = config_auxiliar.get("categorizacion", {}) if config_auxiliar else {}
    catalogo_por_categoria = state.get("catalogo_por_categoria", {})
    
    # Si se usa dato auxiliar Y hay catálogo por categoría, agrupar respuestas por categoría
    if usar_auxiliar and catalogo_por_categoria:
        print(f"\n📊 Evaluando catálogo por categorías para {len(validas)} respuestas...")
        
        # Agrupar respuestas por categoría
        respuestas_por_categoria: Dict[str, List[Tuple[int, Dict[str, Any]]]] = {}
        for idx, resp in validas:
            dato_aux = resp.get("dato_auxiliar")
            categoria = None
            
            if dato_aux in categorizacion.get("negativas", []):
                categoria = "negativas"
            elif dato_aux in categorizacion.get("neutrales", []):
                categoria = "neutrales"
            elif dato_aux in categorizacion.get("positivas", []):
                categoria = "positivas"
            
            if categoria:
                if categoria not in respuestas_por_categoria:
                    respuestas_por_categoria[categoria] = []
                respuestas_por_categoria[categoria].append((idx, resp))
        
        # Evaluar cada grupo por separado
        todas_evaluaciones: List[Dict[str, Any]] = []
        total_prompt = state.get("prompt_tokens", 0)
        total_completion = state.get("completion_tokens", 0)
        total_tokens = state.get("total_tokens", 0)
        
        prompt_template = _load_prompt("evaluar_catalogo")
        prompt = ChatPromptTemplate.from_messages([("system", prompt_template)])
        
        llm_kwargs = {"model": state["modelo_gpt"], "api_key": OPENAI_API_KEY}
        if supports_temperature(state["modelo_gpt"]):
            llm_kwargs["temperature"] = 0.1
        llm = ChatOpenAI(**llm_kwargs)
        chain = prompt | llm
        
        for categoria, grupo_respuestas in respuestas_por_categoria.items():
            if not grupo_respuestas:
                continue
            
            # Obtener catálogo para esta categoría
            catalogo_categoria = catalogo_por_categoria.get(categoria, [])
            if not catalogo_categoria:
                print(f"   ⚠️  No hay catálogo para categoría '{categoria}', usando catálogo general")
                catalogo_categoria = state["catalogo"]
            
            # Construir strings para el prompt
            respuestas_str = "\n".join([f"{idx+1}. {resp['texto']}" for idx, resp in grupo_respuestas])
            catalogo_str = "\n".join(
                [f"  {c['codigo']}. {c['descripcion']}" for c in catalogo_categoria[:50]]
            )
            
            print(f"   📂 Evaluando {len(grupo_respuestas)} respuestas de categoría '{categoria}' con {len(catalogo_categoria)} códigos")
            
            respuesta_llm = chain.invoke(
                {
                    "catalogo": catalogo_str,
                    "pregunta": state["pregunta"],
                    "respuestas": respuestas_str,
                }
            )
            
            prompt_t, completion_t, _ = extraer_tokens(respuesta_llm)
            total_prompt += prompt_t
            total_completion += completion_t
            total_tokens += prompt_t + completion_t
            
            try:
                resultado = ResultadoEvaluacion.model_validate_json(respuesta_llm.content)
                todas_evaluaciones.extend([ev.model_dump() for ev in resultado.evaluaciones])
            except Exception as e:
                raise RuntimeError(
                    f"Error al parsear la salida de evaluación de catálogo (categoría '{categoria}'): {e}\nContenido: {respuesta_llm.content}"
                )
        
        matches = sum(
            1
            for ev in todas_evaluaciones
            for cod in ev.get("evaluaciones", [])
            if cod.get("aplica") and cod.get("confianza", 0) >= 0.85
        )
        print(f"   ✅ Matches totales (confianza >= 0.85): {matches}")
        
        return {
            **state,
            "evaluaciones_batch": todas_evaluaciones,
            "prompt_tokens": total_prompt,
            "completion_tokens": total_completion,
            "total_tokens": total_tokens,
        }
    
    # 🆕 Caso normal: sin dato auxiliar o sin catálogo por categoría
    if not state["catalogo"]:
        print("   ⚠️  Sin catálogo")
        return {**state, "evaluaciones_batch": []}
    
    print(f"\n📊 Evaluando catálogo para {len(validas)} respuestas...")

    respuestas_str = "\n".join([f"{idx+1}. {resp['texto']}" for idx, resp in validas])

    # TODO: Si en el futuro se reintroducen códigos especiales, aquí se podrían separar.
    codigos_normales = [c for c in state["catalogo"]]

    catalogo_str = "\n".join(
        [f"  {c['codigo']}. {c['descripcion']}" for c in codigos_normales[:30]]
    )

    # Cargar plantilla tal cual (usa {catalogo}, {pregunta}, {respuestas})
    prompt_template = _load_prompt("evaluar_catalogo")
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", prompt_template),
        ]
    )

    # Temperature: 0.1 para modelos que lo soportan, sin especificar para GPT-5/O1 (usan 1 por defecto)
    # Igual que el sistema anterior (gpt_hibrido.py)
    llm_kwargs = {"model": state["modelo_gpt"], "api_key": OPENAI_API_KEY}
    if supports_temperature(state["modelo_gpt"]):
        llm_kwargs["temperature"] = 0.1
    llm = ChatOpenAI(**llm_kwargs)
    chain = prompt | llm

    respuesta_llm = chain.invoke(
        {
            "catalogo": catalogo_str,
            "pregunta": state["pregunta"],
            "respuestas": respuestas_str,
        }
    )

    prompt_tokens, completion_tokens, _total = extraer_tokens(respuesta_llm)

    try:
        resultado = ResultadoEvaluacion.model_validate_json(respuesta_llm.content)
    except Exception as e:
        raise RuntimeError(
            f"Error al parsear la salida de evaluación de catálogo: {e}\nContenido: {respuesta_llm.content}"
        )

    matches = sum(
        1
        for ev in resultado.evaluaciones
        for cod in ev.evaluaciones
        if cod.aplica and cod.confianza >= 0.85
    )
    print(f"   ✅ Matches (confianza >= 0.85): {matches}")

    total_prompt = state.get("prompt_tokens", 0) + prompt_tokens
    total_completion = state.get("completion_tokens", 0) + completion_tokens
    total_tokens = state.get("total_tokens", 0) + prompt_tokens + completion_tokens

    return {
        **state,
        "evaluaciones_batch": [ev.model_dump() for ev in resultado.evaluaciones],
        "prompt_tokens": total_prompt,
        "completion_tokens": total_completion,
        "total_tokens": total_tokens,
    }


def nodo_identificar_conceptos(state: EstadoCodificacion) -> EstadoCodificacion:
    validas_con_eval: List[Dict[str, Any]] = []
    
    # 🆕 Obtener configuración de dato auxiliar
    config_auxiliar = state.get("config_auxiliar")
    usar_auxiliar = config_auxiliar and config_auxiliar.get("usar", False)
    categorizacion = config_auxiliar.get("categorizacion", {}) if config_auxiliar else {}

    for i, (resp, val) in enumerate(
        zip(state["batch_respuestas"], state["validaciones_batch"])
    ):
        if not val["es_valida"]:
            continue

        resp_id = i + 1
        evaluacion = next(
            (ev for ev in state["evaluaciones_batch"] if ev["respuesta_id"] == resp_id),
            None,
        )
        if evaluacion:
            codigos_aplicados = [
                cod["codigo"]
                for cod in evaluacion["evaluaciones"]
                if cod["aplica"] and cod["confianza"] >= 0.85
            ]
        else:
            codigos_aplicados = []

        item: Dict[str, Any] = {
            "respuesta_id": resp_id,
            "texto": resp["texto"],
            "codigos_asignados": codigos_aplicados,
        }
        
        # 🆕 Agregar información de categoría si se usa dato auxiliar
        if usar_auxiliar and "dato_auxiliar" in resp:
            dato_aux = resp["dato_auxiliar"]
            # Determinar categoría
            categoria = None
            if dato_aux in categorizacion.get("negativas", []):
                categoria = "negativa"
            elif dato_aux in categorizacion.get("neutrales", []):
                categoria = "neutral"
            elif dato_aux in categorizacion.get("positivas", []):
                categoria = "positiva"
            
            item["dato_auxiliar"] = dato_aux
            item["categoria"] = categoria

        validas_con_eval.append(item)

    if not validas_con_eval:
        print("   ⚠️  Sin respuestas válidas")
        return {**state, "cobertura_batch": []}

    codigo_base = state["proximo_codigo_nuevo"]
    print(
        f"\n🔍 Analizando cobertura para {len(validas_con_eval)} respuestas..."
        f"\n   (Códigos nuevos empezarán desde: {codigo_base})"
    )

    # Códigos ya creados en batches anteriores
    codigos_ya_creados: Dict[int, str] = {}
    if state.get("codificaciones"):
        for cod in state["codificaciones"]:
            for nuevo in cod.get("codigos_nuevos", []):
                cid = nuevo.get("codigo")
                desc = nuevo.get("descripcion", "")
                if cid and desc:
                    codigos_ya_creados[cid] = desc

    codigos_existentes_str = ""
    if codigos_ya_creados:
        codigos_existentes_str = (
            "\n**CÓDIGOS NUEVOS YA CREADOS EN BATCHES ANTERIORES:**\n"
        )
        for cid in sorted(codigos_ya_creados.keys()):
            codigos_existentes_str += f"  {cid}: {codigos_ya_creados[cid]}\n"
        codigos_existentes_str += (
            "\n**IMPORTANTE:** "
            "Si encuentras un concepto similar a uno de estos, NO crees un código nuevo.\n"
        )

    # 🆕 Agrupar respuestas por categoría si se usa dato auxiliar
    respuestas_por_categoria: Dict[str, List[Dict[str, Any]]] = {}
    respuestas_sin_categoria: List[Dict[str, Any]] = []
    
    if usar_auxiliar:
        for item in validas_con_eval:
            categoria = item.get("categoria")
            if categoria:
                if categoria not in respuestas_por_categoria:
                    respuestas_por_categoria[categoria] = []
                respuestas_por_categoria[categoria].append(item)
            else:
                respuestas_sin_categoria.append(item)
    else:
        respuestas_sin_categoria = validas_con_eval
    
    # Construir string de respuestas con información de categoría
    respuestas_str = ""
    
    # 🆕 Si hay categorización, agrupar por categoría
    if usar_auxiliar and respuestas_por_categoria:
        for categoria, items in respuestas_por_categoria.items():
            categoria_label = categoria.capitalize()
            respuestas_str += f"\n### CATEGORÍA: {categoria_label.upper()}S\n"
            respuestas_str += f"(Datos auxiliares: {', '.join(set(item.get('dato_auxiliar', '') for item in items))})\n\n"
            
            for item in items:
                resp_id = item["respuesta_id"]
                texto = item["texto"]
                codigos = item["codigos_asignados"]
                dato_aux = item.get("dato_auxiliar", "")

                if codigos and state["catalogo"]:
                    descrips = []
                    for cid in codigos:
                        desc = next(
                            (c["descripcion"] for c in state["catalogo"] if c["codigo"] == cid),
                            f"Código {cid}",
                        )
                        descrips.append(f"[{cid}: {desc}]")
                    respuestas_str += (
                        f"{resp_id}. \"{texto}\" (Dato auxiliar: {dato_aux})\n   Códigos asignados: {', '.join(descrips)}\n\n"
                    )
                else:
                    respuestas_str += (
                        f'{resp_id}. "{texto}" (Dato auxiliar: {dato_aux})\n   Códigos asignados: '
                        "NINGUNO (generar códigos para TODA la respuesta)\n\n"
                    )
        
        # Respuestas sin categoría
        if respuestas_sin_categoria:
            respuestas_str += "\n### SIN CATEGORÍA\n\n"
            for item in respuestas_sin_categoria:
                resp_id = item["respuesta_id"]
                texto = item["texto"]
                codigos = item["codigos_asignados"]

                if codigos and state["catalogo"]:
                    descrips = []
                    for cid in codigos:
                        desc = next(
                            (c["descripcion"] for c in state["catalogo"] if c["codigo"] == cid),
                            f"Código {cid}",
                        )
                        descrips.append(f"[{cid}: {desc}]")
                    respuestas_str += (
                        f"{resp_id}. \"{texto}\"\n   Códigos asignados: {', '.join(descrips)}\n\n"
                    )
                else:
                    respuestas_str += (
                        f'{resp_id}. "{texto}"\n   Códigos asignados: '
                        "NINGUNO (generar códigos para TODA la respuesta)\n\n"
                    )
    else:
        # Sin categorización: formato original
        for item in validas_con_eval:
            resp_id = item["respuesta_id"]
            texto = item["texto"]
            codigos = item["codigos_asignados"]

            if codigos and state["catalogo"]:
                descrips = []
                for cid in codigos:
                    desc = next(
                        (c["descripcion"] for c in state["catalogo"] if c["codigo"] == cid),
                        f"Código {cid}",
                    )
                    descrips.append(f"[{cid}: {desc}]")
                respuestas_str += (
                    f"{resp_id}. \"{texto}\"\n   Códigos asignados: {', '.join(descrips)}\n\n"
                )
            else:
                respuestas_str += (
                    f'{resp_id}. "{texto}"\n   Códigos asignados: '
                    "NINGUNO (generar códigos para TODA la respuesta)\n\n"
                )

    # 🆕 Agregar información de categorización al prompt si se usa dato auxiliar
    prompt_template = _load_prompt("identificar_conceptos")
    
    # Si hay categorización, agregar instrucciones adicionales
    if usar_auxiliar and respuestas_por_categoria:
        info_categorias = "\n\n### 🆕 INFORMACIÓN DE CATEGORIZACIÓN POR DATO AUXILIAR\n"
        info_categorias += "Las respuestas están agrupadas por categoría según su dato auxiliar:\n"
        for categoria, items in respuestas_por_categoria.items():
            datos_aux_unicos = sorted(set(item.get("dato_auxiliar", "") for item in items if item.get("dato_auxiliar")))
            categoria_label = categoria.capitalize()
            info_categorias += f"- **{categoria_label.upper()}S**: {', '.join(datos_aux_unicos)}\n"
        info_categorias += "\n**IMPORTANTE:** Al generar códigos nuevos, considera el contexto de la categoría. "
        info_categorias += "Las respuestas de la misma categoría pueden compartir conceptos similares relacionados con esa categoría.\n"
        prompt_template = prompt_template + info_categorias
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", prompt_template),
        ]
    )

    # Temperature: 0.1 para modelos que lo soportan, sin especificar para GPT-5/O1 (usan 1 por defecto)
    # Igual que el sistema anterior (gpt_hibrido.py)
    llm_kwargs = {"model": state["modelo_gpt"], "api_key": OPENAI_API_KEY}
    if supports_temperature(state["modelo_gpt"]):
        llm_kwargs["temperature"] = 0.1
    llm = ChatOpenAI(**llm_kwargs)
    chain = prompt | llm

    inicio_tiempo = time.time()
    respuesta_llm = chain.invoke(
        {
            "pregunta": state["pregunta"],
            "codigos_existentes": codigos_existentes_str,
            "respuestas": respuestas_str,
            "codigo_base": codigo_base,
        }
    )

    prompt_tokens, completion_tokens, _total = extraer_tokens(respuesta_llm)

    try:
        resultado = ResultadoCobertura.model_validate_json(respuesta_llm.content)
    except Exception as e:
        raise RuntimeError(
            f"Error al parsear la salida de identificar_conceptos: {e}\nContenido: {respuesta_llm.content}"
        )

    # Deduplicación de conceptos muy similares
    todos_conceptos_batch: List[Dict[str, Any]] = []
    for analisis in resultado.analisis:
        for concepto in analisis.conceptos_nuevos:
            d = concepto.model_dump()
            d["_respuesta_id"] = analisis.respuesta_id
            todos_conceptos_batch.append(d)

    grupos_similares: Dict[str, List[Dict[str, Any]]] = {}
    for concepto in todos_conceptos_batch:
        desc = concepto.get("descripcion", "")
        desc_norm = normalizar_texto(desc)
        encontrado = False
        for desc_existente, grupo in grupos_similares.items():
            if son_conceptos_similares(desc, desc_existente):
                grupo.append(concepto)
                encontrado = True
                break
        if not encontrado:
            grupos_similares[desc_norm] = [concepto]

    mapeo_deduplicacion: Dict[str, int] = {}
    descripciones_finales: Dict[int, str] = {}
    codigo_unificado = codigo_base

    for desc_norm, grupo in grupos_similares.items():
        if len(grupo) > 1:
            desc_final = min(
                grupo, key=lambda x: len(x.get("descripcion", ""))
            ).get("descripcion", "")
            mapeo_deduplicacion[desc_norm] = codigo_unificado
            descripciones_finales[codigo_unificado] = desc_final
            print(
                f"   🔗 Agrupando {len(grupo)} conceptos similares "
                f"bajo código {codigo_unificado}: {desc_final}"
            )
            codigo_unificado += 1
        else:
            concepto = grupo[0]
            cod_orig = concepto.get("codigo", codigo_unificado)
            mapeo_deduplicacion[desc_norm] = cod_orig
            descripciones_finales[cod_orig] = concepto.get("descripcion", "")
            codigo_unificado = max(codigo_unificado, cod_orig + 1)

    analisis_corregidos: List[Dict[str, Any]] = []
    codigo_actual = codigo_base

    for analisis in resultado.analisis:
        conceptos_nuevos = [c.model_dump() for c in analisis.conceptos_nuevos]
        conceptos_dedup: List[Dict[str, Any]] = []
        codigos_vistos: set[int] = set()

        for concepto in conceptos_nuevos:
            desc = concepto.get("descripcion", "")
            desc_norm = normalizar_texto(desc)

            if desc_norm in mapeo_deduplicacion:
                codigo_final = mapeo_deduplicacion[desc_norm]
                desc_final = descripciones_finales.get(codigo_final, desc)
            else:
                codigo_final = concepto.get("codigo", codigo_actual)
                desc_final = desc

            if codigo_final not in codigos_vistos:
                codigos_vistos.add(codigo_final)
                conceptos_dedup.append(
                    {
                        "codigo": codigo_final,
                        "descripcion": desc_final,
                        "texto_original": concepto.get("texto_original", ""),
                    }
                )

        analisis_corregidos.append(
            {
                "respuesta_id": analisis.respuesta_id,
                "respuesta_cubierta_completamente": analisis.respuesta_cubierta_completamente,
                "conceptos_nuevos": conceptos_dedup,
            }
        )

    if todos_conceptos_batch:
        max_codigo = max(
            c["codigo"]
            for c in todos_conceptos_batch
            if c.get("codigo") is not None
        )
        codigo_actual = max(max_codigo + 1, codigo_base)

    cubiertas = sum(1 for a in analisis_corregidos if a["respuesta_cubierta_completamente"])
    con_nuevos = sum(1 for a in analisis_corregidos if len(a["conceptos_nuevos"]) > 0)
    total_conceptos = sum(len(a["conceptos_nuevos"]) for a in analisis_corregidos)

    print(f"   ✅ Completamente cubiertas: {cubiertas}/{len(analisis_corregidos)}")
    print(f"   🆕 Con conceptos nuevos: {con_nuevos}/{len(analisis_corregidos)}")
    print(f"   🆕 Total conceptos nuevos: {total_conceptos}")

    tiempo_nodo = time.time() - inicio_tiempo
    print(f"   ⏱  Tiempo identificar_conceptos: {tiempo_nodo:.1f}s")

    total_prompt = state.get("prompt_tokens", 0) + prompt_tokens
    total_completion = state.get("completion_tokens", 0) + completion_tokens
    total_tokens = state.get("total_tokens", 0) + prompt_tokens + completion_tokens

    return {
        **state,
        "cobertura_batch": analisis_corregidos,
        "proximo_codigo_nuevo": codigo_actual,
        "prompt_tokens": total_prompt,
        "completion_tokens": total_completion,
        "total_tokens": total_tokens,
    }


def nodo_codificar_combinado(state: EstadoCodificacion) -> EstadoCodificacion:
    """
    Nodo optimizado que combina validación + evaluación + identificación en UNA sola llamada GPT.
    Reduce el costo y la latencia en ~70% comparado con los 3 nodos separados.
    """
    print("\n🚀 Codificando batch (validación + evaluación + identificación combinadas)...")
    
    # Preparar respuestas
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
    
    if not respuestas:
        print("   ⚠️  Sin respuestas válidas para procesar")
        return {
            **state,
            "validaciones_batch": [],
            "evaluaciones_batch": [],
            "cobertura_batch": [],
            "respuestas_especiales": respuestas_especiales,
        }
    
    # Preparar catálogo
    catalogo_str = ""
    if state["catalogo"]:
        codigos_normales = [c for c in state["catalogo"]]
        catalogo_str = "\n".join([f"  {c['codigo']}. {c['descripcion']}" for c in codigos_normales[:50]])
    else:
        catalogo_str = "No hay catálogo histórico disponible."
    
    # Códigos ya creados en batches anteriores
    codigos_ya_creados: Dict[int, str] = {}
    if state.get("codificaciones"):
        for cod in state["codificaciones"]:
            for nuevo in cod.get("codigos_nuevos", []):
                cid = nuevo.get("codigo")
                desc = nuevo.get("descripcion", "")
                if cid and desc:
                    codigos_ya_creados[cid] = desc
    
    codigos_existentes_str = ""
    if codigos_ya_creados:
        codigos_existentes_str = "\n**CÓDIGOS NUEVOS YA CREADOS EN BATCHES ANTERIORES:**\n"
        for cid in sorted(codigos_ya_creados.keys()):
            codigos_existentes_str += f"  {cid}: {codigos_ya_creados[cid]}\n"
        codigos_existentes_str += "\n**IMPORTANTE:** Si encuentras un concepto similar a uno de estos, NO crees un código nuevo.\n"
    else:
        codigos_existentes_str = "No hay códigos nuevos creados en batches anteriores."
    
    # Calcular código base
    codigo_base = state.get("proximo_codigo_nuevo", 1)
    
    # Cargar prompt combinado
    prompt_template = _load_prompt("codificar_combinado")
    prompt = ChatPromptTemplate.from_messages([("system", prompt_template)])
    
    # Configurar LLM
    llm_kwargs = {"model": state["modelo_gpt"], "api_key": OPENAI_API_KEY}
    if supports_temperature(state["modelo_gpt"]):
        llm_kwargs["temperature"] = 0.1
    llm = ChatOpenAI(**llm_kwargs)
    chain = prompt | llm
    
    # Llamar a GPT (UNA SOLA VEZ)
    inicio_tiempo = time.time()
    respuesta_llm = chain.invoke(
        {
            "pregunta": state["pregunta"],
            "catalogo": catalogo_str,
            "codigos_existentes": codigos_existentes_str,
            "respuestas": "\n".join(respuestas),
            "codigo_base": codigo_base,
        }
    )
    tiempo_llamada = time.time() - inicio_tiempo
    
    prompt_tokens, completion_tokens, _total = extraer_tokens(respuesta_llm)
    
    print(f"   ✅ Respuesta recibida en {tiempo_llamada:.1f}s ({prompt_tokens + completion_tokens} tokens)")
    
    # Parsear respuesta JSON
    try:
        import json
        contenido = respuesta_llm.content
        # Limpiar markdown code blocks si existen
        if "```json" in contenido:
            contenido = contenido.split("```json")[1].split("```")[0].strip()
        elif "```" in contenido:
            contenido = contenido.split("```")[1].split("```")[0].strip()
        
        resultado = json.loads(contenido)
    except Exception as e:
        raise RuntimeError(f"Error al parsear la salida combinada: {e}\nContenido: {respuesta_llm.content}")
    
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
    for analisis_data in resultado.get("analisis", []):
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


def nodo_ensamblar(state: EstadoCodificacion) -> EstadoCodificacion:
    print("\n🔧 Ensamblando resultados...")

    codificaciones_batch: List[Dict[str, Any]] = []

    for i, (resp, val) in enumerate(
        zip(state["batch_respuestas"], state["validaciones_batch"])
    ):
        resp_id = i + 1

        if not val["es_valida"]:
            codificaciones_batch.append(
                {
                    "fila_excel": resp["fila_excel"],
                    "texto": resp["texto"],
                    "decision": "rechazar",
                    "codigos_historicos": [],
                    "codigos_nuevos": [],
                    # 🆕 Guardar dato auxiliar/categoría si existe (para exportar por categoría)
                    "dato_auxiliar": resp.get("dato_auxiliar"),
                }
            )
            continue

        # 🆕 Determinar categoría a partir de config_auxiliar y dato_auxiliar de la respuesta
        categoria_resp: Optional[str] = None
        config_auxiliar = state.get("config_auxiliar")
        if config_auxiliar and config_auxiliar.get("usar", False):
            categorizacion = config_auxiliar.get("categorizacion", {})
            dato_aux = resp.get("dato_auxiliar")
            if dato_aux:
                if dato_aux in categorizacion.get("negativas", []):
                    categoria_resp = "negativa"
                elif dato_aux in categorizacion.get("neutrales", []):
                    categoria_resp = "neutral"
                elif dato_aux in categorizacion.get("positivas", []):
                    categoria_resp = "positiva"

        codigo_especial = state.get("respuestas_especiales", {}).get(resp_id)
        if codigo_especial:
            codigos_hist = [codigo_especial]
            codigos_nuevos: List[Dict[str, Any]] = []
            decision = "historico"
        else:
            evaluacion = next(
                (ev for ev in state["evaluaciones_batch"] if ev["respuesta_id"] == resp_id),
                {"evaluaciones": []},
            )
            codigos_hist = [
                c["codigo"]
                for c in evaluacion.get("evaluaciones", [])
                if c["aplica"] and c["confianza"] >= 0.85
            ]
            cobertura = next(
                (c for c in state["cobertura_batch"] if c["respuesta_id"] == resp_id),
                {"conceptos_nuevos": []},
            )
            codigos_nuevos = [
                {
                    "codigo": c["codigo"],
                    "descripcion": c["descripcion"],
                    # 🆕 Propagar categoría al nivel de código nuevo
                    "categoria": categoria_resp,
                }
                for c in cobertura.get("conceptos_nuevos", [])
            ]
            if codigos_hist and codigos_nuevos:
                decision = "mixto"
            elif codigos_hist:
                decision = "historico"
            elif codigos_nuevos:
                decision = "nuevo"
            else:
                decision = "rechazar"

        codificaciones_batch.append(
            {
                "fila_excel": resp["fila_excel"],
                "texto": resp["texto"],
                "decision": decision,
                "codigos_historicos": codigos_hist,
                "codigos_nuevos": codigos_nuevos,
                # 🆕 Guardar categoría a nivel de codificación para trazabilidad
                "dato_auxiliar": resp.get("dato_auxiliar"),
                "categoria": categoria_resp,
            }
        )

    decisiones: Dict[str, int] = {}
    for cod in codificaciones_batch:
        dec = cod["decision"]
        decisiones[dec] = decisiones.get(dec, 0) + 1

    print(f"   📊 Decisiones: {decisiones}")

    return {
        **state,
        "codificaciones": state["codificaciones"] + codificaciones_batch,
    }


def decidir_continuar(state: EstadoCodificacion) -> str:
    # batch_actual ya fue incrementado en el nodo finalizar
    # Verificar si hay más respuestas por procesar
    inicio_siguiente = state["batch_actual"] * state["batch_size"]
    hay_mas = inicio_siguiente < len(state["respuestas"])
    
    if hay_mas:
        print(f"\n🔄 Continuando con batch {state['batch_actual'] + 1}...")
        return "preparar_batch"
    else:
        print(f"\n✅ Todos los batches procesados ({state['batch_actual']} batches completados)")
        return "finalizar"


# ========= Codificador de alto nivel (llamado desde la API) =========


class CodificadorNuevo:
    """
    Codificador que implementa el flujo del Grafo V3 utilizando LangGraph.
    """

    def __init__(self, modelo: str = "gpt-5", config_auxiliar: Optional[Dict[str, Any]] = None):
        self.modelo = modelo
        # 🆕 Configuración de dato auxiliar
        self.config_auxiliar = config_auxiliar
        # Asegurar que cada instancia es única (no hay caché compartido)
        self._instancia_id = id(self)

    async def ejecutar_codificacion(
        self,
        ruta_respuestas: str,
        ruta_codigos: Optional[str] = None,
        progress_callback=None,
    ) -> pd.DataFrame:
        """
        Ejecuta el proceso completo de codificación usando el nuevo grafo.
        """
        print("\n" + "=" * 70)
        print("SISTEMA DE CODIFICACIÓN NUEVO (GRAFO V3)")
        print("=" * 70)
        
        # Agregar timestamp único para evitar caché
        import time
        timestamp_ejecucion = time.time()
        print(f"🕐 Timestamp de ejecución: {timestamp_ejecucion}")

        df = load_data(ruta_respuestas)
        print(f"📊 DataFrame cargado: {len(df)} filas, {len(df.columns)} columnas")
        print(f"📊 Columnas: {list(df.columns)}")
        
        # 🆕 Verificar estructura según si se usa dato auxiliar
        usar_auxiliar = self.config_auxiliar is not None and self.config_auxiliar.get("usar", False)
        
        if usar_auxiliar:
            # Con dato auxiliar: ID (A), Dato Auxiliar (B), Respuestas (C)
            if df.shape[1] < 3:
                raise ValueError(
                    "Con dato auxiliar activado, el archivo debe tener al menos 3 columnas "
                    "(ID, Dato Auxiliar, Respuestas)."
                )
            columna_id = df.columns[0]
            columna_auxiliar = df.columns[1]
            columna_respuesta = df.columns[2]
        else:
            # Sin dato auxiliar: ID (A), Respuestas (B)
            if df.shape[1] < 2:
                raise ValueError(
                    "El archivo de respuestas debe tener al menos 2 columnas "
                    "(ID en la primera, respuestas en la segunda)."
                )
            columna_id = df.columns[0]
            columna_respuesta = df.columns[1]
            columna_auxiliar = None
        
        nombre_pregunta = columna_respuesta

        respuestas_reales: List[Dict[str, Any]] = []
        for idx, row in df.iterrows():
            fila_excel = idx + 2  # +2 porque Excel tiene header en fila 1, y pandas indexa desde 0
            id_valor = row[columna_id]
            if pd.isna(id_valor):
                id_valor = idx + 1

            # Filtrar respuestas vacías o solo con guiones
            raw_val = row[columna_respuesta]
            if pd.isna(raw_val):
                continue
            texto = str(raw_val).strip()
            if texto in ["", "-", "--", "---"]:
                continue
            
            # 🆕 Incluir dato auxiliar si está configurado
            dato_auxiliar = None
            if usar_auxiliar and columna_auxiliar:
                raw_aux = row[columna_auxiliar]
                if not pd.isna(raw_aux):
                    dato_auxiliar = str(raw_aux).strip()
            
            respuesta_item: Dict[str, Any] = {
                "fila_excel": fila_excel,
                "texto": texto,
                "id": id_valor
            }
            
            if dato_auxiliar:
                respuesta_item["dato_auxiliar"] = dato_auxiliar
            
            respuestas_reales.append(respuesta_item)
        
        print(f"📋 Total de filas en el archivo (DataFrame): {len(df)}")
        print(f"📋 Total de respuestas cargadas (incluyendo vacías): {len(respuestas_reales)}")

        # Cargar catálogo histórico (si hay)
        catalogo_historico: List[Dict[str, Any]] = []
        catalogo_por_categoria: Dict[str, List[Dict[str, Any]]] = {}  # 🆕 Soporte para categorías
        
        if ruta_codigos:
            df_cat = load_data(ruta_codigos)
            if "COD" in df_cat.columns and "TEXTO" in df_cat.columns:
                categoria_actual = None
                
                for _, row in df_cat.iterrows():
                    try:
                        codigo = int(row["COD"])
                    except Exception:
                        continue
                    desc = str(row["TEXTO"])
                    
                    # 🆕 Detectar marcadores de categoría (COD >= 1000)
                    if codigo >= 1000:
                        # Es un marcador de categoría
                        # Detectar automáticamente la categoría desde el texto
                        categoria_detectada = detectar_categoria_desde_texto(desc)
                        
                        if categoria_detectada:
                            categoria_actual = categoria_detectada
                            
                            # Inicializar lista para esta categoría si no existe
                            if categoria_actual not in catalogo_por_categoria:
                                catalogo_por_categoria[categoria_actual] = []
                            
                            print(f"   📂 Categoría detectada: {categoria_actual} (COD={codigo}, TEXTO={desc})")
                        else:
                            # No se pudo detectar la categoría, pero es un marcador
                            # Intentar inferir por el orden: primero = negativas, segundo = neutrales, tercero = positivas
                            if codigo == 1000 or (codigo >= 1000 and codigo < 2000):
                                categoria_actual = "negativas"
                            elif codigo == 2000 or (codigo >= 2000 and codigo < 3000):
                                categoria_actual = "neutrales"
                            elif codigo == 3000 or codigo >= 3000:
                                categoria_actual = "positivas"
                            else:
                                # No se puede determinar, usar catálogo general
                                categoria_actual = None
                                print(f"   ⚠️  No se pudo detectar categoría para COD={codigo}, TEXTO={desc}")
                                continue
                            
                            if categoria_actual:
                                if categoria_actual not in catalogo_por_categoria:
                                    catalogo_por_categoria[categoria_actual] = []
                                print(f"   📂 Categoría inferida: {categoria_actual} (COD={codigo}, TEXTO={desc})")
                    else:
                        # Es un código normal, agregarlo a la categoría actual (si hay)
                        codigo_item = {"codigo": codigo, "descripcion": desc}
                        catalogo_historico.append(codigo_item)
                        
                        if categoria_actual:
                            catalogo_por_categoria[categoria_actual].append(codigo_item)
                        else:
                            # Si no hay categoría actual, agregar al catálogo general
                            pass
                
                # Mostrar resumen de categorías
                if catalogo_por_categoria:
                    print(f"\n   📚 Catálogo agrupado por categorías:")
                    for cat, codigos in catalogo_por_categoria.items():
                        print(f"      - {cat}: {len(codigos)} códigos")

        # Calcular código inicial para nuevos códigos
        # Regla: los nuevos códigos SIEMPRE continúan la secuencia del mayor código histórico válido.
        # Ejemplo: si el máximo es 47 → nuevos desde 48; si luego el máximo es 115 → nuevos desde 116, etc.
        print(f"\n🔍 Diagnóstico de código inicial:")
        print(f"   📚 Total códigos en catálogo: {len(catalogo_historico)}")
        if catalogo_historico:
            # Mostrar todos los códigos para diagnóstico
            todos_codigos = [
                c["codigo"] for c in catalogo_historico if isinstance(c["codigo"], int)
            ]
            print(
                f"   📚 Todos los códigos (incluyendo posibles especiales): "
                f"{sorted(todos_codigos)}"
            )

            # Opcional: excluir los antiguos especiales 90–98 si aún existieran
            codigos_validos = [c for c in todos_codigos if not (90 <= c <= 98)]
            print(
                f"   📚 Códigos válidos (excluyendo 90–98): "
                f"{sorted(codigos_validos) if codigos_validos else 'NINGUNO'}"
            )

            if codigos_validos:
                max_codigo = max(codigos_validos)
                proximo_codigo_inicial = max_codigo + 1
                print(f"   ✅ Código máximo en catálogo: {max_codigo}")
                print(f"   ✅ Próximo código inicial: {proximo_codigo_inicial}")
            else:
                # No hay códigos válidos
                proximo_codigo_inicial = 1
                print(f"   ✅ No hay códigos válidos en catálogo, empezando desde 1")
        else:
            proximo_codigo_inicial = 1
            print(f"   ✅ No hay catálogo histórico, empezando desde 1")

        print(f"\n📊 Respuestas cargadas: {len(respuestas_reales)}")
        print(f"📚 Catálogo histórico: {len(catalogo_historico)} códigos")
        print(f"🔢 Código inicial para nuevos códigos: {proximo_codigo_inicial}")

        batch_size = 10
        batches_esperados = (len(respuestas_reales) + batch_size - 1) // batch_size

        estado_inicial: EstadoCodificacion = {
            "pregunta": nombre_pregunta,
            "modelo_gpt": self.modelo,
            "batch_size": batch_size,
            "respuestas": respuestas_reales,
            "catalogo": catalogo_historico,
            "catalogo_por_categoria": catalogo_por_categoria,  # 🆕 Catálogo agrupado por categoría
            "batch_actual": 0,
            "batch_respuestas": [],
            "codificaciones": [],
            "validaciones_batch": [],
            "evaluaciones_batch": [],
            "cobertura_batch": [],
            "proximo_codigo_nuevo": proximo_codigo_inicial,
            "respuestas_especiales": {},
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            # 🆕 Configuración de dato auxiliar
            "config_auxiliar": self.config_auxiliar,
        }

        # Construir grafo
        workflow = StateGraph(EstadoCodificacion)
        workflow.add_node("preparar_batch", nodo_preparar_batch)
        
        # 🚀 OPTIMIZACIÓN: Usar nodo combinado (1 llamada GPT) en lugar de 3 nodos separados
        # Esto reduce el costo y la latencia en ~70%
        # Para usar los nodos separados, cambia USE_NODO_COMBINADO a False
        USE_NODO_COMBINADO = True  # Cambiar a False para usar nodos separados
        
        if USE_NODO_COMBINADO:
            print("🚀 Usando nodo combinado (optimizado - 1 llamada GPT por batch)")
            workflow.add_node("codificar_combinado", nodo_codificar_combinado)
            workflow.add_node("ensamblar", nodo_ensamblar)
            workflow.add_node("finalizar", lambda s: {**s, "batch_actual": s["batch_actual"] + 1})
            
            workflow.set_entry_point("preparar_batch")
            workflow.add_edge("preparar_batch", "codificar_combinado")
            workflow.add_edge("codificar_combinado", "ensamblar")
            workflow.add_edge("ensamblar", "finalizar")
        else:
            print("⚠️  Usando nodos separados (3 llamadas GPT por batch - más lento y costoso)")
            workflow.add_node("validar", nodo_validar)
            workflow.add_node("evaluar_catalogo", nodo_evaluar_catalogo)
            workflow.add_node("identificar_conceptos", nodo_identificar_conceptos)
            workflow.add_node("ensamblar", nodo_ensamblar)
            workflow.add_node("finalizar", lambda s: {**s, "batch_actual": s["batch_actual"] + 1})
            
            workflow.set_entry_point("preparar_batch")
            workflow.add_edge("preparar_batch", "validar")
            workflow.add_edge("validar", "evaluar_catalogo")
            workflow.add_edge("evaluar_catalogo", "identificar_conceptos")
            workflow.add_edge("identificar_conceptos", "ensamblar")
            workflow.add_edge("ensamblar", "finalizar")
        workflow.add_conditional_edges(
            "finalizar",
            decidir_continuar,
            {"preparar_batch": "preparar_batch", "finalizar": END},
        )

        app = workflow.compile()

        # Ejecutar grafo completo
        from langgraph.pregel.main import RunnableConfig

        recursion_limit = max(batches_esperados * 10, 100)
        config = RunnableConfig(recursion_limit=recursion_limit)

        print("\n🚀 Ejecutando grafo nuevo...\n")
        
        # 🆕 MEJORA: Ejecutar el stream en un hilo separado para no bloquear el event loop
        import asyncio
        
        estado_final: EstadoCodificacion = estado_inicial
        total_batches = batches_esperados
        
        if progress_callback:
            # Calcular progreso inicial
            progreso_inicial = 0.0
            mensaje_inicial = f"🚀 Iniciando codificación de {len(respuestas_reales)} respuestas en {total_batches} batches..."
            progress_callback(progreso_inicial, mensaje_inicial)
        
        # Función síncrona para ejecutar el stream en un hilo
        def ejecutar_stream():
            """Ejecuta el stream del grafo en un hilo separado"""
            estado_resultado = estado_inicial
            for event in app.stream(estado_inicial, config=config):
                # event es un dict con el nombre del nodo como clave
                for node_name, node_state in event.items():
                    estado_resultado = node_state
                    
                    if progress_callback:
                        batch_actual = estado_resultado.get("batch_actual", 0)
                        total_respuestas = len(estado_resultado.get("respuestas", []))
                        batch_size = estado_resultado.get("batch_size", 10)
                        
                        # Actualizar progreso según el nodo
                        if node_name == "preparar_batch":
                            respuestas_procesadas = batch_actual * batch_size
                            if total_respuestas > 0:
                                progreso = min(respuestas_procesadas / total_respuestas, 0.98)
                                mensaje = f"📦 Preparando batch {batch_actual + 1}/{total_batches}"
                                progress_callback(progreso, mensaje)
                        
                        elif node_name == "validar":
                            respuestas_procesadas = batch_actual * batch_size
                            if total_respuestas > 0:
                                progreso = min((respuestas_procesadas + batch_size * 0.1) / total_respuestas, 0.98)
                                mensaje = f"✅ Validando respuestas del batch {batch_actual + 1}/{total_batches}"
                                progress_callback(progreso, mensaje)
                        
                        elif node_name == "evaluar_catalogo":
                            respuestas_procesadas = batch_actual * batch_size
                            if total_respuestas > 0:
                                progreso = min((respuestas_procesadas + batch_size * 0.3) / total_respuestas, 0.98)
                                mensaje = f"📊 Evaluando catálogo histórico (batch {batch_actual + 1}/{total_batches})"
                                progress_callback(progreso, mensaje)
                        
                        elif node_name == "identificar_conceptos":
                            respuestas_procesadas = batch_actual * batch_size
                            if total_respuestas > 0:
                                progreso = min((respuestas_procesadas + batch_size * 0.6) / total_respuestas, 0.98)
                                mensaje = f"🔍 Identificando conceptos nuevos (batch {batch_actual + 1}/{total_batches})"
                                progress_callback(progreso, mensaje)
                        
                        elif node_name == "ensamblar":
                            respuestas_procesadas = batch_actual * batch_size
                            if total_respuestas > 0:
                                progreso = min((respuestas_procesadas + batch_size * 0.9) / total_respuestas, 0.98)
                                mensaje = f"🔧 Ensamblando resultados (batch {batch_actual + 1}/{total_batches})"
                                progress_callback(progreso, mensaje)
                        
                        elif node_name == "finalizar":
                            batch_actual_final = estado_resultado.get("batch_actual", 0)
                            if batch_actual_final >= total_batches:
                                # Proceso completado
                                progress_callback(1.0, "✅ Codificación completada")
                            else:
                                # Continuando con siguiente batch
                                respuestas_procesadas = batch_actual_final * batch_size
                                if total_respuestas > 0:
                                    progreso = min(respuestas_procesadas / total_respuestas, 0.98)
                                    mensaje = f"🔄 Batch {batch_actual_final}/{total_batches} completado, continuando..."
                                    progress_callback(progreso, mensaje)
            
            return estado_resultado
        
        # Ejecutar en un hilo separado para no bloquear el event loop
        estado_final = await asyncio.to_thread(ejecutar_stream)

        # Construir DataFrame de resultados (igual que en el notebook)
        decisiones: Dict[str, int] = {}
        for c in estado_final["codificaciones"]:
            dec = c["decision"]
            decisiones[dec] = decisiones.get(dec, 0) + 1
        print(f"\n📈 Decisiones: {decisiones}")

        # Exportar al mismo formato que el notebook
        datos_exportar: List[Dict[str, Any]] = []

        # Mapeo fila_excel -> ID
        mapeo_id: Dict[int, Any] = {}
        for idx, row in df.iterrows():
            fila_excel = idx + 2
            id_valor = row[columna_id]
            if pd.isna(id_valor):
                id_valor = idx + 1
            mapeo_id[fila_excel] = id_valor

        for cod in estado_final["codificaciones"]:
            fila_excel = cod["fila_excel"]
            id_valor = mapeo_id.get(fila_excel, fila_excel - 1)

            codigos_asignados: List[str] = []
            if cod["codigos_historicos"]:
                codigos_asignados.extend([str(c) for c in cod["codigos_historicos"]])
            if cod["codigos_nuevos"]:
                codigos_asignados.extend([str(n["codigo"]) for n in cod["codigos_nuevos"]])

            codigos_final = "; ".join(codigos_asignados) if codigos_asignados else ""

            datos_exportar.append(
                {
                    "ID": id_valor,
                    nombre_pregunta: cod["texto"],
                    "Códigos asignados": codigos_final,
                }
            )

        df_resultados = pd.DataFrame(datos_exportar)

        # Catálogo de códigos nuevos
        # 🆕 Incluir categoría (negativa/neutral/positiva) cuando exista
        codigos_nuevos_unicos: Dict[int, Dict[str, Any]] = {}
        for cod in estado_final["codificaciones"]:
            categoria_cod = cod.get("categoria")
            for nuevo in cod["codigos_nuevos"]:
                cid = nuevo["codigo"]
                desc = nuevo["descripcion"]
                cat_nuevo = nuevo.get("categoria", categoria_cod)

                if cid not in codigos_nuevos_unicos:
                    codigos_nuevos_unicos[cid] = {
                        "descripcion": desc,
                        "categoria": cat_nuevo,
                    }
                else:
                    # Si ya existe pero sin categoría, intenta actualizarla
                    if not codigos_nuevos_unicos[cid].get("categoria") and cat_nuevo:
                        codigos_nuevos_unicos[cid]["categoria"] = cat_nuevo

        # Ordenar por categoría (negativas -> neutrales -> positivas -> sin categoría) y luego por código
        orden_categoria = {"negativa": 0, "neutral": 1, "positiva": 2, None: 3}

        filas_catalogo = []
        for cid, data_cod in codigos_nuevos_unicos.items():
            cat = data_cod.get("categoria")
            filas_catalogo.append(
                {
                    "CATEGORIA": cat.capitalize() if isinstance(cat, str) else "",
                    "COD": cid,
                    "TEXTO": data_cod["descripcion"],
                    "_orden_cat": orden_categoria.get(cat, 3),
                }
            )

        df_catalogo_nuevos: pd.DataFrame = pd.DataFrame(filas_catalogo)
        if not df_catalogo_nuevos.empty:
            df_catalogo_nuevos = df_catalogo_nuevos.sort_values(
                by=["_orden_cat", "COD"]
            ).drop(columns=["_orden_cat"])

        # Guardar a un solo DataFrame "principal"; la API existente se encarga de
        # escribir a disco usando save_data / exportar_catalogo si es necesario.
        # Aquí devolvemos solo df_resultados para mantener compatibilidad.

        # (El backend actual espera un DataFrame de resultados; los archivos
        #  finales se guardan en la ruta de la API.)

        # Para que el backend pueda exportar también los códigos nuevos, los
        # devolvemos como atributo adicional y calculamos métricas simples.
        self.df_codigos_nuevos = df_catalogo_nuevos
        total_respuestas_codificadas = len(estado_final["codificaciones"])
        total_codigos_nuevos = len(df_catalogo_nuevos) if not df_catalogo_nuevos.empty else 0
        total_codigos_historicos = sum(
            len(c["codigos_historicos"]) for c in estado_final["codificaciones"]
        )
        # Métricas de uso de tokens acumuladas en el estado del grafo
        prompt_tokens = estado_final.get("prompt_tokens", 0)
        completion_tokens = estado_final.get("completion_tokens", 0)
        total_tokens = estado_final.get("total_tokens", 0)

        # Calcular costo según el modelo seleccionado y los precios por 1K tokens
        costo_total = calcular_costo(prompt_tokens, completion_tokens, self.modelo)

        self.stats = {
            "total_respuestas_codificadas": total_respuestas_codificadas,
            "total_codigos_nuevos": total_codigos_nuevos,
            "total_codigos_historicos": total_codigos_historicos,
            "total_tokens": total_tokens,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "costo_total": costo_total,
        }

        return df_resultados

    def exportar_catalogo_nuevos(self, nombre_proyecto: str) -> Optional[str]:
        """
        Exporta el catálogo de códigos nuevos generado en la última ejecución.
        """
        df_catalogo_nuevos: Optional[pd.DataFrame] = getattr(
            self, "df_codigos_nuevos", None
        )
        if df_catalogo_nuevos is None or df_catalogo_nuevos.empty:
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta_salida = (
            Path("result/codigos_nuevos")
            / f"{nombre_proyecto}_codigos_nuevos_{timestamp}.xlsx"
        )
        ruta_salida.parent.mkdir(parents=True, exist_ok=True)
        save_data(df_catalogo_nuevos, str(ruta_salida))
        return str(ruta_salida)


