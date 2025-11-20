"""
Tests para utilidades generales
"""
import pytest
import pandas as pd
from cod_backend.utils import (
    fix_encoding_issues,
    clean_text_for_gpt,
    clean_text,
)


class TestFixEncodingIssues:
    """Tests para corrección de encoding"""

    def test_fix_encoding_basic(self):
        """Corrige problemas básicos de encoding"""
        assert fix_encoding_issues("naci?n") == "nación"
        assert fix_encoding_issues("opini?n") == "opinión"
        assert fix_encoding_issues("educaci?n") == "educación"

    def test_fix_encoding_preserves_questions(self):
        """Preserva signos de interrogación en preguntas"""
        assert fix_encoding_issues("¿Cómo estás?") == "¿Cómo estás?"
        assert fix_encoding_issues("Qué tal?") == "Qué tal?"

    def test_fix_encoding_handles_none(self):
        """Maneja valores None o NaN"""
        assert fix_encoding_issues(None) == ""
        assert fix_encoding_issues(pd.NA) == ""


class TestCleanTextForGPT:
    """Tests para limpieza mínima optimizada para GPT"""

    def test_preserves_case(self):
        """Preserva mayúsculas"""
        text = "Partido Político Nacional"
        assert clean_text_for_gpt(text) == text

    def test_preserves_punctuation(self):
        """Preserva puntuación"""
        text = "Hola, ¿cómo estás? ¡Bien!"
        assert "," in clean_text_for_gpt(text)
        assert "¿" in clean_text_for_gpt(text)

    def test_preserves_accents(self):
        """Preserva tildes"""
        text = "educación política democrática"
        result = clean_text_for_gpt(text)
        assert "educación" in result
        assert "política" in result

    def test_removes_extra_spaces(self):
        """Elimina espacios múltiples"""
        text = "texto   con    espacios"
        assert clean_text_for_gpt(text) == "texto con espacios"

    def test_fixes_encoding(self):
        """Corrige problemas de encoding"""
        text = "educaci?n p?blica"
        result = clean_text_for_gpt(text)
        assert "educación" in result
        assert "pública" in result

    def test_handles_empty(self):
        """Maneja valores vacíos"""
        assert clean_text_for_gpt("") == ""
        assert clean_text_for_gpt(None) == ""
        assert clean_text_for_gpt(pd.NA) == ""


class TestCleanTextLegacy:
    """Tests para limpieza agresiva (legacy)"""

    def test_converts_to_lowercase(self):
        """Convierte a minúsculas"""
        assert clean_text("TEXTO") == "texto"

    def test_preserves_accents_by_default(self):
        """Preserva tildes por defecto"""
        result = clean_text("educación")
        assert "educación" in result

    def test_removes_accents_when_requested(self):
        """Elimina tildes cuando se solicita"""
        result = clean_text("educación", preserve_accents=False)
        assert "educacion" in result

    def test_removes_special_chars(self):
        """Elimina caracteres especiales"""
        result = clean_text("texto@#$%con&*()caracteres")
        assert "@" not in result
        assert "#" not in result

    def test_normalizes_spaces(self):
        """Normaliza espacios (preserva tildes por defecto)"""
        assert clean_text("texto   múltiple   espacios") == "texto múltiple espacios"

