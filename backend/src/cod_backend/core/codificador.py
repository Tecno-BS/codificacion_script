"""
Codificador Híbrido v0.5 - Migrado al Backend
Sistema simplificado sin embeddings que usa GPT directamente
"""

import pandas as pd
import asyncio
import os
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime

# Imports del backend
from ..utils import clean_text_for_gpt, load_data, save_data
from ..schemas import RespuestaInput, Catalogo, ResultadoCodificacion, CodigoHistorico
from .gpt_hibrido import GptHibrido


class CodificadorHibridoV05:
    """
    Codificador híbrido que orquesta el proceso completo de codificación
    """

    def __init__(self, modelo: str = "gpt-4o-mini"):
        self.gpt = GptHibrido(model=modelo)
        self.respuestas_procesadas = None
        self.mapeo_columnas = {}  # columna -> pregunta
        self.catalogos = {}  # pregunta -> Catalogo
        self.codigos_nuevos = []  # Lista de códigos nuevos generados

    def cargar_catalogos(self, ruta_codigos: str) -> bool:
        """
        Carga catálogos de códigos históricos por pregunta
        """
        try:
            with pd.ExcelFile(ruta_codigos) as excel_file:
                hojas_disponibles = excel_file.sheet_names
                print(f"[v0.5] Hojas de catálogo encontradas: {hojas_disponibles}")

                for hoja in hojas_disponibles:
                    try:
                        df_hoja = pd.read_excel(excel_file, sheet_name=hoja)

                        # Verificar columnas requeridas
                        if 'COD' in df_hoja.columns and 'TEXTO' in df_hoja.columns:
                            # Filtrar filas válidas
                            df_hoja = df_hoja.dropna(subset=['COD', 'TEXTO'])

                            if len(df_hoja) > 0:
                                # Convertir a formato Catalogo
                                codigos = [
                                    CodigoHistorico(
                                        codigo=str(row['COD']),
                                        descripcion=str(row['TEXTO'])
                                    )
                                    for _, row in df_hoja.iterrows()
                                ]

                                self.catalogos[hoja] = Catalogo(
                                    pregunta=hoja,
                                    codigos=codigos
                                )

                                print(f"[v0.5] Catálogo cargado para {hoja}: {len(codigos)} códigos")

                    except Exception as e:
                        print(f"[WARNING] Error al cargar hoja {hoja}: {e}")
                        continue

            if not self.catalogos:
                print("[WARNING] No se pudieron cargar catálogos históricos")
                return False

            print(f"[v0.5] Total preguntas con catálogo: {len(self.catalogos)}")

            # RE-MAPEAR columnas ahora que tenemos catálogos cargados
            if hasattr(self, 'df_respuestas_raw') and self.df_respuestas_raw is not None:
                print("[v0.5] Re-mapeando columnas con catálogos disponibles...")
                self.mapeo_columnas = self.mapear_columnas_preguntas(self.df_respuestas_raw)

            return True

        except Exception as e:
            print(f"[ERROR] Error al cargar catálogos: {e}")
            return False

    def mapear_columnas_preguntas(self, df_respuestas: pd.DataFrame) -> Dict[str, str]:
        """
        Mapea columnas del Excel con nombres de preguntas de forma GENÉRICA
        """
        mapeo = {}

        print(f"[v0.5] Columnas encontradas: {df_respuestas.columns.tolist()}")
        print(f"[v0.5] Catálogos disponibles: {list(self.catalogos.keys())}")

        # Normalizar nombres de catálogos para búsqueda flexible
        catalogos_normalizados = {
            self._normalizar_nombre(k): k
            for k in self.catalogos.keys()
        }

        for col in df_respuestas.columns:
            # Ignorar columnas que claramente no son preguntas
            if self._es_columna_metadata(col):
                continue

            # ESTRATEGIA 1: Extraer código de pregunta del inicio
            codigo_extraido = self._extraer_codigo_pregunta(col)

            if codigo_extraido:
                # Buscar el catálogo correspondiente
                catalogo_encontrado = self._buscar_catalogo_por_codigo(
                    codigo_extraido,
                    catalogos_normalizados
                )

                if catalogo_encontrado:
                    mapeo[col] = catalogo_encontrado
                    print(f"[v0.5] '{col[:50]}...' -> '{catalogo_encontrado}' (código extraído)")
                    continue

            # ESTRATEGIA 2: Match exacto con catálogo
            if col in self.catalogos:
                mapeo[col] = col
                print(f"[v0.5] '{col[:50]}...' -> '{col}' (match exacto)")
                continue

            # ESTRATEGIA 3: Match normalizado con catálogo
            col_normalizado = self._normalizar_nombre(col)
            if col_normalizado in catalogos_normalizados:
                nombre_catalogo = catalogos_normalizados[col_normalizado]
                mapeo[col] = nombre_catalogo
                print(f"[v0.5] '{col[:50]}...' -> '{nombre_catalogo}' (match normalizado)")
                continue

            # ESTRATEGIA 4: Sin catálogo - usar nombre de columna
            mapeo[col] = col
            print(f"[v0.5] '{col[:50]}...' -> '{col}' (sin catálogo - generación pura)")

        if not mapeo:
            print("[WARNING] No se identificaron preguntas válidas")
        else:
            print(f"[v0.5] Total preguntas a procesar: {len(mapeo)}")

        return mapeo

    def _extraer_codigo_pregunta(self, nombre_columna: str) -> Optional[str]:
        """
        Extrae código de pregunta del inicio de la columna
        """
        import re

        texto = nombre_columna.strip()

        # Patrón 1: Letras y números al inicio terminados en punto o espacio
        match = re.match(r'^([a-zA-Z]*\d+[a-zA-Z]*\d*)[.\s]', texto)

        if match:
            codigo = match.group(1).upper()

            # Normalizar: solo agregar P si empieza con número
            if codigo and codigo[0].isdigit():
                codigo = 'P' + codigo

            return codigo

        # Patrón 2: Solo letras/números al inicio sin punto
        match = re.match(r'^([a-zA-Z]+\d+[a-zA-Z]*\d*)', texto, re.IGNORECASE)

        if match:
            codigo = match.group(1).upper()

            if codigo and codigo[0].isdigit():
                codigo = 'P' + codigo

            return codigo

        return None

    def _buscar_catalogo_por_codigo(
        self,
        codigo: str,
        catalogos_normalizados: Dict[str, str]
    ) -> Optional[str]:
        """
        Busca catálogo que coincida con el código extraído
        """
        codigo_norm = self._normalizar_nombre(codigo)

        if codigo_norm in catalogos_normalizados:
            return catalogos_normalizados[codigo_norm]

        for cat_nombre in self.catalogos.keys():
            if cat_nombre.upper() == codigo.upper():
                return cat_nombre

        return None

    def _normalizar_nombre(self, nombre: str) -> str:
        """
        Normaliza nombre de columna/hoja para comparación flexible
        """
        import re
        normalizado = nombre.lower()
        normalizado = normalizado.replace('á', 'a').replace('é', 'e').replace('í', 'i')
        normalizado = normalizado.replace('ó', 'o').replace('ú', 'u').replace('ñ', 'n')
        normalizado = re.sub(r'[^a-z0-9]', '', normalizado)
        return normalizado

    def _es_columna_metadata(self, nombre_columna: str) -> bool:
        """
        Detecta si una columna es metadata (ID, fecha, etc) y no una pregunta
        """
        nombre_lower = nombre_columna.lower()

        metadata_keywords = [
            'id', 'fecha', 'date', 'timestamp', 'hora',
            'usuario', 'user', 'email', 'nombre', 'name',
            'edad', 'age', 'sexo', 'genero', 'gender',
            'ciudad', 'city', 'pais', 'country',
            'unnamed'
        ]

        if len(nombre_lower) <= 2:
            return True

        for keyword in metadata_keywords:
            if keyword in nombre_lower and len(nombre_lower) < 15:
                return True

        return False

    def procesar_respuestas(self, ruta_respuestas: str) -> bool:
        """
        Carga y limpia respuestas del Excel
        """
        try:
            respuestas_raw = load_data(ruta_respuestas)
            print(f"[v0.5] Cargadas {len(respuestas_raw)} respuestas")

            self.df_respuestas_raw = respuestas_raw

            self.mapeo_columnas = self.mapear_columnas_preguntas(respuestas_raw)

            if not self.mapeo_columnas:
                print("[ERROR] No se pudieron mapear columnas con preguntas")
                return False

            respuestas_procesadas = respuestas_raw.copy()

            for columna, pregunta in self.mapeo_columnas.items():
                print(f"[v0.5] Procesando {columna} -> {pregunta}")

                respuestas_procesadas[f'{columna}_limpio'] = \
                    respuestas_procesadas[columna].fillna('').apply(
                        lambda x: clean_text_for_gpt(x)
                    )

            self.respuestas_procesadas = respuestas_procesadas
            print("[v0.5] Respuestas procesadas correctamente")
            return True

        except Exception as e:
            print(f"[ERROR] Error al procesar respuestas: {e}")
            return False

    async def codificar_todas_preguntas(self, progress_callback=None) -> pd.DataFrame:
        """
        Codifica todas las preguntas usando GPT Híbrido

        Args:
            progress_callback: Función opcional para reportar progreso
                              Recibe: (progreso: float 0-1, mensaje: str)
        """
        if self.respuestas_procesadas is None:
            raise ValueError("Debe procesar respuestas primero")

        resultados = self.respuestas_procesadas.copy()

        print("\n" + "="*70)
        print("INICIANDO CODIFICACIÓN v0.5 (GPT HÍBRIDO)")
        print("="*70)

        total_preguntas = len(self.mapeo_columnas)

        for idx_pregunta, (columna, pregunta) in enumerate(self.mapeo_columnas.items(), 1):
            print(f"\n--- Procesando {pregunta} ---")

            if progress_callback:
                progreso_pregunta = (idx_pregunta - 1) / total_preguntas
                progress_callback(
                    progreso_pregunta,
                    f"📋 Pregunta {idx_pregunta}/{total_preguntas}: {pregunta}"
                )

            catalogo = self.catalogos.get(pregunta, Catalogo(pregunta=pregunta, codigos=[]))

            if not catalogo.codigos:
                print(f"[INFO] No hay catálogo histórico para {pregunta}")
            else:
                print(f"[INFO] Catálogo con {len(catalogo.codigos)} códigos")

            resultados[f'{pregunta}_decision'] = None
            resultados[f'{pregunta}_codigo_historico'] = None
            resultados[f'{pregunta}_codigo_nuevo'] = None
            resultados[f'{pregunta}_descripcion_nueva'] = None
            resultados[f'{pregunta}_confianza'] = 0.0
            resultados[f'{pregunta}_justificacion'] = None

            col_limpio = f'{columna}_limpio'
            respuestas_validas = resultados[resultados[col_limpio].str.len() > 0]

            if len(respuestas_validas) == 0:
                print(f"[WARNING] No hay respuestas válidas para {pregunta}")
                continue

            batch_size = 20
            total_respuestas = len(respuestas_validas)
            total_batches = (total_respuestas - 1) // batch_size + 1

            print(f"[v0.5] Procesando {total_respuestas} respuestas en batches de {batch_size}")

            todas_codificaciones_pregunta = []

            for i in range(0, total_respuestas, batch_size):
                batch_df = respuestas_validas.iloc[i:i+batch_size]
                batch_num = i // batch_size + 1

                if progress_callback:
                    progreso_en_pregunta = (batch_num - 1) / total_batches
                    progreso_global = (idx_pregunta - 1 + progreso_en_pregunta) / total_preguntas

                    respuestas_procesadas_count = min(i + batch_size, total_respuestas)
                    progress_callback(
                        progreso_global,
                        f"🤖 {pregunta} | Batch {batch_num}/{total_batches} ({respuestas_procesadas_count}/{total_respuestas} respuestas)"
                    )

                respuestas_batch = [
                    RespuestaInput(
                        id=str(idx),
                        texto=row[col_limpio],
                        pregunta=pregunta
                    )
                    for idx, row in batch_df.iterrows()
                ]

                print(f"[v0.5] Batch {batch_num}/{total_batches}")
                codificaciones = await self.gpt.codificar_batch(
                    pregunta=pregunta,
                    respuestas=respuestas_batch,
                    catalogo=catalogo,
                    normalizar=False  # NO normalizar dentro del batch
                )

                todas_codificaciones_pregunta.extend(codificaciones)

            # Normalizar TODOS los códigos nuevos de esta pregunta juntos
            print(f"[NORMALIZACIÓN] Procesando {len(todas_codificaciones_pregunta)} codificaciones de {pregunta}")
            todas_codificaciones_pregunta = self._normalizar_codigos_pregunta(
                todas_codificaciones_pregunta,
                catalogo
            )

            # Aplicar resultados normalizados
            for cod in todas_codificaciones_pregunta:
                idx = int(cod.respuesta_id)

                resultados.at[idx, f'{pregunta}_decision'] = cod.decision
                resultados.at[idx, f'{pregunta}_confianza'] = cod.confianza
                resultados.at[idx, f'{pregunta}_justificacion'] = cod.justificacion

                # COLUMNA UNIFICADA DE CÓDIGO
                codigos_asignados = []

                if cod.codigos_historicos:
                    codigos_str = [str(c) for c in cod.codigos_historicos]
                    codigos_asignados.extend(codigos_str)

                if cod.codigos_nuevos:
                    codigos_asignados.extend(cod.codigos_nuevos)

                if codigos_asignados:
                    resultados.at[idx, f'{pregunta}_codigo'] = ";".join(codigos_asignados)

                # Descripción solo para códigos NUEVOS
                if cod.codigos_nuevos and cod.descripciones_nuevas:
                    resultados.at[idx, f'{pregunta}_descripcion_nueva'] = " | ".join(cod.descripciones_nuevas)

                    for i, codigo_nuevo in enumerate(cod.codigos_nuevos):
                        descripcion = cod.descripciones_nuevas[i] if i < len(cod.descripciones_nuevas) else ""
                        self.codigos_nuevos.append({
                            'pregunta': pregunta,
                            'codigo_nuevo': codigo_nuevo,
                            'descripcion': descripcion,
                            'idea_principal': cod.idea_principal
                        })

            print(f"[v0.5] Codificación completada para {pregunta}")

        if progress_callback:
            progress_callback(1.0, f"✅ Todas las preguntas procesadas ({total_preguntas}/{total_preguntas})")

        print("\n" + "="*70)
        print("CODIFICACIÓN COMPLETADA")
        print(f"Costo total: ${self.gpt.costo_total:.4f}")
        print("="*70)

        return self._filtrar_columnas_exportar(resultados)

    def _similitud_descripciones(self, desc1: str, desc2: str) -> float:
        """
        Calcula similitud entre dos descripciones (0.0 a 1.0)
        """
        import unicodedata
        import re

        def normalizar(texto):
            texto = ''.join(
                c for c in unicodedata.normalize('NFD', texto)
                if unicodedata.category(c) != 'Mn'
            )
            texto = re.sub(r'[^a-z0-9\s]', ' ', texto.lower())
            stop_words = {'de', 'del', 'la', 'el', 'en', 'para', 'por', 'con', 'sin', 'sobre', 'a', 'y', 'o'}
            palabras = [p for p in texto.split() if p and p not in stop_words]
            return set(palabras), ' '.join(palabras)

        palabras1, texto1 = normalizar(desc1)
        palabras2, texto2 = normalizar(desc2)

        if not palabras1 or not palabras2:
            return 0.0

        if texto1 in texto2 or texto2 in texto1:
            return 0.95

        interseccion = len(palabras1 & palabras2)
        union = len(palabras1 | palabras2)
        similitud_jaccard = interseccion / union if union > 0 else 0.0

        min_palabras = min(len(palabras1), len(palabras2))
        if interseccion >= min_palabras * 0.8:
            return 0.90

        return similitud_jaccard

    def _normalizar_codigos_pregunta(
        self,
        codificaciones: List[ResultadoCodificacion],
        catalogo: Catalogo
    ) -> List[ResultadoCodificacion]:
        """
        Normaliza códigos nuevos para UNA pregunta completa
        """
        # Calcular próximo código disponible del catálogo
        codigos_numericos = []
        for cod in catalogo.codigos:
            codigo_str = cod.codigo if hasattr(cod, 'codigo') else cod['codigo']
            try:
                codigos_numericos.append(int(codigo_str))
            except (ValueError, TypeError):
                pass
        proximo_codigo = max(codigos_numericos) + 1 if codigos_numericos else 1

        print(f"\n{'='*70}")
        print(f"[NORMALIZACIÓN] Código inicial: {proximo_codigo}")
        print(f"{'='*70}")

        # Recolectar TODAS las descripciones únicas
        descripciones_originales = []
        for cod in codificaciones:
            if (cod.decision in ["nuevo", "mixto"]) and cod.descripciones_nuevas:
                for desc in cod.descripciones_nuevas:
                    if desc not in descripciones_originales:
                        descripciones_originales.append(desc)

        # Agrupar descripciones similares
        mapa_unificacion = {}
        descripciones_representativas = []

        umbral_similitud = 0.85

        for desc in descripciones_originales:
            es_redundante = False

            for desc_rep in descripciones_representativas:
                similitud = self._similitud_descripciones(desc, desc_rep)

                if similitud >= umbral_similitud:
                    mapa_unificacion[desc] = desc_rep
                    es_redundante = True
                    print(f"[SIMILITUD {similitud:.2f}] '{desc}' → '{desc_rep}' (unificado)")
                    break

            if not es_redundante:
                mapa_unificacion[desc] = desc
                descripciones_representativas.append(desc)

        # Asignar códigos a las descripciones representativas
        mapa_codigos = {}
        codigo_actual = proximo_codigo

        for desc_rep in descripciones_representativas:
            mapa_codigos[desc_rep] = str(codigo_actual)
            print(f"[CODIGO {codigo_actual}] {desc_rep}")
            codigo_actual += 1

        # Reasignar códigos normalizados
        codificaciones_normalizadas = []
        for cod in codificaciones:
            if (cod.decision in ["nuevo", "mixto"]) and cod.descripciones_nuevas:
                codigos_normalizados = []
                descripciones_normalizadas = []

                for desc in cod.descripciones_nuevas:
                    desc_unificada = mapa_unificacion.get(desc, desc)
                    codigo_correcto = mapa_codigos[desc_unificada]

                    if codigo_correcto not in codigos_normalizados:
                        codigos_normalizados.append(codigo_correcto)
                        descripciones_normalizadas.append(desc_unificada)

                if codigos_normalizados:
                    cod_nuevo = ResultadoCodificacion(
                        respuesta_id=cod.respuesta_id,
                        decision=cod.decision,
                        codigos_historicos=cod.codigos_historicos,
                        codigo_nuevo=codigos_normalizados[0] if codigos_normalizados else None,
                        descripcion_nueva=descripciones_normalizadas[0] if descripciones_normalizadas else None,
                        idea_principal=cod.idea_principal,
                        confianza=cod.confianza,
                        justificacion=cod.justificacion,
                        codigos_nuevos=codigos_normalizados,
                        descripciones_nuevas=descripciones_normalizadas
                    )
                    codificaciones_normalizadas.append(cod_nuevo)
                else:
                    if cod.codigos_historicos:
                        cod_nuevo = ResultadoCodificacion(
                            respuesta_id=cod.respuesta_id,
                            decision="asignar",
                            codigos_historicos=cod.codigos_historicos,
                            codigo_nuevo=None,
                            descripcion_nueva=None,
                            idea_principal=cod.idea_principal,
                            confianza=cod.confianza,
                            justificacion=cod.justificacion + " (códigos nuevos unificados)",
                            codigos_nuevos=[],
                            descripciones_nuevas=[]
                        )
                        codificaciones_normalizadas.append(cod_nuevo)
            else:
                codificaciones_normalizadas.append(cod)

        print(f"{'='*70}")
        print(f"[NORMALIZACIÓN] Total códigos únicos generados: {len(mapa_codigos)}")
        print(f"[NORMALIZACIÓN] Descripciones unificadas: {len(descripciones_originales) - len(descripciones_representativas)}")
        print(f"{'='*70}\n")
        return codificaciones_normalizadas

    def _filtrar_columnas_exportar(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Selecciona columnas relevantes para exportar
        """
        try:
            columnas_originales = list(self.mapeo_columnas.keys())
            columnas_limpias = [f"{col}_limpio" for col in columnas_originales if f"{col}_limpio" in df.columns]

            columnas_resultados = []
            for _, pregunta in self.mapeo_columnas.items():
                for sufijo in ['_decision', '_codigo', '_descripcion_nueva', '_confianza', '_justificacion']:
                    col = f"{pregunta}{sufijo}"
                    if col in df.columns:
                        columnas_resultados.append(col)

            otras_columnas = [c for c in df.columns if c not in columnas_originales + columnas_limpias + columnas_resultados]

            columnas_finales = otras_columnas + columnas_limpias + columnas_resultados
            columnas_finales = [c for c in columnas_finales if c in df.columns]

            print(f"[v0.5] Exportando {len(columnas_finales)} columnas")

            return df[columnas_finales]

        except Exception as e:
            print(f"[ERROR] Error al filtrar columnas: {e}")
            return df

    def exportar_catalogo_nuevos(self, ruta_salida: str = None, nombre_proyecto: str = None) -> Optional[str]:
        """
        Exporta catálogo de códigos nuevos generados SOLO de este proyecto
        """
        if not self.codigos_nuevos:
            print("[INFO] No hay códigos nuevos para exportar")
            return None

        if ruta_salida is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            if nombre_proyecto:
                nombre_limpio = nombre_proyecto.replace('.xlsx', '').replace('.xls', '')
                nombre_limpio = ''.join(c for c in nombre_limpio if c.isalnum() or c in '_-')
                nombre_archivo = f"codigos_nuevos_{nombre_limpio}_{timestamp}.xlsx"
            else:
                nombre_archivo = f"codigos_nuevos_{timestamp}.xlsx"

            ruta_salida = f"result/codigos_nuevos/{nombre_archivo}"

        try:
            df_nuevos = pd.DataFrame(self.codigos_nuevos)

            if len(df_nuevos) > 0:
                df_consolidado = df_nuevos.groupby(
                    ['pregunta', 'codigo_nuevo', 'descripcion'],
                    dropna=False
                ).agg({
                    'idea_principal': 'first'
                }).reset_index()

                frecuencia = df_nuevos.groupby(
                    ['pregunta', 'codigo_nuevo']
                ).size().reset_index(name='frecuencia')

                df_consolidado = df_consolidado.merge(
                    frecuencia,
                    on=['pregunta', 'codigo_nuevo'],
                    how='left'
                )

                columnas_orden = [
                    'pregunta',
                    'codigo_nuevo',
                    'descripcion',
                    'idea_principal',
                    'frecuencia'
                ]
                df_consolidado = df_consolidado[columnas_orden]

                df_consolidado['aprobado'] = ''
                df_consolidado['codigo_final'] = ''
                df_consolidado['observaciones'] = ''

                df_consolidado = df_consolidado.sort_values(
                    ['pregunta', 'frecuencia'],
                    ascending=[True, False]
                )
            else:
                df_consolidado = df_nuevos

            os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)

            with pd.ExcelWriter(ruta_salida, engine='openpyxl') as writer:
                df_consolidado.to_excel(writer, sheet_name='Codigos_Nuevos', index=False)

                worksheet = writer.sheets['Codigos_Nuevos']
                worksheet.column_dimensions['A'].width = 15
                worksheet.column_dimensions['B'].width = 35
                worksheet.column_dimensions['C'].width = 50
                worksheet.column_dimensions['D'].width = 50
                worksheet.column_dimensions['E'].width = 12
                worksheet.column_dimensions['F'].width = 12
                worksheet.column_dimensions['G'].width = 15
                worksheet.column_dimensions['H'].width = 40

            print(f"\n[v0.5] Catálogo de códigos nuevos exportado:")
            print(f"   - Archivo: {ruta_salida}")
            print(f"   - Códigos únicos: {len(df_consolidado)}")
            print(f"   - Respuestas con códigos nuevos: {len(self.codigos_nuevos)}")

            if len(df_consolidado) > 0:
                print(f"\n   Desglose por pregunta:")
                resumen = df_consolidado.groupby('pregunta').size()
                for pregunta, cantidad in resumen.items():
                    print(f"     - {pregunta}: {cantidad} códigos nuevos")

            return ruta_salida

        except Exception as e:
            print(f"[ERROR] Error al exportar catálogo nuevos: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def ejecutar_codificacion(
        self,
        ruta_respuestas: str,
        ruta_codigos: Optional[str] = None,
        progress_callback=None
    ) -> pd.DataFrame:
        """
        Ejecuta proceso completo de codificación v0.5
        """
        print("\n" + "="*70)
        print("SISTEMA DE CODIFICACIÓN HÍBRIDO v0.5")
        print("="*70)

        # 1. Procesar respuestas
        if not self.procesar_respuestas(ruta_respuestas):
            raise Exception("Error al procesar respuestas")

        # 2. Cargar catálogos (opcional)
        if ruta_codigos:
            self.cargar_catalogos(ruta_codigos)
        else:
            print("[INFO] Sin catálogos históricos - modo generación pura")

        # 3. Codificar con GPT
        resultados = await self.codificar_todas_preguntas(progress_callback)

        # 4. Exportar códigos nuevos
        nombre_proyecto = Path(ruta_respuestas).stem
        self.exportar_catalogo_nuevos(nombre_proyecto=nombre_proyecto)

        return resultados

    def guardar_resultados(self, resultados: pd.DataFrame, ruta: str):
        """
        Guarda resultados en Excel
        """
        save_data(resultados, ruta)
        print(f"[v0.5] Resultados guardados en: {ruta}")

