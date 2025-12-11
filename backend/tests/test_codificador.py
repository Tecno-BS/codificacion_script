"""
Tests para Codificador Híbrido V05
"""
import pytest
from cod_backend.core import CodificadorHibridoV05


def test_codificador_init():
    """Test inicialización del codificador"""
    codificador = CodificadorHibridoV05(modelo="gpt-4o-mini")
    assert codificador.gpt is not None
    assert codificador.catalogos == {}
    assert codificador.codigos_nuevos == []


def test_normalizar_nombre():
    """Test normalización de nombres"""
    codificador = CodificadorHibridoV05()
    
    assert codificador._normalizar_nombre("FC1") == "fc1"
    assert codificador._normalizar_nombre("P12A") == "p12a"
    assert codificador._normalizar_nombre("¿Pregunta?") == "pregunta"
    assert codificador._normalizar_nombre("Educación") == "educacion"


def test_extraer_codigo_pregunta():
    """Test extracción de códigos de preguntas"""
    codificador = CodificadorHibridoV05()
    
    # Con punto
    assert codificador._extraer_codigo_pregunta("FC1. ¿Cómo se llama...") == "FC1"
    assert codificador._extraer_codigo_pregunta("P12A. ¿Por qué...") == "P12A"
    assert codificador._extraer_codigo_pregunta("1a. Mencione...") == "P1A"
    assert codificador._extraer_codigo_pregunta("5AC. ¿Cuál...") == "P5AC"
    
    # Sin punto
    assert codificador._extraer_codigo_pregunta("FC1 ¿Cómo...") == "FC1"
    assert codificador._extraer_codigo_pregunta("PA3 Descripción...") == "PA3"
    
    # Sin código
    assert codificador._extraer_codigo_pregunta("¿Pregunta sin código?") is None


def test_es_columna_metadata():
    """Test detección de columnas metadata"""
    codificador = CodificadorHibridoV05()
    
    # Metadata
    assert codificador._es_columna_metadata("ID") is True
    assert codificador._es_columna_metadata("fecha") is True
    assert codificador._es_columna_metadata("usuario") is True
    assert codificador._es_columna_metadata("Unnamed: 0") is True
    
    # No metadata
    assert codificador._es_columna_metadata("FC1. ¿Cómo se llama...") is False
    assert codificador._es_columna_metadata("Pregunta completa") is False


def test_similitud_descripciones():
    """Test cálculo de similitud entre descripciones"""
    codificador = CodificadorHibridoV05()
    
    # Muy similares (contención)
    sim = codificador._similitud_descripciones("Versatilidad de uso", "Versatilidad de uso en comidas")
    assert sim >= 0.85
    
    # Similares (comparten palabra clave)
    sim = codificador._similitud_descripciones("Sabor agradable", "Buen sabor")
    assert sim > 0.2  # Comparten "sabor"
    
    # Diferentes
    sim = codificador._similitud_descripciones("Sabor", "Precio")
    assert sim == 0.0
    
    # Idénticas
    sim = codificador._similitud_descripciones("Enfermería", "Enfermería")
    assert sim >= 0.95
    
    # Muy similares con stop words
    sim = codificador._similitud_descripciones("Calidad del producto", "Calidad de producto")
    assert sim >= 0.8


@pytest.mark.skip(reason="Test de integración - requiere archivos de datos reales")
async def test_ejecutar_codificacion_completa():
    """
    Test de integración completo (skip por defecto)
    Requiere archivos de prueba reales
    """
    codificador = CodificadorHibridoV05(modelo="gpt-4o-mini")
    
    # Aquí irían rutas a archivos de prueba
    ruta_respuestas = "data/test_respuestas.xlsx"
    ruta_codigos = "data/test_codigos.xlsx"
    
    resultados = await codificador.ejecutar_codificacion(
        ruta_respuestas=ruta_respuestas,
        ruta_codigos=ruta_codigos
    )
    
    assert resultados is not None
    assert len(resultados) > 0

