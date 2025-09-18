import pandas as pd
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
    os.makedirs(os.path.dirname(ruta), exist_ok=True)

    try:
        data.to_excel(ruta, index=False)
        print(f"Resultados guardados en {ruta}")
    except Exception as e:
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
