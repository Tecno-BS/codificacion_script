import pandas as pd
import numpy as np
import re 
import unicodedata 
import os
from pathlib import Path
from typing import List, Dict, Any, Optional


#Limpia el texto y normaliza para procesamiento
def clean_text(text: str) -> str:
    if not isinstance(text, str) or pd.isna(text):
        return ""
    
    text = text.lower()

    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')

    text = re.sub(r'[^a-z0-9\s]', ' ', text)

    text = re.sub(r'\s+',' ', text)
    text = text.strip()

    return text


#Carga datos desde archivo Excel o CSV 
def load_data(ruta: str) -> pd.DataFrame:
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"Archivo no encontrado { ruta }")
    
    extension = Path(ruta).suffix.lower()

    try:
        if extension == '.xlsx' or extension == '.xls':
            return pd.read_excel(ruta)
        elif extension == '.csv':
            return pd.read_csv(ruta)
        else:
            raise ValueError(f"Formato no soportado: {extension}")
    except Exception as e:
        raise Exception(f"Error al cargar el archivo {ruta}: {e}")


#Guarda resultados en archivo Excel
def save_data(data: pd.DataFrame, ruta: str) -> bool:
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

#Verifica si existen códigos anteriores
def verify_codes(ruta_codes: str) -> bool:
    if not os.path.exists(ruta_codes):
        return False

    try: 
        df = load_data(ruta_codes)

        if df.empty:
            return False
        
        columnas_requeridas = ['COD', 'TEXTO']
        
        if not all (col in df.columns for col in columnas_requeridas):
            return False

        return True
    except Exception:
        False
