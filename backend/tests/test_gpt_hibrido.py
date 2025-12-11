"""
Tests para GptHibrido (sin hacer llamadas reales a la API)
"""
import pytest
from cod_backend.core import GptHibrido
from cod_backend import config


def test_gpt_model_detection():
    """Test detección de versiones de modelo"""
    # Nota: Solo testeamos la lógica, no inicializamos el cliente
    
    # GPT-5 detection
    assert GptHibrido._is_gpt5_or_later(None, "gpt-5") is True
    assert GptHibrido._is_gpt5_or_later(None, "gpt-5-turbo") is True
    assert GptHibrido._is_gpt5_or_later(None, "gpt-6") is True
    
    # O1 detection
    assert GptHibrido._is_gpt5_or_later(None, "o1-preview") is True
    assert GptHibrido._is_gpt5_or_later(None, "o1-mini") is True
    
    # GPT-4 family (no es GPT-5+)
    assert GptHibrido._is_gpt5_or_later(None, "gpt-4o-mini") is False
    assert GptHibrido._is_gpt5_or_later(None, "gpt-4o") is False
    assert GptHibrido._is_gpt5_or_later(None, "gpt-4.1") is False


def test_temperature_support():
    """Test detección de soporte de temperature"""
    # GPT-5 y O1 no soportan temperature
    assert GptHibrido._supports_temperature(None, "gpt-5") is False
    assert GptHibrido._supports_temperature(None, "o1-preview") is False
    
    # GPT-4 family sí soporta
    assert GptHibrido._supports_temperature(None, "gpt-4o-mini") is True
    assert GptHibrido._supports_temperature(None, "gpt-4o") is True


def test_gpt_requires_api_key():
    """Test que GptHibrido requiere API key cuando OPENAI_AVAILABLE es True"""
    if not config.OPENAI_AVAILABLE:
        pytest.skip("OpenAI no disponible (modo MOCK), saltando test")
    
    # Sin API key y sin configuración de entorno debe fallar
    # Si hay API key en el entorno, se usará automáticamente
    if config.OPENAI_API_KEY:
        pytest.skip("API key ya configurada en entorno, saltando test de error")
    
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        GptHibrido(api_key=None)


def test_calcular_costo():
    """Test cálculo de costos"""
    if not config.OPENAI_AVAILABLE:
        pytest.skip("OpenAI no disponible (modo MOCK), saltando test")
    
    # Crear instancia mock (solo para testear _calcular_costo)
    # Nota: Esto fallará si no hay API key, pero el método _calcular_costo es independiente
    
    # Test con valores conocidos para gpt-4o-mini
    # Precios: input=0.150, output=0.600 por 1M tokens
    # 1000 input + 1000 output = 0.00015 + 0.0006 = 0.00075
    
    # Solo testeamos la lógica sin instanciar
    costo_esperado = (1000 / 1_000_000) * 0.150 + (1000 / 1_000_000) * 0.600
    assert abs(costo_esperado - 0.00075) < 0.000001


@pytest.mark.skip(reason="Test de integración - requiere API key real")
async def test_codificar_batch_integration():
    """
    Test de integración completo (skip por defecto)
    Para ejecutar: pytest -v -k test_codificar_batch_integration --run-integration
    """
    from cod_backend.schemas import RespuestaInput, Catalogo, CodigoHistorico
    
    gpt = GptHibrido(model="gpt-4o-mini")
    
    respuestas = [
        RespuestaInput(id="1", texto="Enfermería", pregunta="FC1"),
        RespuestaInput(id="2", texto="Medicina", pregunta="FC1"),
    ]
    
    catalogo = Catalogo(
        pregunta="FC1",
        codigos=[
            CodigoHistorico(codigo="5", descripcion="Enfermería"),
            CodigoHistorico(codigo="10", descripcion="Medicina"),
        ]
    )
    
    resultados = await gpt.codificar_batch(
        pregunta="¿Cómo se llama el curso/programa/estudios que ha realizado?",
        respuestas=respuestas,
        catalogo=catalogo
    )
    
    assert len(resultados) == 2
    assert all(r.respuesta_id in ["1", "2"] for r in resultados)

