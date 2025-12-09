"""
Nodo del grafo: Validar respuestas.
"""
from typing import Dict, Any, List
from ...graph.state import EstadoCodificacion
from ...models.validacion import ResultadoValidacion
from ...utils import detectar_codigo_especial
from ..prompts import load_prompt
from ..services import LLMService


def nodo_validar(state: EstadoCodificacion) -> EstadoCodificacion:
    """
    Valida si las respuestas son válidas para codificar.
    
    Args:
        state: Estado actual del grafo
        
    Returns:
        Estado actualizado con validaciones del batch
    """
    print("\n✅ Validando respuestas...")
    prompt_template = load_prompt("validar")

    respuestas = []
    respuestas_especiales: Dict[int, int] = {}
    respuestas_rechazadas_automatico: Dict[int, bool] = {}

    for i, resp in enumerate(state["batch_respuestas"]):
        resp_id = i + 1
        texto = resp["texto"]
        
        # Rechazar automáticamente respuestas vacías o solo con "-"
        texto_limpio = str(texto).strip() if texto else ""
        if not texto_limpio or texto_limpio == "-" or texto_limpio == "---" or texto_limpio.replace("-", "").replace(" ", "") == "":
            respuestas_rechazadas_automatico[resp_id] = True
            continue  # No incluir en la lista para el LLM
        
        codigo_esp = detectar_codigo_especial(texto)
        if codigo_esp is not None:
            respuestas_especiales[resp_id] = codigo_esp
        respuestas.append(f"{resp_id}. {texto}")

    # Usar servicio LLM
    llm_service = LLMService(state["modelo_gpt"])
    respuesta_llm = llm_service.invoke_with_system(
        system_template=prompt_template,
        user_template="PREGUNTA:\n{pregunta}\n\nRESPUESTAS:\n{respuestas}",
        variables={
            "pregunta": state["pregunta"],
            "respuestas": "\n".join(respuestas),
        }
    )

    prompt_tokens, completion_tokens, _total = llm_service.extract_tokens(respuesta_llm)

    # Parsear a modelo estructurado
    try:
        resultado = ResultadoValidacion.model_validate_json(respuesta_llm.content)
    except Exception as e:
        raise RuntimeError(f"Error al parsear la salida de validación: {e}\nContenido: {respuesta_llm.content}")

    validaciones: List[Dict[str, Any]] = []
    idx_llm = 0
    for i, _resp in enumerate(state["batch_respuestas"]):
        rid = i + 1
        # Rechazar automáticamente respuestas vacías o solo con "-"
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

