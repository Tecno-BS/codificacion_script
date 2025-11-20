"""
Tests para schemas Pydantic del GPT
"""
import pytest
from cod_backend.schemas import (
    RespuestaInput,
    Catalogo,
    CodigoHistorico,
    ResultadoCodificacion,
)


def test_respuesta_input():
    """Test creación de RespuestaInput"""
    resp = RespuestaInput(
        id="1",
        texto="Enfermería",
        pregunta="FC1"
    )
    assert resp.id == "1"
    assert resp.texto == "Enfermería"
    assert resp.pregunta == "FC1"


def test_codigo_historico():
    """Test creación de CodigoHistorico"""
    cod = CodigoHistorico(
        codigo="5",
        descripcion="Enfermería"
    )
    assert cod.codigo == "5"
    assert cod.descripcion == "Enfermería"


def test_catalogo_empty():
    """Test catálogo vacío"""
    cat = Catalogo(pregunta="FC1", codigos=[])
    assert cat.pregunta == "FC1"
    assert len(cat.codigos) == 0


def test_catalogo_with_codes():
    """Test catálogo con códigos"""
    codigos = [
        CodigoHistorico(codigo="5", descripcion="Enfermería"),
        CodigoHistorico(codigo="10", descripcion="Medicina"),
    ]
    cat = Catalogo(pregunta="FC1", codigos=codigos)
    assert len(cat.codigos) == 2
    assert cat.codigos[0].codigo == "5"


def test_resultado_codificacion_asignar():
    """Test resultado con decisión asignar"""
    result = ResultadoCodificacion(
        respuesta_id="1",
        decision="asignar",
        codigos_historicos=["5", "10"],
        codigo_nuevo=None,
        descripcion_nueva=None,
        idea_principal=None,
        confianza=0.95,
        justificacion="Respuesta clara"
    )
    assert result.decision == "asignar"
    assert len(result.codigos_historicos) == 2
    assert result.codigo_nuevo is None


def test_resultado_codificacion_nuevo():
    """Test resultado con decisión nuevo"""
    result = ResultadoCodificacion(
        respuesta_id="1",
        decision="nuevo",
        codigos_historicos=[],
        codigo_nuevo="24",
        descripcion_nueva="Bioquímica",
        idea_principal="Ciencias químicas",
        confianza=0.88,
        justificacion="Tema emergente"
    )
    assert result.decision == "nuevo"
    assert result.codigo_nuevo == "24"
    assert result.descripcion_nueva == "Bioquímica"


def test_resultado_multicodificacion():
    """Test resultado con múltiples códigos nuevos"""
    result = ResultadoCodificacion(
        respuesta_id="1",
        decision="nuevo",
        codigos_historicos=[],
        codigo_nuevo=None,
        descripcion_nueva=None,
        idea_principal="Múltiples temas",
        confianza=0.90,
        justificacion="Respuesta con varios temas",
        codigos_nuevos=["24", "25"],
        descripciones_nuevas=["Bioquímica", "Química orgánica"]
    )
    assert len(result.codigos_nuevos) == 2
    assert len(result.descripciones_nuevas) == 2
    assert result.codigos_nuevos[0] == "24"


def test_resultado_post_init_migration():
    """Test que model_post_init migra campos singulares a listas"""
    result = ResultadoCodificacion(
        respuesta_id="1",
        decision="nuevo",
        codigos_historicos=[],
        codigo_nuevo="24",  # Singular
        descripcion_nueva="Bioquímica",  # Singular
        idea_principal="Tema",
        confianza=0.90,
        justificacion="Test"
    )
    # Debe migrar automáticamente a las listas
    assert len(result.codigos_nuevos) == 1
    assert result.codigos_nuevos[0] == "24"
    assert len(result.descripciones_nuevas) == 1
    assert result.descripciones_nuevas[0] == "Bioquímica"

