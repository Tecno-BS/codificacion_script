"""
Utilidades generales - Sistema de Codificación Automatizada
"""
import pandas as pd
import numpy as np
import re
import unicodedata
import os
from pathlib import Path
from typing import List, Dict, Any, Optional


def fix_encoding_issues(text: str) -> str:
    """
    Corrige problemas de encoding comunes donde tildes aparecen como '?'
    Utiliza patrones contextuales comunes en español para determinar la corrección
    """
    if not isinstance(text, str) or pd.isna(text):
        return ""

    # NO aplicar correcciones si el texto es una pregunta (? al final)
    if text.strip().endswith('?'):
        return text

    # Si comienza con ¿, solo corregir después del inicio
    if text.startswith('¿'):
        return text

    # Patrones contextuales comunes en español (más específicos primero)
    # Formato: (patrón, reemplazo)
    context_patterns = [
        # Terminaciones comunes
        ('ci?n', 'ción'),  # nación, función, representación
        ('si?n', 'sión'),  # decisión
        ('ni?n', 'nión'),  # opinión
        ('ti?n', 'tión'),  # gestión
        ('ri?n', 'rión'),  #
        ('aci?n', 'ación'),  # representación
        ('ici?n', 'ición'),  #
        ('uci?n', 'ución'),  #
        # Vocal + ?n al final
        ('a?n', 'án'),
        ('e?n', 'én'),
        ('i?n', 'ín'),
        ('o?n', 'ón'),
        ('u?n', 'ún'),
        # ? solo (probablemente reemplaza una vocal con tilde)
        # Contextos específicos
        ('?blica', 'ública'),  # pública
        ('?blico', 'úblico'),  # público
        ('p?blica', 'pública'),
        ('p?blico', 'público'),
        ('c?mara', 'cámara'),
        ('?mara', 'ámara'),  # cámara
        ('pol?tica', 'política'),
        ('democr?tico', 'democrático'),
        ('?tico', 'ático'),  # democrático
        ('?tica', 'ática'),  # política
        # Ñ mal codificada
        ('a?o', 'año'),
        ('n?o', 'ño'),
        ('n?a', 'ña'),
        # Patrones generales (aplicar al final)
        ('a?', 'á'),
        ('e?', 'é'),
        ('i?', 'í'),
        ('o?', 'ó'),
        ('u?', 'ú'),
        ('A?', 'Á'),
        ('E?', 'É'),
        ('I?', 'Í'),
        ('O?', 'Ó'),
        ('U?', 'Ú'),
    ]

    # Aplicar reemplazos en orden (específicos primero)
    for pattern, replacement in context_patterns:
        text = text.replace(pattern, replacement)

    return text


def clean_text_for_gpt(text: str) -> str:
    """
    Limpieza MÍNIMA optimizada para GPT (v0.5)

    Preserva el máximo contexto para que GPT entienda mejor:
    - Mantiene mayúsculas (énfasis, nombres propios)
    - Mantiene puntuación (contexto emocional, sentido)
    - Mantiene tildes (significado en español)

    Solo corrige:
    - Problemas de encoding (? -> tildes)
    - Espacios múltiples
    - Caracteres de control/no imprimibles

    Args:
        text: Texto a limpiar

    Returns:
        Texto con limpieza mínima
    """
    if not isinstance(text, str) or pd.isna(text):
        return ""

    # 1. Corregir problemas de encoding (CRÍTICO)
    text = fix_encoding_issues(text)

    # 2. Eliminar caracteres de control y no imprimibles
    # Preserva: letras, números, espacios, puntuación común, tildes
    text = ''.join(char for char in text if char.isprintable() or char.isspace())

    # 3. Normalizar espacios múltiples (ahorra tokens)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    # NO convertir a minúsculas
    # NO eliminar puntuación
    # NO eliminar caracteres especiales relevantes

    return text


