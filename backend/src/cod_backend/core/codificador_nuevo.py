"""
Codificador nuevo basado en el Grafo V3 (evaluación booleana).

Implementa la misma lógica que el grafo de LangGraph, pero empaquetada
como un servicio de backend. Utiliza LangChain + LangGraph y carga los
prompts desde archivos .md para mantener el código limpio.

"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

import pandas as pd
from langgraph.pregel.main import RunnableConfig

from ..config import calcular_costo
from ..utils import load_data, save_data

# Imports de la estructura modular
from .codificacion.graph.state import EstadoCodificacion
from .codificacion.graph.builder import construir_grafo
from .codificacion.utils import calcular_batch_size_optimo, detectar_categoria_desde_texto


class CodificadorNuevo:
    """
    Codificador que implementa el flujo del Grafo V3 utilizando LangGraph.
    """

    def __init__(self, modelo: str = "gpt-4o-mini", config_auxiliar: Optional[Dict[str, Any]] = None):
        """
        Inicializa el codificador.
        
        Args:
            modelo: Modelo GPT a usar (por defecto "gpt-4o-mini")
            config_auxiliar: Configuración de dato auxiliar para categorización
        """
        self.modelo = modelo
        self.config_auxiliar = config_auxiliar
        self._instancia_id = id(self)
        self.df_codigos_nuevos: Optional[pd.DataFrame] = None
        self.stats: Optional[Dict[str, Any]] = None

    async def ejecutar_codificacion(
        self,
        ruta_respuestas: str,
        ruta_codigos: Optional[str] = None,
        progress_callback=None,
    ) -> pd.DataFrame:
        """
        Ejecuta el proceso completo de codificación usando el nuevo grafo.
        
        Args:
            ruta_respuestas: Ruta al archivo Excel con respuestas
            ruta_codigos: Ruta opcional al archivo Excel con catálogo histórico
            progress_callback: Función opcional para reportar progreso
            
        Returns:
            DataFrame con los resultados de la codificación
        """
        print("\n" + "=" * 70)
        print("SISTEMA DE CODIFICACIÓN NUEVO (GRAFO V3)")
        print("=" * 70)
        
        import time
        timestamp_ejecucion = time.time()
        print(f"🕐 Timestamp de ejecución: {timestamp_ejecucion}")

        # Cargar datos
        df = load_data(ruta_respuestas)
        print(f"📊 DataFrame cargado: {len(df)} filas, {len(df.columns)} columnas")
        print(f"📊 Columnas: {list(df.columns)}")
        
        # Determinar estructura según si se usa dato auxiliar
        usar_auxiliar = self.config_auxiliar is not None and self.config_auxiliar.get("usar", False)
        
        # Validar número mínimo de columnas
        if df.shape[1] < 2:
            raise ValueError(
                "El archivo de respuestas debe tener al menos 2 columnas "
                "(ID en la primera, respuestas en la segunda)."
            )
        
        columna_id = df.columns[0]
        columna_respuesta = df.columns[1]
        
        # Solo usar dato auxiliar si está configurado Y el archivo tiene 3+ columnas
        if usar_auxiliar and df.shape[1] >= 3:
            columna_auxiliar = df.columns[1]
            columna_respuesta = df.columns[2]
            print(f"📊 Usando dato auxiliar: columna '{columna_auxiliar}'")
        else:
            columna_auxiliar = None
            if usar_auxiliar and df.shape[1] < 3:
                print(f"⚠️  Dato auxiliar configurado pero el archivo solo tiene {df.shape[1]} columnas. "
                      f"Continuando sin dato auxiliar (usando solo ID y Respuestas).")
                # Desactivar uso de dato auxiliar si no está disponible
                usar_auxiliar = False
        
        nombre_pregunta = columna_respuesta

        # Procesar respuestas
        respuestas_reales: List[Dict[str, Any]] = []
        for idx, row in df.iterrows():
            fila_excel = idx + 2  # +2 porque Excel tiene header en fila 1, y pandas indexa desde 0
            id_valor = row[columna_id]
            if pd.isna(id_valor):
                id_valor = idx + 1

            # Filtrar respuestas vacías o solo con guiones
            raw_val = row[columna_respuesta]
            if pd.isna(raw_val):
                continue
            texto = str(raw_val).strip()
            if texto in ["", "-", "--", "---"]:
                continue
            
            # Incluir dato auxiliar si está configurado y disponible
            dato_auxiliar = None
            if usar_auxiliar and columna_auxiliar is not None:
                try:
                    raw_aux = row[columna_auxiliar]
                    if not pd.isna(raw_aux):
                        dato_auxiliar = str(raw_aux).strip()
                        # Si el dato auxiliar está vacío o es solo guiones, no incluirlo
                        if dato_auxiliar in ["", "-", "--", "---"]:
                            dato_auxiliar = None
                except (KeyError, IndexError):
                    # Si la columna no existe o hay algún error, simplemente no usar dato auxiliar
                    dato_auxiliar = None
            
            respuesta_item: Dict[str, Any] = {
                "fila_excel": fila_excel,
                "texto": texto,
                "id": id_valor
            }
            
            # Solo agregar dato_auxiliar si tiene un valor válido
            if dato_auxiliar:
                respuesta_item["dato_auxiliar"] = dato_auxiliar
            
            respuestas_reales.append(respuesta_item)
        
        print(f"📋 Total de filas en el archivo (DataFrame): {len(df)}")
        print(f"📋 Total de respuestas cargadas: {len(respuestas_reales)}")

        # Cargar catálogo histórico
        catalogo_historico, catalogo_por_categoria = self._cargar_catalogo(ruta_codigos)

        # Calcular código inicial para nuevos códigos
        proximo_codigo_inicial = self._calcular_codigo_inicial(catalogo_historico)

        print(f"\n📊 Respuestas cargadas: {len(respuestas_reales)}")
        print(f"📚 Catálogo histórico: {len(catalogo_historico)} códigos")
        print(f"🔢 Código inicial para nuevos códigos: {proximo_codigo_inicial}")

        # Calcular batch size óptimo
        batch_size = calcular_batch_size_optimo(
            total_respuestas=len(respuestas_reales),
            tamanio_catalogo=len(catalogo_historico),
            modelo=self.modelo
        )
        batches_esperados = (len(respuestas_reales) + batch_size - 1) // batch_size
        print(f"📦 Batch size optimizado: {batch_size} respuestas por batch ({batches_esperados} batches totales)")

        # Actualizar config_auxiliar si se desactivó automáticamente
        config_auxiliar_final = self.config_auxiliar
        if not usar_auxiliar and self.config_auxiliar is not None:
            # Crear una copia de la configuración pero con usar=False
            config_auxiliar_final = {**self.config_auxiliar, "usar": False}
        
        # Preparar estado inicial
        estado_inicial: EstadoCodificacion = {
            "pregunta": nombre_pregunta,
            "modelo_gpt": self.modelo,
            "batch_size": batch_size,
            "respuestas": respuestas_reales,
            "catalogo": catalogo_historico,
            "catalogo_por_categoria": catalogo_por_categoria,
            "batch_actual": 0,
            "batch_respuestas": [],
            "codificaciones": [],
            "validaciones_batch": [],
            "evaluaciones_batch": [],
            "cobertura_batch": [],
            "proximo_codigo_nuevo": proximo_codigo_inicial,
            "respuestas_especiales": {},
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "config_auxiliar": config_auxiliar_final,
        }

        # Construir y ejecutar grafo
        workflow = construir_grafo()
        app = workflow.compile()
        
        print("🚀 Usando nodo combinado (optimizado - 1 llamada GPT por batch)")

        recursion_limit = max(batches_esperados * 10, 100)
        config = RunnableConfig(recursion_limit=recursion_limit)

        print("\n🚀 Ejecutando grafo nuevo...\n")
        
        # Ejecutar en hilo separado para no bloquear el event loop
        import asyncio
        estado_final = await asyncio.to_thread(
            self._ejecutar_stream,
            app,
            estado_inicial,
            config,
            batches_esperados,
            len(respuestas_reales),
            batch_size,
            progress_callback
        )

        # Construir DataFrame de resultados
        df_resultados = self._construir_dataframe_resultados(
            estado_final,
            df,
            columna_id,
            nombre_pregunta
        )

        # Calcular estadísticas
        self._calcular_estadisticas(estado_final)

        return df_resultados

    def _cargar_catalogo(
        self,
        ruta_codigos: Optional[str]
    ) -> tuple[List[Dict[str, Any]], Dict[str, List[Dict[str, Any]]]]:
        """
        Carga el catálogo histórico desde un archivo Excel.
        
        Returns:
            Tupla con (catalogo_historico, catalogo_por_categoria)
        """
        catalogo_historico: List[Dict[str, Any]] = []
        catalogo_por_categoria: Dict[str, List[Dict[str, Any]]] = {}
        
        if not ruta_codigos:
            return catalogo_historico, catalogo_por_categoria
        
        df_cat = load_data(ruta_codigos)
        if "COD" not in df_cat.columns or "TEXTO" not in df_cat.columns:
            return catalogo_historico, catalogo_por_categoria
        
        categoria_actual = None
        
        for _, row in df_cat.iterrows():
            try:
                codigo = int(row["COD"])
            except Exception:
                continue
            desc = str(row["TEXTO"])
            
            # Detectar marcadores de categoría (COD >= 1000)
            if codigo >= 1000:
                categoria_detectada = detectar_categoria_desde_texto(desc)
                
                if categoria_detectada:
                    categoria_actual = categoria_detectada
                    if categoria_actual not in catalogo_por_categoria:
                        catalogo_por_categoria[categoria_actual] = []
                    print(f"   📂 Categoría detectada: {categoria_actual} (COD={codigo}, TEXTO={desc})")
                else:
                    # Inferir por rango de código
                    if codigo == 1000 or (codigo >= 1000 and codigo < 2000):
                        categoria_actual = "negativas"
                    elif codigo == 2000 or (codigo >= 2000 and codigo < 3000):
                        categoria_actual = "neutrales"
                    elif codigo == 3000 or codigo >= 3000:
                        categoria_actual = "positivas"
                    else:
                        categoria_actual = None
                        print(f"   ⚠️  No se pudo detectar categoría para COD={codigo}, TEXTO={desc}")
                        continue
                    
                    if categoria_actual:
                        if categoria_actual not in catalogo_por_categoria:
                            catalogo_por_categoria[categoria_actual] = []
                        print(f"   📂 Categoría inferida: {categoria_actual} (COD={codigo}, TEXTO={desc})")
            else:
                # Es un código normal
                codigo_item = {"codigo": codigo, "descripcion": desc}
                catalogo_historico.append(codigo_item)
                
                if categoria_actual:
                    catalogo_por_categoria[categoria_actual].append(codigo_item)
        
        # Mostrar resumen de categorías
        if catalogo_por_categoria:
            print(f"\n   📚 Catálogo agrupado por categorías:")
            for cat, codigos in catalogo_por_categoria.items():
                print(f"      - {cat}: {len(codigos)} códigos")
        
        return catalogo_historico, catalogo_por_categoria

    def _calcular_codigo_inicial(self, catalogo_historico: List[Dict[str, Any]]) -> int:
        """
        Calcula el código inicial para nuevos códigos basándose en el catálogo histórico.
        
        Returns:
            Código inicial para nuevos códigos
        """
        print(f"\n🔍 Diagnóstico de código inicial:")
        print(f"   📚 Total códigos en catálogo: {len(catalogo_historico)}")
        
        if not catalogo_historico:
            print(f"   ✅ No hay catálogo histórico, empezando desde 1")
            return 1
        
        todos_codigos = [
            c["codigo"] for c in catalogo_historico if isinstance(c["codigo"], int)
        ]
        print(f"   📚 Todos los códigos: {sorted(todos_codigos)}")
        
        # Excluir códigos especiales 90-98
        codigos_validos = [c for c in todos_codigos if not (90 <= c <= 98)]
        print(f"   📚 Códigos válidos (excluyendo 90-98): {sorted(codigos_validos) if codigos_validos else 'NINGUNO'}")
        
        if codigos_validos:
            max_codigo = max(codigos_validos)
            proximo_codigo_inicial = max_codigo + 1
            print(f"   ✅ Código máximo en catálogo: {max_codigo}")
            print(f"   ✅ Próximo código inicial: {proximo_codigo_inicial}")
            return proximo_codigo_inicial
        else:
            print(f"   ✅ No hay códigos válidos en catálogo, empezando desde 1")
            return 1

    def _ejecutar_stream(
        self,
        app,
        estado_inicial: EstadoCodificacion,
        config: RunnableConfig,
        total_batches: int,
        total_respuestas: int,
        batch_size: int,
        progress_callback=None
    ) -> EstadoCodificacion:
        """
        Ejecuta el stream del grafo en un hilo separado.
        
        Returns:
            Estado final del grafo
            
        Raises:
            Exception: Si ocurre un error durante la ejecución, se propaga con mensaje descriptivo
        """
        estado_resultado = estado_inicial
        
        try:
            for event in app.stream(estado_inicial, config=config):
                for node_name, node_state in event.items():
                    estado_resultado = node_state
                    
                    if progress_callback:
                        batch_actual = estado_resultado.get("batch_actual", 0)
                        
                        # Actualizar progreso según el nodo
                        if node_name == "preparar_batch":
                            respuestas_procesadas = batch_actual * batch_size
                            if total_respuestas > 0:
                                progreso = min(respuestas_procesadas / total_respuestas, 0.98)
                                mensaje = f"📦 Preparando batch {batch_actual + 1}/{total_batches}"
                                progress_callback(progreso, mensaje)
                        
                        elif node_name == "codificar_combinado":
                            respuestas_procesadas = batch_actual * batch_size
                            if total_respuestas > 0:
                                progreso = min((respuestas_procesadas + batch_size * 0.5) / total_respuestas, 0.98)
                                mensaje = f"🚀 Codificando batch {batch_actual + 1}/{total_batches}"
                                progress_callback(progreso, mensaje)
                        
                        elif node_name == "ensamblar":
                            respuestas_procesadas = batch_actual * batch_size
                            if total_respuestas > 0:
                                progreso = min((respuestas_procesadas + batch_size * 0.9) / total_respuestas, 0.98)
                                mensaje = f"🔧 Ensamblando resultados (batch {batch_actual + 1}/{total_batches})"
                                progress_callback(progreso, mensaje)
                        
                        elif node_name == "finalizar":
                            batch_actual_final = estado_resultado.get("batch_actual", 0)
                            if batch_actual_final >= total_batches:
                                progress_callback(1.0, "✅ Codificación completada")
                            else:
                                respuestas_procesadas = batch_actual_final * batch_size
                                if total_respuestas > 0:
                                    progreso = min(respuestas_procesadas / total_respuestas, 0.98)
                                mensaje = f"🔄 Batch {batch_actual_final}/{total_batches} completado, continuando..."
                                progress_callback(progreso, mensaje)
            
            return estado_resultado
        except Exception as e:
            # Mejorar el mensaje de error con contexto
            import traceback
            error_traceback = traceback.format_exc()
            print(f"❌ ERROR en _ejecutar_stream:")
            print(error_traceback)
            
            # Crear un mensaje de error más descriptivo
            mensaje_error = str(e)
            if not mensaje_error:
                mensaje_error = f"Error durante la ejecución del grafo: {type(e).__name__}"
            
            # Propagar el error con el mensaje mejorado
            raise RuntimeError(f"Error durante la codificación: {mensaje_error}") from e

    def _construir_dataframe_resultados(
        self,
        estado_final: EstadoCodificacion,
        df: pd.DataFrame,
        columna_id: str,
        nombre_pregunta: str
    ) -> pd.DataFrame:
        """
        Construye el DataFrame de resultados a partir del estado final.
        
        Returns:
            DataFrame con los resultados
        """
        decisiones: Dict[str, int] = {}
        for c in estado_final["codificaciones"]:
            dec = c["decision"]
            decisiones[dec] = decisiones.get(dec, 0) + 1
        print(f"\n📈 Decisiones: {decisiones}")

        # Mapeo fila_excel -> ID
        mapeo_id: Dict[int, Any] = {}
        for idx, row in df.iterrows():
            fila_excel = idx + 2
            id_valor = row[columna_id]
            if pd.isna(id_valor):
                id_valor = idx + 1
            mapeo_id[fila_excel] = id_valor

        datos_exportar: List[Dict[str, Any]] = []
        for cod in estado_final["codificaciones"]:
            fila_excel = cod["fila_excel"]
            id_valor = mapeo_id.get(fila_excel, fila_excel - 1)

            codigos_asignados: List[str] = []
            if cod["codigos_historicos"]:
                codigos_asignados.extend([str(c) for c in cod["codigos_historicos"]])
            if cod["codigos_nuevos"]:
                codigos_asignados.extend([str(n["codigo"]) for n in cod["codigos_nuevos"]])

            codigos_final = "; ".join(codigos_asignados) if codigos_asignados else ""

            datos_exportar.append({
                "ID": id_valor,
                nombre_pregunta: cod["texto"],
                "Códigos asignados": codigos_final,
            })

        return pd.DataFrame(datos_exportar)

    def _calcular_estadisticas(self, estado_final: EstadoCodificacion) -> None:
        """
        Calcula estadísticas de la ejecución y las guarda en self.stats.
        También construye el DataFrame de códigos nuevos.
        """
        # Construir catálogo de códigos nuevos
        codigos_nuevos_unicos: Dict[int, Dict[str, Any]] = {}
        for cod in estado_final["codificaciones"]:
            categoria_cod = cod.get("categoria")
            for nuevo in cod["codigos_nuevos"]:
                cid = nuevo["codigo"]
                desc = nuevo["descripcion"]
                cat_nuevo = nuevo.get("categoria", categoria_cod)

                if cid not in codigos_nuevos_unicos:
                    codigos_nuevos_unicos[cid] = {
                        "descripcion": desc,
                        "categoria": cat_nuevo,
                    }
                else:
                    if not codigos_nuevos_unicos[cid].get("categoria") and cat_nuevo:
                        codigos_nuevos_unicos[cid]["categoria"] = cat_nuevo

        # Ordenar por categoría y código
        orden_categoria = {"negativa": 0, "neutral": 1, "positiva": 2, None: 3}
        filas_catalogo = []
        for cid, data_cod in codigos_nuevos_unicos.items():
            cat = data_cod.get("categoria")
            filas_catalogo.append({
                "CATEGORIA": cat.capitalize() if isinstance(cat, str) else "",
                "COD": cid,
                "TEXTO": data_cod["descripcion"],
                "_orden_cat": orden_categoria.get(cat, 3),
            })

        df_catalogo_nuevos = pd.DataFrame(filas_catalogo)
        if not df_catalogo_nuevos.empty:
            df_catalogo_nuevos = df_catalogo_nuevos.sort_values(
                by=["_orden_cat", "COD"]
            ).drop(columns=["_orden_cat"])

        self.df_codigos_nuevos = df_catalogo_nuevos

        # Calcular estadísticas
        total_respuestas_codificadas = len(estado_final["codificaciones"])
        total_codigos_nuevos = len(df_catalogo_nuevos) if not df_catalogo_nuevos.empty else 0
        total_codigos_historicos = sum(
            len(c["codigos_historicos"]) for c in estado_final["codificaciones"]
        )
        prompt_tokens = estado_final.get("prompt_tokens", 0)
        completion_tokens = estado_final.get("completion_tokens", 0)
        total_tokens = estado_final.get("total_tokens", 0)
        costo_total = calcular_costo(prompt_tokens, completion_tokens, self.modelo)

        self.stats = {
            "total_respuestas_codificadas": total_respuestas_codificadas,
            "total_codigos_nuevos": total_codigos_nuevos,
            "total_codigos_historicos": total_codigos_historicos,
            "total_tokens": total_tokens,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "costo_total": costo_total,
        }

    def exportar_catalogo_nuevos(self, nombre_proyecto: str) -> Optional[str]:
        """
        Exporta el catálogo de códigos nuevos generado en la última ejecución.
        
        Args:
            nombre_proyecto: Nombre del proyecto para el archivo
            
        Returns:
            Ruta del archivo exportado o None si no hay códigos nuevos
        """
        df_catalogo_nuevos: Optional[pd.DataFrame] = getattr(
            self, "df_codigos_nuevos", None
        )
        if df_catalogo_nuevos is None or df_catalogo_nuevos.empty:
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta_salida = (
            Path("result/codigos_nuevos")
            / f"{nombre_proyecto}_codigos_nuevos_{timestamp}.xlsx"
        )
        ruta_salida.parent.mkdir(parents=True, exist_ok=True)
        save_data(df_catalogo_nuevos, str(ruta_salida))
        return str(ruta_salida)
