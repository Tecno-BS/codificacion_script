"""
Tests para el módulo de configuración
"""
import pytest
from cod_backend import config


def test_config_constants_exist():
    """Verificar que las constantes principales existen"""
    assert hasattr(config, 'OPENAI_MODEL')
    assert hasattr(config, 'GPT_TEMPERATURE')
    assert hasattr(config, 'GPT_MAX_TOKENS')
    assert hasattr(config, 'UMBRAL_SIMILITUD')
    assert hasattr(config, 'EMBEDDING_MODEL')


def test_config_values_types():
    """Verificar tipos de datos de configuraciones"""
    assert isinstance(config.GPT_TEMPERATURE, (int, float))
    assert isinstance(config.GPT_MAX_TOKENS, int)
    assert isinstance(config.UMBRAL_SIMILITUD, float)
    assert isinstance(config.HABILITAR_MULTICODIGO, bool)
    assert isinstance(config.USE_GPT_MOCK, bool)


def test_config_default_values():
    """Verificar valores por defecto razonables"""
    assert 0 <= config.GPT_TEMPERATURE <= 2
    assert config.GPT_MAX_TOKENS > 0
    assert 0 <= config.UMBRAL_SIMILITUD <= 1
    assert config.GPT_BATCH_SIZE > 0


def test_config_paths_exist():
    """Verificar que las rutas de configuración existen"""
    assert hasattr(config, 'PROJECT_ROOT')
    assert hasattr(config, 'RUTA_DATOS_RAW')
    assert hasattr(config, 'RUTA_DATA_PROCESSED')
    assert hasattr(config, 'RUTA_RESULTADOS')


def test_mock_mode():
    """Verificar que el modo MOCK está configurado correctamente"""
    # El valor depende del .env.backend, verificamos que existe la config
    assert isinstance(config.USE_GPT_MOCK, bool)
    print(f"[TEST] Modo MOCK: {config.USE_GPT_MOCK}")

