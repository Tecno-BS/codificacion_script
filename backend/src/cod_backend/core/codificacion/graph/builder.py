"""
Constructor del grafo de codificación.

Construye el grafo de LangGraph con el flujo optimizado usando el nodo combinado.
"""
from langgraph.graph import StateGraph, END

from .state import EstadoCodificacion
from ..nodes import (
    nodo_preparar_batch,
    nodo_codificar_combinado,
    nodo_ensamblar,
    decidir_continuar,
)


def construir_grafo() -> StateGraph:
    """
    Construye el grafo de codificación optimizado.
    
    El grafo usa el nodo combinado que reduce el costo y latencia en ~70%
    comparado con los nodos separados.
    
    Returns:
        Grafo compilado listo para ejecutar
    """
    workflow = StateGraph(EstadoCodificacion)
    
    # Agregar nodos
    workflow.add_node("preparar_batch", nodo_preparar_batch)
    workflow.add_node("codificar_combinado", nodo_codificar_combinado)
    workflow.add_node("ensamblar", nodo_ensamblar)
    workflow.add_node("finalizar", lambda s: {**s, "batch_actual": s["batch_actual"] + 1})
    
    # Configurar flujo
    workflow.set_entry_point("preparar_batch")
    workflow.add_edge("preparar_batch", "codificar_combinado")
    workflow.add_edge("codificar_combinado", "ensamblar")
    workflow.add_edge("ensamblar", "finalizar")
    
    # Condición para continuar o finalizar
    workflow.add_conditional_edges(
        "finalizar",
        decidir_continuar,
        {"preparar_batch": "preparar_batch", "finalizar": END},
    )
    
    return workflow

