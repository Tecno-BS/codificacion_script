"""
Nodo del grafo: Ensamblar resultados del batch.

Combina validaciones, evaluaciones y cobertura en codificaciones finales,
y realiza validación y deduplicación de códigos nuevos.
"""
from typing import Any, Dict, List, Optional, Set

from ..graph.state import EstadoCodificacion
from ...utils import (
    normalizar_texto,
    normalizar_marca_nombre,
    es_marca_o_nombre_propio,
)


def _determinar_categoria_respuesta(
    resp: Dict[str, Any],
    state: EstadoCodificacion
) -> Optional[str]:
    """
    Determina la categoría de una respuesta basándose en config_auxiliar.
    
    Args:
        resp: Respuesta del batch
        state: Estado actual del grafo
        
    Returns:
        Categoría ("negativa", "neutral", "positiva") o None
    """
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
    return categoria_resp


def _validar_y_deduplicar_codigos(
    codificaciones_batch: List[Dict[str, Any]],
    state: EstadoCodificacion
) -> List[Dict[str, Any]]:
    """
    Valida y deduplica códigos nuevos del batch.
    
    Args:
        codificaciones_batch: Lista de codificaciones del batch
        state: Estado actual del grafo
        
    Returns:
        Lista de codificaciones con códigos validados y deduplicados
    """
    codigos_nuevos_batch: List[Dict[str, Any]] = []
    for cod in codificaciones_batch:
        codigos_nuevos_batch.extend(cod.get("codigos_nuevos", []))
    
    if not codigos_nuevos_batch:
        return codificaciones_batch
    
    # Recopilar todos los códigos existentes (históricos + batches anteriores)
    codigos_existentes_map: Dict[str, int] = {}  # desc_normalizada -> codigo
    
    # Del catálogo histórico
    for cat_item in state.get("catalogo", []):
        desc = cat_item.get("descripcion", "")
        if desc:
            desc_norm = normalizar_texto(desc)
            codigos_existentes_map[desc_norm] = cat_item.get("codigo")
    
    # De batches anteriores
    for cod_prev in state.get("codificaciones", []):
        for nuevo_prev in cod_prev.get("codigos_nuevos", []):
            desc = nuevo_prev.get("descripcion", "")
            if desc:
                desc_norm = normalizar_texto(desc)
                codigos_existentes_map[desc_norm] = nuevo_prev.get("codigo")
    
    # Validar y deduplicar códigos nuevos del batch actual
    codigos_vistos_batch: Dict[str, Dict[str, Any]] = {}  # desc_normalizada -> código_info
    duplicados_encontrados = 0
    
    for cod_nuevo in codigos_nuevos_batch:
        desc = cod_nuevo.get("descripcion", "")
        if not desc:
            continue
        
        desc_norm = normalizar_texto(desc)
        
        # Verificar si ya existe en catálogo histórico o batches anteriores
        if desc_norm in codigos_existentes_map:
            codigo_existente = codigos_existentes_map[desc_norm]
            print(f"   ⚠️  Duplicado detectado: '{desc}' ya existe como código {codigo_existente}")
            duplicados_encontrados += 1
            continue
        
        # Verificar si ya existe en este batch
        if desc_norm in codigos_vistos_batch:
            codigo_existente_batch = codigos_vistos_batch[desc_norm].get("codigo")
            print(f"   ⚠️  Duplicado en batch: '{desc}' ya fue creado como código {codigo_existente_batch}")
            duplicados_encontrados += 1
            continue
        
        # Para marcas/nombres propios, normalizar la descripción
        if es_marca_o_nombre_propio(desc):
            desc_normalizada = normalizar_marca_nombre(desc)
            cod_nuevo["descripcion"] = desc_normalizada
            desc_norm = normalizar_texto(desc_normalizada)
        
        codigos_vistos_batch[desc_norm] = cod_nuevo
    
    if duplicados_encontrados > 0:
        print(f"   ⚠️  {duplicados_encontrados} códigos duplicados detectados y eliminados")
    
    # Crear mapeo de códigos originales a códigos validados
    mapeo_codigos_validos: Dict[int, Dict[str, Any]] = {}  # codigo_original -> codigo_validado
    
    for cod_nuevo in codigos_nuevos_batch:
        desc = cod_nuevo.get("descripcion", "")
        if not desc:
            continue
        desc_norm = normalizar_texto(desc)
        codigo_orig = cod_nuevo.get("codigo")
        
        # Si el código está en codigos_vistos_batch, significa que es válido y único
        if desc_norm in codigos_vistos_batch:
            mapeo_codigos_validos[codigo_orig] = codigos_vistos_batch[desc_norm]
    
    # Actualizar códigos nuevos en codificaciones_batch con los validados
    for cod in codificaciones_batch:
        codigos_nuevos_validados = []
        codigos_ya_agregados: Set[str] = set()  # Para evitar duplicados dentro de la misma respuesta
        
        for cod_nuevo in cod.get("codigos_nuevos", []):
            codigo_orig = cod_nuevo.get("codigo")
            
            # Si el código está en el mapeo de válidos, usarlo
            if codigo_orig in mapeo_codigos_validos:
                codigo_validado = mapeo_codigos_validos[codigo_orig]
                desc_validada = codigo_validado.get("descripcion", "")
                desc_norm = normalizar_texto(desc_validada)
                
                # Solo agregar si no lo hemos agregado ya (evitar duplicados en misma respuesta)
                if desc_norm not in codigos_ya_agregados:
                    codigos_nuevos_validados.append(codigo_validado)
                    codigos_ya_agregados.add(desc_norm)
        
        cod["codigos_nuevos"] = codigos_nuevos_validados
    
    return codificaciones_batch


def nodo_ensamblar(state: EstadoCodificacion) -> EstadoCodificacion:
    """
    Ensambla los resultados del batch en codificaciones finales.
    
    Args:
        state: Estado actual del grafo
        
    Returns:
        Estado actualizado con codificaciones del batch agregadas
    """
    print("\n🔧 Ensamblando resultados...")
    
    codificaciones_batch: List[Dict[str, Any]] = []
    
    for i, (resp, val) in enumerate(
        zip(state["batch_respuestas"], state["validaciones_batch"])
    ):
        resp_id = i + 1
        
        if not val["es_valida"]:
            codificaciones_batch.append({
                "fila_excel": resp["fila_excel"],
                "texto": resp["texto"],
                "decision": "rechazar",
                "codigos_historicos": [],
                "codigos_nuevos": [],
                "dato_auxiliar": resp.get("dato_auxiliar"),
            })
            continue
        
        # Determinar categoría a partir de config_auxiliar y dato_auxiliar de la respuesta
        categoria_resp = _determinar_categoria_respuesta(resp, state)
        
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
        
        codificaciones_batch.append({
            "fila_excel": resp["fila_excel"],
            "texto": resp["texto"],
            "decision": decision,
            "codigos_historicos": codigos_hist,
            "codigos_nuevos": codigos_nuevos,
            "dato_auxiliar": resp.get("dato_auxiliar"),
            "categoria": categoria_resp,
        })
    
    # Validar y deduplicar códigos nuevos
    codificaciones_batch = _validar_y_deduplicar_codigos(codificaciones_batch, state)
    
    decisiones: Dict[str, int] = {}
    for cod in codificaciones_batch:
        dec = cod["decision"]
        decisiones[dec] = decisiones.get(dec, 0) + 1
    
    print(f"   📊 Decisiones: {decisiones}")
    
    return {
        **state,
        "codificaciones": state["codificaciones"] + codificaciones_batch,
    }

