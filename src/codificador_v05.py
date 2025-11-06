"""
Codificador Hibrido v0.5
Sistema simplificado sin embeddings que usa GPT directamente
"""

import pandas as pd
import asyncio
import os
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime

from config import USE_GPT_MOCK
from utils import clean_text_for_gpt, load_data, save_data
from contexto import ContextoProyecto

# Importar GPT (real o mock segun configuracion)
if USE_GPT_MOCK:
    from gpt_hibrido_mock import GptHibridoMock as GptHibrido
    from gpt_hibrido import RespuestaInput, Catalogo, ResultadoCodificacion
    print("[v0.5] Usando GPT Hibrido MOCK (sin costos)")
else:
    from gpt_hibrido import GptHibrido, RespuestaInput, Catalogo, ResultadoCodificacion
    print("[v0.5] Usando GPT Hibrido REAL (consumira API)")


class CodificadorHibridoV05:
    
    def __init__(self, contexto: Optional[ContextoProyecto] = None, modelo: str = "gpt-4o-mini"):
        self.gpt = GptHibrido(model=modelo)
        self.respuestas_procesadas = None
        self.mapeo_columnas = {}  # columna -> pregunta
        self.catalogos = {}  # pregunta -> Catalogo
        self.codigos_nuevos = []  # Lista de codigos nuevos generados
        self.contexto = contexto or ContextoProyecto.vacio()  # Contexto del proyecto
    
    def establecer_contexto(self, contexto: ContextoProyecto):
        """
        Establece o actualiza el contexto del proyecto
        
        Args:
            contexto: Instancia de ContextoProyecto con informacion del proyecto
        """
        self.contexto = contexto
        
        if contexto.tiene_contexto():
            print(f"[v0.5] Contexto establecido: {contexto.resumen_corto()}")
        else:
            print("[v0.5] Contexto vacio (codificacion sin contexto)")
    
    def cargar_catalogos(self, ruta_codigos: str) -> bool:
        """
        Carga catalogos de codigos historicos por pregunta
        """
        try:
            with pd.ExcelFile(ruta_codigos) as excel_file:
                hojas_disponibles = excel_file.sheet_names
                print(f"[v0.5] Hojas de catalogo encontradas: {hojas_disponibles}")
                
                for hoja in hojas_disponibles:
                    try:
                        df_hoja = pd.read_excel(excel_file, sheet_name=hoja)
                        
                        # Verificar columnas requeridas
                        if 'COD' in df_hoja.columns and 'TEXTO' in df_hoja.columns:
                            # Filtrar filas validas
                            df_hoja = df_hoja.dropna(subset=['COD', 'TEXTO'])
                            
                            if len(df_hoja) > 0:
                                # Convertir a formato Catalogo
                                codigos = [
                                    {
                                        'codigo': str(row['COD']),
                                        'descripcion': str(row['TEXTO'])
                                    }
                                    for _, row in df_hoja.iterrows()
                                ]
                                
                                self.catalogos[hoja] = Catalogo(
                                    pregunta=hoja,
                                    codigos=codigos
                                )
                                
                                print(f"[v0.5] Catalogo cargado para {hoja}: {len(codigos)} codigos")
                        
                    except Exception as e:
                        print(f"[WARNING] Error al cargar hoja {hoja}: {e}")
                        continue
            
            if not self.catalogos:
                print("[WARNING] No se pudieron cargar catalogos historicos")
                return False
            
            print(f"[v0.5] Total preguntas con catalogo: {len(self.catalogos)}")
            
            # RE-MAPEAR columnas ahora que tenemos catálogos cargados
            if hasattr(self, 'df_respuestas_raw') and self.df_respuestas_raw is not None:
                print("[v0.5] Re-mapeando columnas con catálogos disponibles...")
                self.mapeo_columnas = self.mapear_columnas_preguntas(self.df_respuestas_raw)
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Error al cargar catalogos: {e}")
            return False
    
    def mapear_columnas_preguntas(self, df_respuestas: pd.DataFrame) -> Dict[str, str]:
        """
        Mapea columnas del Excel con nombres de preguntas de forma GENERICA
        
        Estrategia INTELIGENTE:
        1. Extrae código de pregunta del inicio (ej: "1a.", "P5AC.", "8d.")
        2. Normaliza el código (ej: "1a" -> "P1A", "5ac" -> "P5AC")
        3. Busca coincidencia con catálogos disponibles
        4. Si no hay código o catálogo, usa nombre completo
        """
        mapeo = {}
        
        print(f"[v0.5] Columnas encontradas: {df_respuestas.columns.tolist()}")
        print(f"[v0.5] Catalogos disponibles: {list(self.catalogos.keys())}")
        
        # Normalizar nombres de catalogos para busqueda flexible
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
            print("[WARNING] No se identificaron preguntas validas")
        else:
            print(f"[v0.5] Total preguntas a procesar: {len(mapeo)}")
        
        return mapeo
    
    def _extraer_codigo_pregunta(self, nombre_columna: str) -> Optional[str]:
        """
        Extrae código de pregunta del inicio de la columna
        
        Ejemplos:
        - "1a. ¿Qué funciones..." → "P1A"
        - "5AC. ¿Por qué no..." → "P5AC"
        - "8d. Mencione..." → "P8D"
        - "P12A. Algo..." → "P12A"
        - "12a. ¿Por qué..." → "P12A"
        - "FC1. ¿Cómo se llama..." → "FC1"
        - "PA3. Descripción..." → "PA3"
        """
        import re
        
        # Limpiar espacios al inicio/final
        texto = nombre_columna.strip()
        
        # Patrón 1: Letras y números al inicio terminados en punto o espacio
        # Captura: letras (opcionales) + números + letras (opcionales) antes del primer punto o espacio
        # Ejemplos: "FC1.", "P12A.", "1a.", "5AC.", "PA3."
        match = re.match(r'^([a-zA-Z]*\d+[a-zA-Z]*\d*)[.\s]', texto)
        
        if match:
            codigo = match.group(1).upper()
            
            # Normalizar: solo agregar P si empieza con número (no con letra)
            if codigo and codigo[0].isdigit():
                codigo = 'P' + codigo
            
            return codigo
        
        # Patrón 2: Solo letras/números al inicio sin punto 
        # Para códigos tipo "P12", "P1A", "FC1" sin punto
        match = re.match(r'^([a-zA-Z]+\d+[a-zA-Z]*\d*)', texto, re.IGNORECASE)
        
        if match:
            codigo = match.group(1).upper()
            
            # Normalizar: solo agregar P si empieza con número
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
        
        Busca con flexibilidad:
        - Código exacto normalizado
        - Variaciones comunes (P1A = P1a = p1a)
        """
        # Normalizar código buscado
        codigo_norm = self._normalizar_nombre(codigo)
        
        # Buscar en catálogos normalizados
        if codigo_norm in catalogos_normalizados:
            return catalogos_normalizados[codigo_norm]
        
        # Buscar en catálogos originales (case-insensitive)
        for cat_nombre in self.catalogos.keys():
            if cat_nombre.upper() == codigo.upper():
                return cat_nombre
        
        return None
    
    def _normalizar_nombre(self, nombre: str) -> str:
        """
        Normaliza nombre de columna/hoja para comparacion flexible
        """
        import re
        # Minusculas, sin acentos, sin espacios extras, sin caracteres especiales
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
        
        # Columnas comunes que NO son preguntas
        metadata_keywords = [
            'id', 'fecha', 'date', 'timestamp', 'hora',
            'usuario', 'user', 'email', 'nombre', 'name',
            'edad', 'age', 'sexo', 'genero', 'gender',
            'ciudad', 'city', 'pais', 'country',
            'unnamed'  # Columnas sin nombre de pandas
        ]
        
        # Si es muy corto (probable ID)
        if len(nombre_lower) <= 2:
            return True
        
        # Si contiene keywords de metadata
        for keyword in metadata_keywords:
            if keyword in nombre_lower and len(nombre_lower) < 15:
                return True
        
        return False
    
    def procesar_respuestas(self, ruta_respuestas: str) -> bool:
        """
        Carga y limpia respuestas del Excel
        """
        try:
            # Cargar Excel
            respuestas_raw = load_data(ruta_respuestas)
            print(f"[v0.5] Cargadas {len(respuestas_raw)} respuestas")
            
            # Guardar referencia para poder re-mapear después de cargar catálogos
            self.df_respuestas_raw = respuestas_raw
            
            # Mapear columnas (se re-mapeará después de cargar catálogos)
            self.mapeo_columnas = self.mapear_columnas_preguntas(respuestas_raw)
            
            if not self.mapeo_columnas:
                print("[ERROR] No se pudieron mapear columnas con preguntas")
                return False
            
            # Limpiar textos de cada columna
            respuestas_procesadas = respuestas_raw.copy()
            
            for columna, pregunta in self.mapeo_columnas.items():
                print(f"[v0.5] Procesando {columna} -> {pregunta}")
                
                # Limpieza MÍNIMA optimizada para GPT
                # Preserva mayúsculas, puntuación, tildes (máximo contexto)
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
        Codifica todas las preguntas usando GPT Hibrido
        
        Args:
            progress_callback: Función opcional para reportar progreso
                              Recibe: (progreso: float 0-1, mensaje: str)
        """
        if self.respuestas_procesadas is None:
            raise ValueError("Debe procesar respuestas primero")
        
        resultados = self.respuestas_procesadas.copy()
        
        print("\n" + "="*70)
        print("INICIANDO CODIFICACION v0.5 (GPT HIBRIDO)")
        print("="*70)
        
        # Calcular progreso total
        total_preguntas = len(self.mapeo_columnas)
        
        for idx_pregunta, (columna, pregunta) in enumerate(self.mapeo_columnas.items(), 1):
            print(f"\n--- Procesando {pregunta} ---")
            
            # Reportar progreso: inicio de pregunta
            if progress_callback:
                progreso_pregunta = (idx_pregunta - 1) / total_preguntas
                progress_callback(
                    progreso_pregunta,
                    f"📋 Pregunta {idx_pregunta}/{total_preguntas}: {pregunta}"
                )
            
            # Obtener catalogo (o crear vacio si no existe)
            catalogo = self.catalogos.get(pregunta, Catalogo(pregunta=pregunta, codigos=[]))
            
            if not catalogo.codigos:
                print(f"[INFO] No hay catalogo historico para {pregunta}")
            else:
                print(f"[INFO] Catalogo con {len(catalogo.codigos)} codigos")
            
            # Crear columnas de resultados
            resultados[f'{pregunta}_decision'] = None
            resultados[f'{pregunta}_codigo_historico'] = None
            resultados[f'{pregunta}_codigo_nuevo'] = None
            resultados[f'{pregunta}_descripcion_nueva'] = None
            resultados[f'{pregunta}_confianza'] = 0.0
            resultados[f'{pregunta}_justificacion'] = None
            
            # Filtrar respuestas validas
            col_limpio = f'{columna}_limpio'
            respuestas_validas = resultados[resultados[col_limpio].str.len() > 0]
            
            if len(respuestas_validas) == 0:
                print(f"[WARNING] No hay respuestas validas para {pregunta}")
                continue
            
            # Crear batches de ~20 respuestas para GPT
            batch_size = 20
            total_respuestas = len(respuestas_validas)
            total_batches = (total_respuestas - 1) // batch_size + 1
            
            print(f"[v0.5] Procesando {total_respuestas} respuestas en batches de {batch_size}")
            
            # Acumular TODAS las codificaciones de esta pregunta para normalizar al final
            todas_codificaciones_pregunta = []
            
            for i in range(0, total_respuestas, batch_size):
                batch_df = respuestas_validas.iloc[i:i+batch_size]
                batch_num = i // batch_size + 1
                
                # Reportar progreso: batch actual
                if progress_callback:
                    # Calcular progreso dentro de esta pregunta
                    progreso_en_pregunta = (batch_num - 1) / total_batches
                    progreso_global = (idx_pregunta - 1 + progreso_en_pregunta) / total_preguntas
                    
                    respuestas_procesadas = min(i + batch_size, total_respuestas)
                    progress_callback(
                        progreso_global,
                        f"🤖 {pregunta} | Batch {batch_num}/{total_batches} ({respuestas_procesadas}/{total_respuestas} respuestas)"
                    )
                
                # Preparar respuestas para GPT
                respuestas_batch = [
                    RespuestaInput(
                        id=str(idx),
                        texto=row[col_limpio],
                        pregunta=pregunta
                    )
                    for idx, row in batch_df.iterrows()
                ]
                
                # Codificar con GPT (con contexto) - SIN normalizar aún
                print(f"[v0.5] Batch {batch_num}/{total_batches}")
                codificaciones = await self.gpt.codificar_batch(
                    pregunta=pregunta,
                    respuestas=respuestas_batch,
                    catalogo=catalogo,
                    contexto=self.contexto,
                    normalizar=False  # NO normalizar dentro del batch
                )
                
                # Acumular codificaciones (no aplicar aún)
                todas_codificaciones_pregunta.extend(codificaciones)
            
            # AHORA: Normalizar TODOS los códigos nuevos de esta pregunta juntos
            print(f"[NORMALIZACION] Procesando {len(todas_codificaciones_pregunta)} codificaciones de {pregunta}")
            todas_codificaciones_pregunta = self._normalizar_codigos_pregunta(
                todas_codificaciones_pregunta, 
                catalogo
            )
            
            # FINALMENTE: Aplicar resultados normalizados
            for cod in todas_codificaciones_pregunta:
                idx = int(cod.respuesta_id)
                
                resultados.at[idx, f'{pregunta}_decision'] = cod.decision
                resultados.at[idx, f'{pregunta}_confianza'] = cod.confianza
                resultados.at[idx, f'{pregunta}_justificacion'] = cod.justificacion
                
                # COLUMNA UNIFICADA DE CÓDIGO
                # Prioridad: históricos > nuevos > vacío (rechazado)
                codigos_asignados = []
                
                # 1. Agregar códigos históricos si existen
                if cod.codigos_historicos:
                    codigos_str = [str(c) for c in cod.codigos_historicos]
                    codigos_asignados.extend(codigos_str)
                
                # 2. Agregar códigos nuevos si existen
                if cod.codigos_nuevos:
                    codigos_asignados.extend(cod.codigos_nuevos)
                
                # 3. Guardar en columna unificada
                if codigos_asignados:
                    resultados.at[idx, f'{pregunta}_codigo'] = ";".join(codigos_asignados)
                
                # Descripción solo para códigos NUEVOS
                if cod.codigos_nuevos and cod.descripciones_nuevas:
                    resultados.at[idx, f'{pregunta}_descripcion_nueva'] = " | ".join(cod.descripciones_nuevas)
                    
                    # Guardar CADA código nuevo para catalogo consolidado
                    for i, codigo_nuevo in enumerate(cod.codigos_nuevos):
                        descripcion = cod.descripciones_nuevas[i] if i < len(cod.descripciones_nuevas) else ""
                        self.codigos_nuevos.append({
                            'pregunta': pregunta,
                            'codigo_nuevo': codigo_nuevo,
                            'descripcion': descripcion,
                            'idea_principal': cod.idea_principal
                        })
            
            print(f"[v0.5] Codificacion completada para {pregunta}")
        
        # Reportar progreso: completado
        if progress_callback:
            progress_callback(1.0, f"✅ Todas las preguntas procesadas ({total_preguntas}/{total_preguntas})")
        
        print("\n" + "="*70)
        print("CODIFICACION COMPLETADA")
        print(f"Costo total: ${self.gpt.costo_total:.4f}")
        print("="*70)
        
        return self._filtrar_columnas_exportar(resultados)
    
    def _similitud_descripciones(self, desc1: str, desc2: str) -> float:
        """
        Calcula similitud entre dos descripciones (0.0 a 1.0)
        Detecta redundancias como "Versatilidad de uso" vs "Versatilidad de uso en comidas"
        """
        # Normalizar: minúsculas, sin tildes, sin puntuación
        import unicodedata
        import re
        
        def normalizar(texto):
            # Remover tildes
            texto = ''.join(
                c for c in unicodedata.normalize('NFD', texto)
                if unicodedata.category(c) != 'Mn'
            )
            # Minúsculas y solo letras/espacios
            texto = re.sub(r'[^a-z0-9\s]', ' ', texto.lower())
            # Remover palabras vacías comunes
            stop_words = {'de', 'del', 'la', 'el', 'en', 'para', 'por', 'con', 'sin', 'sobre', 'a', 'y', 'o'}
            palabras = [p for p in texto.split() if p and p not in stop_words]
            return set(palabras), ' '.join(palabras)
        
        palabras1, texto1 = normalizar(desc1)
        palabras2, texto2 = normalizar(desc2)
        
        if not palabras1 or not palabras2:
            return 0.0
        
        # Caso 1: Una descripción contiene completamente a la otra
        # "Versatilidad uso" está contenido en "Versatilidad uso comidas"
        if texto1 in texto2 or texto2 in texto1:
            return 0.95  # Muy similar
        
        # Caso 2: Similitud de Jaccard (intersección / unión)
        interseccion = len(palabras1 & palabras2)
        union = len(palabras1 | palabras2)
        similitud_jaccard = interseccion / union if union > 0 else 0.0
        
        # Caso 3: Si comparten todas las palabras clave (>80% de la más corta)
        min_palabras = min(len(palabras1), len(palabras2))
        if interseccion >= min_palabras * 0.8:
            return 0.90
        
        return similitud_jaccard
    
    def _normalizar_codigos_pregunta(
        self, 
        codificaciones: List,
        catalogo
    ) -> List:
        """
        Normaliza códigos nuevos para UNA pregunta completa
        Garantiza que cada descripción ÚNICA tiene un código ÚNICO
        Detecta y unifica descripciones similares/redundantes
        Soporta múltiples códigos nuevos por respuesta
        """
        from gpt_hibrido import ResultadoCodificacion
        
        # Calcular próximo código disponible del catálogo
        codigos_numericos = []
        for cod in catalogo.codigos:
            try:
                codigos_numericos.append(int(cod['codigo']))
            except (ValueError, TypeError):
                pass
        proximo_codigo = max(codigos_numericos) + 1 if codigos_numericos else 1
        
        print(f"\n{'='*70}")
        print(f"[NORMALIZACION] Código inicial: {proximo_codigo}")
        print(f"{'='*70}")
        
        # Recolectar TODAS las descripciones únicas
        descripciones_originales = []
        for cod in codificaciones:
            if (cod.decision in ["nuevo", "mixto"]) and cod.descripciones_nuevas:
                for desc in cod.descripciones_nuevas:
                    if desc not in descripciones_originales:
                        descripciones_originales.append(desc)
        
        # Agrupar descripciones similares
        # Mapeo: descripción original -> descripción representativa
        mapa_unificacion = {}
        descripciones_representativas = []
        
        umbral_similitud = 0.85  # 85% de similitud para considerar redundantes
        
        for desc in descripciones_originales:
            # Buscar si es similar a alguna descripción ya agregada
            es_redundante = False
            
            for desc_rep in descripciones_representativas:
                similitud = self._similitud_descripciones(desc, desc_rep)
                
                if similitud >= umbral_similitud:
                    # Es redundante, mapear a la representativa
                    mapa_unificacion[desc] = desc_rep
                    es_redundante = True
                    print(f"[SIMILITUD {similitud:.2f}] '{desc}' → '{desc_rep}' (unificado)")
                    break
            
            if not es_redundante:
                # Es una descripción única, agregar como representativa
                mapa_unificacion[desc] = desc
                descripciones_representativas.append(desc)
        
        # Mapeo: descripción representativa -> código asignado
        mapa_codigos = {}
        codigo_actual = proximo_codigo
        
        # Asignar códigos a las descripciones representativas
        for desc_rep in descripciones_representativas:
            mapa_codigos[desc_rep] = str(codigo_actual)
            print(f"[CODIGO {codigo_actual}] {desc_rep}")
            codigo_actual += 1
        
        # Segunda pasada: reasignar códigos normalizados
        codificaciones_normalizadas = []
        for cod in codificaciones:
            if (cod.decision in ["nuevo", "mixto"]) and cod.descripciones_nuevas:
                # Normalizar CADA código de la lista
                codigos_normalizados = []
                descripciones_normalizadas = []
                
                for desc in cod.descripciones_nuevas:
                    # 1. Unificar con descripción representativa
                    desc_unificada = mapa_unificacion.get(desc, desc)
                    
                    # 2. Obtener código de la descripción unificada
                    codigo_correcto = mapa_codigos[desc_unificada]
                    
                    # Evitar duplicados en la misma respuesta
                    if codigo_correcto not in codigos_normalizados:
                        codigos_normalizados.append(codigo_correcto)
                        descripciones_normalizadas.append(desc_unificada)
                
                # Solo crear codificación si quedaron códigos después de deduplicar
                if codigos_normalizados:
                    # Crear nueva codificación con códigos normalizados
                    cod_nuevo = ResultadoCodificacion(
                        respuesta_id=cod.respuesta_id,
                        decision=cod.decision,
                        codigos_historicos=cod.codigos_historicos,
                        codigo_nuevo=codigos_normalizados[0] if codigos_normalizados else None,  # Compatibilidad
                        descripcion_nueva=descripciones_normalizadas[0] if descripciones_normalizadas else None,  # Compatibilidad
                        idea_principal=cod.idea_principal,
                        confianza=cod.confianza,
                        justificacion=cod.justificacion,
                        codigos_nuevos=codigos_normalizados,  # Lista normalizada y deduplicada
                        descripciones_nuevas=descripciones_normalizadas  # Descripciones unificadas
                    )
                    codificaciones_normalizadas.append(cod_nuevo)
                else:
                    # Si no quedaron códigos nuevos, convertir a "asignar" o "rechazar"
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
                # Mantener sin cambios (asignar, rechazar, etc.)
                codificaciones_normalizadas.append(cod)
        
        print(f"{'='*70}")
        print(f"[NORMALIZACION] Total códigos únicos generados: {len(mapa_codigos)}")
        print(f"[NORMALIZACION] Descripciones unificadas: {len(descripciones_originales) - len(descripciones_representativas)}")
        print(f"{'='*70}\n")
        return codificaciones_normalizadas
    
    def _filtrar_columnas_exportar(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Selecciona columnas relevantes para exportar
        """
        try:
            columnas_originales = list(self.mapeo_columnas.keys())
            columnas_limpias = [f"{col}_limpio" for col in columnas_originales if f"{col}_limpio" in df.columns]
            
            # Columnas de resultados por pregunta
            columnas_resultados = []
            for _, pregunta in self.mapeo_columnas.items():
                for sufijo in ['_decision', '_codigo', '_descripcion_nueva', '_confianza', '_justificacion']:
                    col = f"{pregunta}{sufijo}"
                    if col in df.columns:
                        columnas_resultados.append(col)
            
            # Todas las demas columnas
            otras_columnas = [c for c in df.columns if c not in columnas_originales + columnas_limpias + columnas_resultados]
            
            # Orden: otras -> limpias -> resultados
            columnas_finales = otras_columnas + columnas_limpias + columnas_resultados
            columnas_finales = [c for c in columnas_finales if c in df.columns]
            
            print(f"[v0.5] Exportando {len(columnas_finales)} columnas")
            
            return df[columnas_finales]
            
        except Exception as e:
            print(f"[ERROR] Error al filtrar columnas: {e}")
            return df
    
    def exportar_catalogo_nuevos(self, ruta_salida: str = None, nombre_proyecto: str = None) -> Optional[str]:
        """
        Exporta catalogo de codigos nuevos generados SOLO de este proyecto
        
        Args:
            ruta_salida: Ruta completa del archivo de salida (opcional)
            nombre_proyecto: Nombre del proyecto para generar nombre de archivo (opcional)
        
        Returns:
            Ruta del archivo generado o None si no hay codigos nuevos
        """
        if not self.codigos_nuevos:
            print("[INFO] No hay codigos nuevos para exportar")
            return None
        
        # Generar nombre de archivo dinamico si no se especifica
        if ruta_salida is None:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if nombre_proyecto:
                # Limpiar nombre de proyecto para usar en archivo
                nombre_limpio = nombre_proyecto.replace('.xlsx', '').replace('.xls', '')
                nombre_limpio = ''.join(c for c in nombre_limpio if c.isalnum() or c in '_-')
                nombre_archivo = f"codigos_nuevos_{nombre_limpio}_{timestamp}.xlsx"
            else:
                nombre_archivo = f"codigos_nuevos_{timestamp}.xlsx"
            
            ruta_salida = f"result/codigos_nuevos/{nombre_archivo}"
        
        try:
            # Consolidar codigos duplicados y contar frecuencia
            df_nuevos = pd.DataFrame(self.codigos_nuevos)
            
            # Agrupar por pregunta + codigo_nuevo + descripcion
            if len(df_nuevos) > 0:
                df_consolidado = df_nuevos.groupby(
                    ['pregunta', 'codigo_nuevo', 'descripcion'], 
                    dropna=False
                ).agg({
                    'idea_principal': 'first'  # Tomar la primera idea principal
                }).reset_index()
                
                # Contar frecuencia (cuántas respuestas usaron este código)
                frecuencia = df_nuevos.groupby(
                    ['pregunta', 'codigo_nuevo']
                ).size().reset_index(name='frecuencia')
                
                df_consolidado = df_consolidado.merge(
                    frecuencia, 
                    on=['pregunta', 'codigo_nuevo'], 
                    how='left'
                )
                
                # Reordenar columnas
                columnas_orden = [
                    'pregunta',
                    'codigo_nuevo',
                    'descripcion',
                    'idea_principal',
                    'frecuencia'
                ]
                df_consolidado = df_consolidado[columnas_orden]
                
                # Agregar columnas para revision manual
                df_consolidado['aprobado'] = ''
                df_consolidado['codigo_final'] = ''
                df_consolidado['observaciones'] = ''
                
                # Ordenar por pregunta y frecuencia (más usados primero)
                df_consolidado = df_consolidado.sort_values(
                    ['pregunta', 'frecuencia'], 
                    ascending=[True, False]
                )
            else:
                df_consolidado = df_nuevos
            
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
            
            # Exportar a Excel con formato
            with pd.ExcelWriter(ruta_salida, engine='openpyxl') as writer:
                df_consolidado.to_excel(writer, sheet_name='Codigos_Nuevos', index=False)
                
                # Ajustar ancho de columnas
                worksheet = writer.sheets['Codigos_Nuevos']
                worksheet.column_dimensions['A'].width = 15  # pregunta
                worksheet.column_dimensions['B'].width = 35  # codigo_nuevo
                worksheet.column_dimensions['C'].width = 50  # descripcion
                worksheet.column_dimensions['D'].width = 50  # idea_principal
                worksheet.column_dimensions['E'].width = 12  # frecuencia
                worksheet.column_dimensions['F'].width = 12  # aprobado
                worksheet.column_dimensions['G'].width = 15  # codigo_final
                worksheet.column_dimensions['H'].width = 40  # observaciones
            
            print(f"\n[v0.5] Catalogo de codigos nuevos exportado:")
            print(f"   - Archivo: {ruta_salida}")
            print(f"   - Codigos unicos: {len(df_consolidado)}")
            print(f"   - Respuestas con codigos nuevos: {len(self.codigos_nuevos)}")
            
            # Resumen por pregunta
            if len(df_consolidado) > 0:
                print(f"\n   Desglose por pregunta:")
                resumen = df_consolidado.groupby('pregunta').size()
                for pregunta, cantidad in resumen.items():
                    print(f"     - {pregunta}: {cantidad} codigos nuevos")
            
            return ruta_salida
            
        except Exception as e:
            print(f"[ERROR] Error al exportar catalogo nuevos: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def ejecutar_codificacion(
        self, 
        ruta_respuestas: str, 
        ruta_codigos: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Ejecuta proceso completo de codificacion v0.5
        """
        print("\n" + "="*70)
        print("SISTEMA DE CODIFICACION HIBRIDO v0.5")
        print("="*70)
        
        # 1. Procesar respuestas
        if not self.procesar_respuestas(ruta_respuestas):
            raise Exception("Error al procesar respuestas")
        
        # 2. Cargar catalogos (opcional)
        if ruta_codigos:
            self.cargar_catalogos(ruta_codigos)
        else:
            print("[INFO] Sin catalogos historicos - modo generacion pura")
        
        # 3. Codificar con GPT
        resultados = asyncio.run(self.codificar_todas_preguntas())
        
        # 4. Exportar codigos nuevos (con nombre de proyecto)
        nombre_proyecto = Path(ruta_respuestas).stem  # Extraer nombre sin extension
        self.exportar_catalogo_nuevos(nombre_proyecto=nombre_proyecto)
        
        return resultados
    
    def guardar_resultados(self, resultados: pd.DataFrame, ruta: str):
        """
        Guarda resultados en Excel con hoja de contexto
        """
        # Crear ExcelWriter para multiples hojas
        with pd.ExcelWriter(ruta, engine='openpyxl') as writer:
            # Hoja 1: Resultados de codificacion
            resultados.to_excel(writer, sheet_name='Resultados', index=False)
            
            # Hoja 2: Contexto del proyecto (si existe)
            if self.contexto.tiene_contexto():
                contexto_df = pd.DataFrame([
                    ["Campo", "Valor"],
                    ["Nombre Proyecto", self.contexto.nombre_proyecto],
                    ["Cliente", self.contexto.cliente],
                    ["Fecha", self.contexto.fecha or datetime.now().strftime("%Y-%m-%d")],
                    ["", ""],
                    ["Antecedentes", self.contexto.antecedentes],
                    ["Objetivo", self.contexto.objetivo],
                    ["Grupo Objetivo", self.contexto.grupo_objetivo],
                    ["Notas Adicionales", self.contexto.notas_adicionales],
                ])
                contexto_df.to_excel(writer, sheet_name='Contexto_Proyecto', index=False, header=False)
                print(f"[v0.5] Contexto guardado en hoja 'Contexto_Proyecto'")
        
        print(f"[v0.5] Resultados guardados en: {ruta}")

