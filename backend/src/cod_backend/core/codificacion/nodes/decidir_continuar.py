"""
Nodo del grafo: Decidir si continuar con el siguiente batch.
"""
from ..graph.state import EstadoCodificacion


def decidir_continuar(state: EstadoCodificacion) -> str:
    """
    Decide si continuar procesando más batches o finalizar.
    
    Args:
        state: Estado actual del grafo
        
    Returns:
        "preparar_batch" si hay más respuestas, "finalizar" si no
    """
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