def clean_text(text: str, preserve_accents: bool = True) -> str:
    """
    Limpieza AGRESIVA (legacy - para compatibilidad con v2.1)

    NOTA: Para v0.5 se recomienda usar clean_text_for_gpt()

    Args:
        text: Texto a limpiar
        preserve_accents: Si True, preserva tildes y caracteres acentuados
    """
    if not isinstance(text, str) or pd.isna(text):
        return ""

    # Primero corregir problemas de encoding
    text = fix_encoding_issues(text)

    # Convertir a minúsculas
    text = text.lower()

    # Manejar tildes según configuración
    if not preserve_accents:
        # Solo eliminar tildes si explícitamente se solicita
        text = unicodedata.normalize('NFD', text)
        text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')

    # Preservar letras con tildes, ñ y caracteres alfanuméricos
    if preserve_accents:
        # Permitir: letras (incluidas á,é,í,ó,ú,ñ), números y espacios
        text = re.sub(r'[^a-záéíóúñü0-9\s]', ' ', text)
    else:
        # Solo letras sin tildes, números y espacios
        text = re.sub(r'[^a-z0-9\s]', ' ', text)

    # Normalizar espacios múltiples
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    return text


def load_data(ruta: str) -> pd.DataFrame:
    """
    Carga datos desde archivo Excel o CSV

    Args:
        ruta: Ruta al archivo

    Returns:
        DataFrame con los datos

    Raises:
        FileNotFoundError: Si el archivo no existe
        ValueError: Si el formato no es soportado
    """
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"Archivo no encontrado {ruta}")

    extension = Path(ruta).suffix.lower()

    try:
        if extension in ['.xlsx', '.xls']:
            return pd.read_excel(ruta)
        elif extension == '.csv':
            return pd.read_csv(ruta)
        else:
            raise ValueError(f"Formato no soportado: {extension}")
    except Exception as e:
        raise Exception(f"Error al cargar el archivo {ruta}: {e}")


def save_data(data: pd.DataFrame, ruta: str) -> bool:
    """
    Guarda resultados en archivo Excel

    Args:
        data: DataFrame a guardar
        ruta: Ruta de destino

    Returns:
        True si se guardó exitosamente

    Raises:
        Exception: Si hay un error al guardar
    """
    try:
        print(f"Iniciando guardado en {ruta}")
        print(f"Datos: {len(data)} filas, {len(data.columns)} columnas")

        # Verificar que el DataFrame no esté vacío
        if data is None or len(data) == 0:
            print("Advertencia: DataFrame vacío")
            return False

        # Crear directorio si no existe
        os.makedirs(os.path.dirname(ruta), exist_ok=True)

        # Limpiar datos problemáticos antes de guardar
        data_clean = data.copy()

        # Normalizar nombres de columnas a string
        data_clean.columns = data_clean.columns.map(str)

        # Aviso si hay columnas duplicadas (puede afectar accesos por etiqueta)
        try:
            if data_clean.columns.duplicated().any():
                print("Advertencia: hay nombres de columnas duplicados en el DataFrame a exportar")
        except Exception:
            pass

        # Convertir todas las columnas 'object' a string, accediendo por índice y saneando celdas no escalares
        for i in range(data_clean.shape[1]):
            serie = data_clean.iloc[:, i]
            if serie.dtype == 'object':

                def _to_safe_str(v):
                    if v is None or (isinstance(v, float) and pd.isna(v)):
                        return ''
                    # Si ya es escalar aceptable, devuélvelo tal cual (se maneja por to_excel)
                    if isinstance(v, (str, bool, int, float, np.integer, np.floating, np.bool_)):
                        return v
                    # Evitar objetos complejos (DataFrame/Series/list/dict/etc.)
                    try:
                        return str(v)
                    except Exception:
                        return ''

                data_clean.iloc[:, i] = serie.map(_to_safe_str)

        # Guardar archivo
        data_clean.to_excel(ruta, index=False, engine='openpyxl')
        print(f"Resultados guardados exitosamente en {ruta}")
        return True

    except Exception as e:
        print(f"Error detallado al guardar archivo {ruta}: {e}")
        print(f"Tipo de error: {type(e)}")
        print(f"Columnas del DataFrame: {list(data.columns) if data is not None else 'None'}")
        if data is not None and len(data) > 0:
            print(f"Primeras 3 filas:\n{data.head(3)}")
        raise Exception(f"Error al guardar archivo {ruta}: {e}")


def verify_codes(ruta_codes: str) -> bool:
    """
    Verifica si existen códigos anteriores válidos

    Args:
        ruta_codes: Ruta al archivo de códigos

    Returns:
        True si el archivo existe y tiene el formato correcto
    """
    if not os.path.exists(ruta_codes):
        return False

    try:
        df = load_data(ruta_codes)

        if df.empty:
            return False

        columnas_requeridas = ['COD', 'TEXTO']

        if not all(col in df.columns for col in columnas_requeridas):
            return False

        return True
    except Exception:
        return False

