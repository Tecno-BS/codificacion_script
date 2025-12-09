"""
Utilidades para extracción y manejo de tokens de respuestas LLM.
"""
from typing import Any, Tuple


def extraer_tokens(response: Any) -> Tuple[int, int, int]:
    """
    Extrae (prompt_tokens, completion_tokens, total_tokens) desde response_metadata.
    
    Compatible con los formatos nuevos de OpenAI (input/output/total_tokens) 
    y antiguos (prompt_tokens/completion_tokens/total_tokens).
    
    Args:
        response: Respuesta del LLM (ChatOpenAI response)
        
    Returns:
        Tupla con (prompt_tokens, completion_tokens, total_tokens)
    """
    meta = getattr(response, "response_metadata", {}) or {}
    usage = meta.get("token_usage") or meta.get("usage") or {}

    prompt = (
        usage.get("prompt_tokens")
        or usage.get("input_tokens")
        or 0
    )
    completion = (
        usage.get("completion_tokens")
        or usage.get("output_tokens")
        or 0
    )
    total = (
        usage.get("total_tokens")
        or (prompt + completion)
    )
    return int(prompt or 0), int(completion or 0), int(total or 0)

