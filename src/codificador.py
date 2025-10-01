import pandas as pd 
import numpy as np
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

#GPT
import asyncio
from sklearn.metrics.pairwise import cosine_similarity


import os
from pathlib import Path
from config import * 
from utils import *
from embeddings import GenerateEmebeddings

if USE_GPT_MOCK:
    from gpt_agent_mock import GptCodificadorMock as GptCodificador, ItemGPT, ResultadoGPT
    print("🤖 Usando GPT Mock para desarrollo")
else:
    from gpt_agent import GptCodificador, ItemGPT, ResultadoGPT
    print("⚠️ Usando GPT Real (consumirá créditos)")


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
            # Usar contexto para cerrar el archivo en Windows (evita WinError 32)
            with pd.ExcelFile(ruta) as excel_file:
                hojas_disponibles = excel_file.sheet_names
                print(f"Hojas disponibles en códigos: {hojas_disponibles}")
                
                for hoja in hojas_disponibles:
                    try:
                        # Cargar hoja desde el manejador abierto
                        df_hoja = pd.read_excel(excel_file, sheet_name=hoja)
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
        Codifica respuestas de todas las preguntas con multicodificación y auxiliares
        """
        if (self.history_codes is None or len(self.history_codes) == 0 or
            self.codes_embeddings is None or len(self.codes_embeddings) == 0):
            raise ValueError("Debe cargar códigos anteriores primero")
        
        if (self.respuestas_procesadas is None or
            self.embeddings_respuestas is None or len(self.embeddings_respuestas) == 0):
            raise ValueError("Debe procesar respuestas primero")
        
        resultados = self.respuestas_procesadas.copy()
        
        print("=== INICIANDO CODIFICACIÓN DE TODAS LAS PREGUNTAS ===")
        
        # Inicializar agente GPT
        gpt_agente = GptCodificador()
        contexto_proyecto = {
            "objetivo": "Codificación de respuestas abiertas",
            "target": "Encuestados"
        }
        
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
            resultados[f'{pregunta}_origen'] = None
            
            # Obtener datos de esta pregunta
            df_codigos = self.history_codes[pregunta].copy()
            embeddings_codigos = self.codes_embeddings[pregunta]
            
            # Codificar cada respuesta
            respuestas_validas = resultados[resultados[f'{columna}_limpio'].str.len() > 0]
            
            # Recolectar items para GPT
            items_gpt = []
            
            for idx, row in respuestas_validas.iterrows():
                # Obtener índice del embedding
                idx_embedding = respuestas_validas.index.get_loc(idx)
                embedding_respuesta = self.embeddings_respuestas[pregunta][idx_embedding]
                
                # Filtrar por auxiliar si corresponde
                df_codigos_filtrado = df_codigos
                embeddings_filtrados = embeddings_codigos
                auxiliar_detectado = None
                
                if pregunta in AUXILIARES_POR_PREGUNTA:
                    col_aux = AUXILIARES_POR_PREGUNTA[pregunta]["col_aux"]
                    if f"{col_aux}_limpio" in resultados.columns:
                        aux_val = str(resultados.at[idx, f"{col_aux}_limpio"]).strip()
                        if aux_val:
                            aux_norm = AUXILIARES_CANONICOS.get(aux_val.lower(), aux_val.lower())
                            auxiliar_detectado = aux_norm
                            
                            if "auxiliar" in df_codigos.columns:
                                mask = df_codigos["auxiliar"].fillna("").str.lower().eq(aux_norm)
                                if mask.any():
                                    df_codigos_filtrado = df_codigos[mask].reset_index(drop=True)
                                    if not df_codigos_filtrado.empty:
                                        embeddings_filtrados = self.generate_embeddings.generate_embeddings(df_codigos_filtrado["descripcion"].tolist())
                                    else:
                                        # Si no hay códigos que coincidan con el auxiliar, usar todos
                                        df_codigos_filtrado = df_codigos
                                        embeddings_filtrados = embeddings_codigos
                
                # Validar que embeddings_filtrados no esté vacío
                if len(embeddings_filtrados) == 0:
                    print(f"Advertencia: No hay embeddings para {pregunta}, saltando respuesta {idx}")
                    resultados.at[idx, f"{pregunta}_codigo"] = "SIN_EMBEDDINGS"
                    resultados.at[idx, f"{pregunta}_similitud"] = 0.0
                    continue
                
                # Calcular similitudes
                sims = cosine_similarity(
                    embedding_respuesta.reshape(1, -1),
                    embeddings_filtrados
                )[0]
                
                # 1) Candidatos "sólidos" para multicodificación
                indices_solidos = np.where(sims >= UMBRAL_MULTICODIGO)[0]
                indices_orden = indices_solidos[np.argsort(sims[indices_solidos])[::-1]]
                
                codigos_asignados = []
                similitudes_asignadas = []
                
                for j in indices_orden[:MAX_CODIGOS]:
                    codigo = str(df_codigos_filtrado.iloc[j]["codigo"])
                    codigos_asignados.append(codigo)
                    similitudes_asignadas.append(float(sims[j]))
                
                if codigos_asignados:
                    # Asignación automática múltiple
                    resultados.at[idx, f"{pregunta}_codigo"] = SEPARADOR_CODIGOS.join(codigos_asignados)
                    resultados.at[idx, f"{pregunta}_similitud"] = max(similitudes_asignadas)
                    resultados.at[idx, f"{pregunta}_candidatos"] = str([(cod, sim) for cod, sim in zip(codigos_asignados, similitudes_asignadas)])
                    resultados.at[idx, f"{pregunta}_origen"] = "CATALOGO"
                else:
                    # 2) Fallback: un solo código si supera umbral normal
                    j = int(np.argmax(sims))
                    mejor_sim = float(sims[j])
                    
                    if mejor_sim >= UMBRAL_SIMILITUD:
                        resultados.at[idx, f"{pregunta}_codigo"] = str(df_codigos_filtrado.iloc[j]["codigo"])
                        resultados.at[idx, f"{pregunta}_similitud"] = mejor_sim
                        resultados.at[idx, f"{pregunta}_candidatos"] = str([(str(df_codigos_filtrado.iloc[j]["codigo"]), mejor_sim)])
                        resultados.at[idx, f"{pregunta}_origen"] = "CATALOGO"
                    else:
                        # 3) Marcar para GPT
                        resultados.at[idx, f"{pregunta}_codigo"] = "REVISAR"
                        resultados.at[idx, f"{pregunta}_similitud"] = mejor_sim
                        
                        # Preparar candidatos para GPT
                        top_k_indices = np.argsort(sims)[::-1][:GPT_TOP_K]
                        candidatos_gpt = []
                        for k in top_k_indices:
                            candidatos_gpt.append({
                                "codigo": str(df_codigos_filtrado.iloc[k]["codigo"]),
                                "descripcion": str(df_codigos_filtrado.iloc[k]["descripcion"]),
                                "similitud": float(sims[k])
                            })
                        
                        items_gpt.append(ItemGPT(
                            id_respuesta=str(idx),
                            pregunta=pregunta,
                            texto=row[f'{columna}_limpio'],
                            candidatos=candidatos_gpt,
                            auxiliar=auxiliar_detectado
                        ))
            
            # Procesar items con GPT
            if items_gpt:
                print(f"Enviando {len(items_gpt)} respuestas a GPT...")
                resultados_gpt = asyncio.run(gpt_agente.codificar_lote(items_gpt, contexto_proyecto))
                
                # Aplicar resultados de GPT
                for resultado in resultados_gpt:
                    idx = int(resultado.id_respuesta)
                    decision = resultado.raw.get("decision", "rechazar")
                    
                    if decision == "asignar":
                        codigos = resultado.raw.get("codigos_asignados", [])
                        if codigos:
                            resultados.at[idx, f"{pregunta}_codigo"] = SEPARADOR_CODIGOS.join(codigos)
                            resultados.at[idx, f"{pregunta}_similitud"] = 1.0  # Marcador de GPT
                            resultados.at[idx, f"{pregunta}_origen"] = "GPT"
                    elif decision == "nuevo":
                        propuesta = resultado.raw.get("propuesta_codigo_nuevo", {})
                        if propuesta:
                            nuevo_codigo = f"NUEVO_{propuesta.get('codigo_sugerido', 'UNKNOWN')}"
                            resultados.at[idx, f"{pregunta}_codigo"] = nuevo_codigo
                            resultados.at[idx, f"{pregunta}_similitud"] = 1.0
                            resultados.at[idx, f"{pregunta}_origen"] = "GPT"
                            
                            # Guardar propuesta para revisión
                            self._guardar_propuesta_nueva(pregunta, propuesta)
            
            print(f"Codificación completada para {pregunta}")
            if items_gpt:
                print(f"Costo GPT estimado: ${gpt_agente.costo_total:.4f}")
        
        print("\n=== CODIFICACIÓN COMPLETADA ===")
        gpt_agente.guardar_cache()
        return self.filtrar_columnas_para_exportar(resultados)

    def _guardar_propuesta_nueva(self, pregunta: str, propuesta: Dict[str, str]):
        """Guarda propuesta de nuevo código para revisión"""
        try:
            ruta_propuestas = "result/modelos/catalogo_propuestos.xlsx"
            os.makedirs(os.path.dirname(ruta_propuestas), exist_ok=True)
            
            nueva_propuesta = {
                "pregunta": pregunta,
                "codigo_propuesto": propuesta.get("codigo_sugerido", ""),
                "descripcion": propuesta.get("descripcion", ""),
                "fecha": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                "estado": "pendiente"
            }
            
            if os.path.exists(ruta_propuestas):
                df_existente = pd.read_excel(ruta_propuestas)
                df_nuevo = pd.concat([df_existente, pd.DataFrame([nueva_propuesta])], ignore_index=True)
            else:
                df_nuevo = pd.DataFrame([nueva_propuesta])
            
            df_nuevo.to_excel(ruta_propuestas, index=False)
            
        except Exception as e:
            print(f"Error al guardar propuesta: {e}")


    def filtrar_columnas_para_exportar(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            # Validar que el DataFrame no esté vacío
            if df is None or len(df) == 0:
                print("Advertencia: DataFrame vacío, retornando DataFrame vacío")
                return pd.DataFrame()
            
            # Columnas originales de preguntas (tal como vienen en el Excel)
            columnas_originales = list(self.mapeo_columnas.keys()) if self.mapeo_columnas else []

            # Sus versiones limpias
            columnas_limpias = [f"{col}_limpio" for col in columnas_originales if f"{col}_limpio" in df.columns]

            # Columnas de resultados por pregunta (solo código y origen)
            columnas_resultados = []
            for _, pregunta in self.mapeo_columnas.items():
                for suf in ["_codigo", "_origen"]:
                    col = f"{pregunta}{suf}"
                    if col in df.columns:
                        columnas_resultados.append(col)

            # "Todo lo demás": columnas que no sean originales ni marcadas como "_limpio" de otras cosas
            columnas_excluir = set(columnas_originales)
            columnas_incluir_otros = [c for c in df.columns if c not in columnas_excluir]

            # Orden sugerido: otros -> limpias -> resultados
            columnas_finales = []
            columnas_finales.extend([c for c in columnas_incluir_otros if c not in columnas_limpias + columnas_resultados])
            columnas_finales.extend(columnas_limpias)
            columnas_finales.extend(columnas_resultados)

            # Evita KeyError si algo faltara
            columnas_finales = [c for c in columnas_finales if c in df.columns]
            
            # Si no hay columnas finales, retornar el DataFrame original
            if not columnas_finales:
                print("Advertencia: No se encontraron columnas para exportar, retornando DataFrame original")
                return df

            # Normalizar nombres de columnas a string para evitar errores de selección
            df2 = df.copy()
            df2.columns = df2.columns.map(str)

            # Asegurar que todas las columnas finales existan y sean strings
            columnas_finales = [str(c) for c in columnas_finales if str(c) in df2.columns]

            print(f"Exportando {len(columnas_finales)} columnas: {columnas_finales[:5]}...")
            print(f"Columnas_finales (len={len(columnas_finales)}): {columnas_finales[:8]}...")

            # Selección robusta por etiquetas
            return df2.loc[:, columnas_finales]
            
        except Exception as e:
            print(f"Error al filtrar columnas: {e}")
            return df

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
                
                if pregunta in AUXILIARES_POR_PREGUNTA:
                    col_aux = AUXILIARES_POR_PREGUNTA[pregunta]["col_aux"]
                    if col_aux in respuestas_procesadas.columns:
                        respuestas_procesadas[f"{col_aux}_limpio"] = respuestas_procesadas[col_aux].fillna("").apply(clean_text)
                
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
        # Evitar evaluar DataFrame en contexto booleano (ambiguous truth value)
        if self.respuestas_procesadas is None or not self.embeddings_respuestas:
            raise ValueError("Debe procesar respuestas primero")
        
        resultados = self.respuestas_procesadas.copy()
        
        print("Respuestas preparadas para codificación con GPT")
        return self.filtrar_columnas_para_exportar(resultados)

    def ejecutar_codificacion(self, ruta_respuestas: str, ruta_codigos: Optional[str] = None) -> pd.DataFrame:
        """
        Ejecuta el proceso completo de codificación para todas las preguntas
        """
        print("=== INICIANDO PROCESO DE CODIFICACIÓN MULTIPREGUNTA ===")
        
        # Procesar respuestas
        if not self.process_responses(ruta_respuestas):
            raise Exception("Error al procesar respuestas")
        
        # Verificar si hay códigos históricos
        if (ruta_codigos is not None) and verify_codes(ruta_codigos):
            print("Códigos anteriores encontrados - Usando codificación híbrida")
            if self.load_history_codes(ruta_codigos):
                return self.codificar_todas_preguntas()
            else:
                print("Error al cargar códigos - Continuando sin códigos anteriores")

        print("Sin códigos anteriores - Preparando para GPT")
        return self.codificar_sin_historicos()

    def guardar_resultados(self, resultados: pd.DataFrame, ruta: str) -> None:
        try:
            # Normalizar nombres de columnas a string para evitar selecciones ambiguas
            df2 = resultados.copy()
            df2.columns = df2.columns.map(str)

            print(f"Guardando resultados: {len(df2)} filas, {len(df2.columns)} columnas")
            print(f"Tipos de columnas: {df2.dtypes.value_counts()}")
            
            # Verificar que no haya valores problemáticos y normalizar objetos a string
            # Nota: si hay columnas duplicadas, acceder por etiqueta devuelve DataFrame.
            # Recorremos por índice para obtener siempre Series.
            for i, col in enumerate(df2.columns):
                serie = df2.iloc[:, i]
                dtype = serie.dtype
                if dtype == 'object':
                    df2.iloc[:, i] = serie.astype(str)
            
            save_data(df2, ruta)
            print(f"Resultados guardados exitosamente en {ruta}")
            
        except Exception as e:
            print(f"Error al guardar resultados: {e}")
            print(f"Tipo de datos del DataFrame: {type(resultados)}")
            try:
                print(f"Dtypes: {resultados.dtypes}")
            except Exception:
                pass
            raise

        




