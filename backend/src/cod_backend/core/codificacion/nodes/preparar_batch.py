"""
Nodo del grafo: Preparar batch de respuestas.
"""
from ..graph.state import EstadoCodificacion


def nodo_preparar_batch(state: EstadoCodificacion) -> EstadoCodificacion:
    """
    Prepara el siguiente batch de respuestas para procesar.
    
    Args:
        state: Estado actual del grafo
        
    Returns:
        Estado actualizado con el batch de respuestas preparado
    """
    inicio = state["batch_actual"] * state["batch_size"]
    fin = inicio + state["batch_size"]
    batch = state["respuestas"][inicio:fin]
    print(f"\n📦 Preparando batch {state['batch_actual'] + 1}: filas {inicio + 1} a {min(fin, len(state['respuestas']))} de {len(state['respuestas'])}")
    return {**state, "batch_respuestas": batch}

