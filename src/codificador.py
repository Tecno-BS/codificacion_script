import pandas as pd 
import numpy as np
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


import os
from pathlib import Path
from .config import * 
from .utils import *
from .embeddings import GenerateEmebeddings

class SemanticCoder:
    def __init__(self):
        self.generate_embeddings = GenerateEmebeddings(EMBEDDING_MODEL)
        self.history_codes = {}  # Diccionario: pregunta -> DataFrame
        self.codes_embeddings = {}  # Diccionario: pregunta -> embeddings
        self.respuestas_procesadas = None
        self.embeddings_respuestas = {}  # Diccionario: pregunta -> embeddings
        self.mapeo_columnas = {}  # Diccionario: columna -> pregunta
    
    def mapear_columnas_preguntas(self, df_respuestas: pd.DataFrame) -> Dict[str, str]:
        """
        Mapea columnas del archivo de respuestas con preguntas
        """
        mapeo = {}
        
        print(f"Columnas encontradas: {df_respuestas.columns.tolist()}")
        
        # Mapeo manual basado en las columnas reales del archivo
        for col in df_respuestas.columns:
            col_lower = col.lower()
            col_clean = col.strip()
            
            print(f"Analizando columna: '{col}'")
            
            # Mapeo específico para las columnas de tu archivo
            if 'qué funciones tiene la cámara de representantes' in col_lower:
                mapeo[col] = 'P1A'
                print(f"  -> Mapeada a P1A")
            elif 'qué funciones tiene la cámara de representantes y p2' in col_lower:
                mapeo[col] = 'P1C'
                print(f"  -> Mapeada a P1C")
            elif 'cámara de representantes y p2' in col_lower:
                mapeo[col] = 'P2A'
                print(f"  -> Mapeada a P2A")
            elif 'elecciones' in col_lower:
                mapeo[col] = 'P5AC'
                print(f"  -> Mapeada a P5AC")
            elif 'presentan' in col_lower:
                mapeo[col] = 'P8D'
                print(f"  -> Mapeada a P8D")
            elif 'cámara de representantes' in col_lower and 'p9' in col_lower:
                mapeo[col] = 'P9AA'
                print(f"  -> Mapeada a P9AA")
            elif 'presentado' in col_lower and 'p9' in col_lower:
                mapeo[col] = 'P9A1'
                print(f"  -> Mapeada a P9A1")
            elif 'presentado por' in col_lower:
                mapeo[col] = 'P9B'
                print(f"  -> Mapeada a P9B")
            elif 'p12' in col_lower and 'p12' in col_lower:
                mapeo[col] = 'P12A'
                print(f"  -> Mapeada a P12A")
            elif 'cuáles páginas web' in col_lower or 'páginas web' in col_lower:
                mapeo[col] = 'P13A'
                print(f"  -> Mapeada a P13A")
            else:
                print(f"  -> No mapeada")
        
        print(f"Mapeo final: {mapeo}")
        return mapeo

    def load_history_codes(self, ruta: str) -> bool:
        """
        Carga códigos históricos de todas las hojas
        """
        try:
            # Cargar todas las hojas del archivo Excel
            excel_file = pd.ExcelFile(ruta)
            hojas_disponibles = excel_file.sheet_names
            
            print(f"Hojas disponibles en códigos: {hojas_disponibles}")
            
            for hoja in hojas_disponibles:
                try:
                    # Cargar hoja
                    df_hoja = pd.read_excel(ruta, sheet_name=hoja)
                    
                    # Verificar que tenga las columnas necesarias
                    if 'COD' in df_hoja.columns and 'TEXTO' in df_hoja.columns:
                        # Renombrar columnas para consistencia
                        df_hoja = df_hoja.rename(columns={'COD': 'codigo', 'TEXTO': 'descripcion'})
                        
                        # Filtrar filas válidas
                        df_hoja = df_hoja.dropna(subset=['codigo', 'descripcion'])
                        
                        if len(df_hoja) > 0:
                            self.history_codes[hoja] = df_hoja
                            print(f"Cargados {len(df_hoja)} códigos para {hoja}")
                        else:
                            print(f"Hoja {hoja} está vacía")
                    else:
                        print(f"Hoja {hoja} no tiene columnas COD y TEXTO")
                        
                except Exception as e:
                    print(f"Error al cargar hoja {hoja}: {e}")
                    continue
            
            if not self.history_codes:
                print("No se pudieron cargar códigos históricos")
                return False
            
            # Generar embeddings para cada pregunta
            for pregunta, df_codigos in self.history_codes.items():
                descriptions = df_codigos['descripcion'].tolist()
                self.codes_embeddings[pregunta] = self.generate_embeddings.generate_embeddings(descriptions)
                print(f"Embeddings generados para {pregunta}")
            
            print(f"Total de preguntas con códigos: {len(self.history_codes)}")
            return True
            
        except Exception as e:
            print(f"Error al cargar códigos históricos: {e}")
            return False
    
    def codificar_todas_preguntas(self) -> pd.DataFrame:
        """
        Codifica respuestas de todas las preguntas
        """
        if not self.history_codes or len(self.history_codes) == 0 or not self.codes_embeddings or len(self.codes_embeddings) == 0:
            raise ValueError("Debe cargar códigos anteriores primero")
        
        if self.respuestas_procesadas is None or not self.embeddings_respuestas or len(self.embeddings_respuestas) == 0:
            raise ValueError("Debe procesar respuestas primero")
        
        resultados = self.respuestas_procesadas.copy()
        
        print("=== INICIANDO CODIFICACIÓN DE TODAS LAS PREGUNTAS ===")
        
        for columna, pregunta in self.mapeo_columnas.items():
            print(f"\n--- Procesando {pregunta} ---")
            
            if pregunta not in self.history_codes:
                print(f"No hay códigos para {pregunta}, saltando...")
                continue
            
            if pregunta not in self.embeddings_respuestas:
                print(f"No hay embeddings para {pregunta}, saltando...")
                continue
            
            # Crear columnas para esta pregunta
            resultados[f'{pregunta}_codigo'] = None
            resultados[f'{pregunta}_similitud'] = 0.0
            resultados[f'{pregunta}_candidatos'] = None
            
            # Obtener datos de esta pregunta
            df_codigos = self.history_codes[pregunta]
            embeddings_codigos = self.codes_embeddings[pregunta]
            embeddings_respuestas = self.embeddings_respuestas[pregunta]
            
            # Codificar cada respuesta
            respuestas_validas = resultados[resultados[f'{columna}_limpio'].str.len() > 0]
            
            for idx, row in respuestas_validas.iterrows():
                # Obtener índice del embedding
                idx_embedding = respuestas_validas.index.get_loc(idx)
                embedding_respuesta = embeddings_respuestas[idx_embedding]
                
                # Encontrar códigos similares
                candidatos = self.generate_embeddings.find_similaritys(
                    embedding_respuesta,
                    embeddings_codigos,
                    top_k=TOP_CANDIDATOS
                )

                # Guardar candidatos
                resultados.at[idx, f'{pregunta}_candidatos'] = str(candidatos)

                # Verificar si hay candidatos (cambiar esta línea)
                if len(candidatos) > 0:  # ← SOLUCIÓN: usar len() en lugar de comparación directa
                    mejor_candidato = candidatos[0]
                    codigo_idx, similitud = mejor_candidato
                    
                    # Asignar código si supera umbral
                    if similitud >= UMBRAL_SIMILITUD:
                        codigo = df_codigos.iloc[codigo_idx]['codigo']
                        resultados.at[idx, f'{pregunta}_codigo'] = codigo
                        resultados.at[idx, f'{pregunta}_similitud'] = similitud
                    else:
                        # Marcar para revisión manual
                        resultados.at[idx, f'{pregunta}_codigo'] = 'REVISAR'
                        resultados.at[idx, f'{pregunta}_similitud'] = similitud
            
            print(f"Codificación completada para {pregunta}")
        
        print("\n=== CODIFICACIÓN COMPLETADA ===")
        return resultados

    def process_responses(self, ruta_respuestas: str) -> bool:
        """
        Procesa respuestas de todas las columnas
        """
        try:
            # Cargar respuestas
            respuestas_raw = load_data(ruta_respuestas)
            print(f"Cargados {len(respuestas_raw)} respuestas")
            
            # Mapear columnas con preguntas
            self.mapeo_columnas = self.mapear_columnas_preguntas(respuestas_raw)
            print(f"Mapeo de columnas: {self.mapeo_columnas}")
            
            if not self.mapeo_columnas:
                print("No se pudieron mapear columnas con preguntas")
                return False
            
            # Procesar cada columna
            respuestas_procesadas = respuestas_raw.copy()
            
            for columna, pregunta in self.mapeo_columnas.items():
                print(f"Procesando columna {columna} -> {pregunta}")
                
                # Limpiar textos de esta columna
                respuestas_procesadas[f'{columna}_limpio'] = respuestas_procesadas[columna].fillna('').apply(clean_text)
                
                # Filtrar respuestas válidas
                respuestas_validas = respuestas_procesadas[respuestas_procesadas[f'{columna}_limpio'].str.len() > 0]
                
                if len(respuestas_validas) > 0:
                    # Generar embeddings
                    texto_limpios = respuestas_validas[f'{columna}_limpio'].tolist()
                    self.embeddings_respuestas[pregunta] = self.generate_embeddings.generate_embeddings(texto_limpios)
                    print(f"Embeddings generados para {pregunta}: {len(texto_limpios)} respuestas")
                else:
                    print(f"No hay respuestas válidas para {pregunta}")
            
            # Guardar respuestas procesadas
            self.respuestas_procesadas = respuestas_procesadas
            
            print("Todas las respuestas procesadas")
            return True
            
        except Exception as e:
            print(f"Error al procesar respuestas: {e}")
            return False
    
    def codificar_sin_historicos(self) -> pd.DataFrame:
        """
        Codifica respuestas sin códigos históricos (solo embeddings)
        """
        if not self.respuestas_procesadas or not self.embeddings_respuestas:
            raise ValueError("Debe procesar respuestas primero")
        
        resultados = self.respuestas_procesadas.copy()
        resultados['embedding_generado'] = True
        resultados['preparado_para_gpt'] = True
        
        print("Respuestas preparadas para codificación con GPT")
        return resultados

    def ejecutar_codificacion(self, ruta_respuestas: str, ruta_codigos: Optional[str] = None) -> pd.DataFrame:
        """
        Ejecuta el proceso completo de codificación para todas las preguntas
        """
        print("=== INICIANDO PROCESO DE CODIFICACIÓN MULTIPREGUNTA ===")
        
        # Procesar respuestas
        if not self.process_responses(ruta_respuestas):
            raise Exception("Error al procesar respuestas")
        
        # Verificar si hay códigos históricos
        if ruta_codigos and verify_codes(ruta_codigos):
            print("Códigos anteriores encontrados - Usando codificación híbrida")
            if self.load_history_codes(ruta_codigos):
                return self.codificar_todas_preguntas()
            else:
                print("Error al cargar códigos - Continuando sin códigos anteriores")
        
        print("Sin códigos anteriores - Preparando para GPT")
        return self.codificar_sin_historicos()

    def guardar_resultados(self, resultados: pd.DataFrame, ruta: str) -> None:
        save_data(resultados, ruta)
        print(f"Resultados guardados en {ruta}")

        




