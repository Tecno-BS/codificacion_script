import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Tuple
import os
from pathlib import Path

from .config import *
from .utils import load_data


class EvaluadorCodificacion:
    def __init__(self):
        self.resultados = None
        self.metricas = {}
        self.metricas_por_pregunta = {}  # Métricas por cada pregunta
        self.graficos_generados = []
        self.preguntas_procesadas = []  # Lista de preguntas encontradas

    def identificar_preguntas(self) -> List[str]:
        """
        Identifica las preguntas procesadas en los resultados
        """
        if self.resultados is None:
            return []
        
        preguntas = []
        
        # Buscar columnas que terminan en _codigo
        for col in self.resultados.columns:
            if col.endswith('_codigo'):
                pregunta = col.replace('_codigo', '')
                preguntas.append(pregunta)
        
        self.preguntas_procesadas = preguntas
        return preguntas

    def cargar_resultados(self, ruta_resultados: str) -> bool:
        try:
            self.resultados = load_data(ruta_resultados)
            print(f"Resultados cargados: {len(self.resultados)} registros")
            return True
        except Exception as e:
            print(f"Error al cargar resultados: {e}")
            return False
    
    def calcular_metricas_basicas(self) -> Dict[str, float]:
        if self.resultados is None:
            raise ValueError("Debe cargar resultados primero")

        # Identificar preguntas
        preguntas = self.identificar_preguntas()
        
        metricas = {}
        metricas['total_respuestas'] = len(self.resultados)
        metricas['preguntas_procesadas'] = len(preguntas)
        metricas['preguntas'] = preguntas

        # Métricas consolidadas de todas las preguntas
        total_codificadas = 0
        total_revisar = 0
        total_similitudes = []

        for pregunta in preguntas:
            col_codigo = f'{pregunta}_codigo'
            col_similitud = f'{pregunta}_similitud'
            
            if col_codigo in self.resultados.columns:
                # Respuestas con código asignado
                codificadas = self.resultados[self.resultados[col_codigo].notna()]
                total_codificadas += len(codificadas)
                
                # Respuestas que requieren revisión
                revisar = self.resultados[self.resultados[col_codigo] == 'REVISAR']
                total_revisar += len(revisar)
                
                # Similitudes
                if col_similitud in self.resultados.columns:
                    similitudes = self.resultados[col_similitud].dropna()
                    total_similitudes.extend(similitudes.tolist())

        # Métricas consolidadas
        metricas['respuestas_codificadas'] = total_codificadas
        metricas['porcentaje_codificadas'] = (total_codificadas / len(self.resultados)) * 100 if len(self.resultados) > 0 else 0
        
        metricas['respuestas_revisar'] = total_revisar
        metricas['porcentaje_revisar'] = (total_revisar / len(self.resultados)) * 100 if len(self.resultados) > 0 else 0

        # Similitudes consolidadas
        if total_similitudes:
            metricas['similitud_promedio'] = np.mean(total_similitudes)
            metricas['similitud_minima'] = np.min(total_similitudes)
            metricas['similitud_maxima'] = np.max(total_similitudes)
            metricas['similitud_mediana'] = np.median(total_similitudes)

        # Calcular métricas por pregunta
        self.metricas_por_pregunta = {}
        for pregunta in preguntas:
            self.metricas_por_pregunta[pregunta] = self._calcular_metricas_pregunta(pregunta)

        self.metricas = metricas
        return metricas

    def _calcular_metricas_pregunta(self, pregunta: str) -> Dict[str, float]:
        """
        Calcula métricas para una pregunta específica
        """
        col_codigo = f'{pregunta}_codigo'
        col_similitud = f'{pregunta}_similitud'
        
        if col_codigo not in self.resultados.columns:
            return {}
        
        metricas = {}
        
        # Respuestas válidas para esta pregunta
        respuestas_validas = self.resultados[self.resultados[col_codigo].notna()]
        metricas['total_respuestas'] = len(respuestas_validas)
        
        # Respuestas codificadas vs revisar
        codificadas = respuestas_validas[respuestas_validas[col_codigo] != 'REVISAR']
        revisar = respuestas_validas[respuestas_validas[col_codigo] == 'REVISAR']
        
        metricas['respuestas_codificadas'] = len(codificadas)
        metricas['respuestas_revisar'] = len(revisar)
        metricas['porcentaje_codificadas'] = (len(codificadas) / len(respuestas_validas)) * 100 if len(respuestas_validas) > 0 else 0
        
        # Distribución de códigos
        if len(codificadas) > 0:
            codigos_dist = codificadas[col_codigo].value_counts()
            metricas['codigos_unicos'] = len(codigos_dist)
            metricas['codigo_mas_frecuente'] = codigos_dist.index[0] if len(codigos_dist) > 0 else None
            metricas['frecuencia_codigo_mas_frecuente'] = codigos_dist.iloc[0] if len(codigos_dist) > 0 else 0
        
        # Similitudes
        if col_similitud in self.resultados.columns:
            similitudes = respuestas_validas[col_similitud].dropna()
            if len(similitudes) > 0:
                metricas['similitud_promedio'] = similitudes.mean()
                metricas['similitud_minima'] = similitudes.min()
                metricas['similitud_maxima'] = similitudes.max()
                metricas['similitud_mediana'] = similitudes.median()
        
        return metricas

    def analizar_distribucion_codigos(self) -> Dict[str, pd.DataFrame]:
        if self.resultados is None:
            raise ValueError("Debe cargar resultados primero")
        
        preguntas = self.identificar_preguntas()
        distribuciones = {}
        
        for pregunta in preguntas:
            col_codigo = f'{pregunta}_codigo'
            
            if col_codigo not in self.resultados.columns:
                continue
                
            # Filtrar códigos válidos
            codigos_validos = self.resultados[
                (self.resultados[col_codigo].notna()) & 
                (self.resultados[col_codigo] != 'REVISAR')
            ]
            
            if len(codigos_validos) == 0:
                distribuciones[pregunta] = pd.DataFrame()
                continue
            
            # Calcular distribución
            distribucion = codigos_validos[col_codigo].value_counts().reset_index()
            distribucion.columns = ['codigo', 'frecuencia']
            distribucion['porcentaje'] = (distribucion['frecuencia'] / len(codigos_validos)) * 100
            distribucion['porcentaje_acumulado'] = distribucion['porcentaje'].cumsum()
            
            distribuciones[pregunta] = distribucion
        
        return distribuciones
    
    def generar_grafico_distribucion(self, ruta_salida: str = None) -> str:
        if self.resultados is None:
            raise ValueError("Debe cargar resultados primero")
        
        preguntas = self.identificar_preguntas()
        
        if not preguntas:
            print("No hay preguntas para graficar")
            return ""
        
        # Calcular número de filas y columnas para subplots
        n_preguntas = len(preguntas)
        n_cols = min(2, n_preguntas)
        n_rows = (n_preguntas + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 6 * n_rows))
        if n_preguntas == 1:
            axes = [axes]
        elif n_rows == 1:
            axes = axes.reshape(1, -1)
        
        plt.style.use('default')
        sns.set_palette("husl")
        
        for i, pregunta in enumerate(preguntas):
            row = i // n_cols
            col = i % n_cols
            ax = axes[row, col] if n_rows > 1 else axes[col]
            
            col_codigo = f'{pregunta}_codigo'
            
            if col_codigo in self.resultados.columns:
                codigos_validos = self.resultados[
                    (self.resultados[col_codigo].notna()) & 
                    (self.resultados[col_codigo] != 'REVISAR')
                ]
                
                if len(codigos_validos) > 0:
                    top_codigos = codigos_validos[col_codigo].value_counts().head(10)
                    top_codigos.plot(kind='bar', ax=ax, color='skyblue')
                    ax.set_title(f'Top 10 Códigos - {pregunta}')
                    ax.set_xlabel('Código')
                    ax.set_ylabel('Frecuencia')
                    ax.tick_params(axis='x', rotation=45)
                else:
                    ax.text(0.5, 0.5, f'No hay códigos válidos\npara {pregunta}', 
                        ha='center', va='center', transform=ax.transAxes)
                    ax.set_title(f'{pregunta} - Sin datos')
        
        # Ocultar subplots vacíos
        for i in range(n_preguntas, n_rows * n_cols):
            row = i // n_cols
            col = i % n_cols
            if n_rows > 1:
                axes[row, col].set_visible(False)
            else:
                axes[col].set_visible(False)
        
        plt.tight_layout()
        
        if ruta_salida is None:
            ruta_salida = os.path.join(RUTA_RESULTADOS, 'metricas', 'distribucion_codigos_multi.png')
        
        os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
        plt.savefig(ruta_salida, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.graficos_generados.append(ruta_salida)
        return ruta_salida

    def generar_reporte_completo(self, ruta_salida: str = None) -> str:
        if self.resultados is None:
            raise ValueError("Debe cargar resultados primero")
        
        metricas = self.calcular_metricas_basicas()
        distribuciones = self.analizar_distribucion_codigos()
        ruta_grafico = self.generar_grafico_distribucion()
        
        reporte = []
        reporte.append("=== REPORTE DE CODIFICACIÓN MULTI-PREGUNTA ===")
        reporte.append(f"Fecha: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Métricas generales
        reporte.append("## MÉTRICAS GENERALES\n")
        for metrica, valor in metricas.items():
            if metrica not in ['preguntas']:  # Excluir lista de preguntas
                if isinstance(valor, float):
                    reporte.append(f"- **{metrica}**: {valor:.2f}")
                else:
                    reporte.append(f"- **{metrica}**: {valor}")
        
        # Métricas por pregunta
        reporte.append("\n## MÉTRICAS POR PREGUNTA\n")
        for pregunta, metricas_pregunta in self.metricas_por_pregunta.items():
            reporte.append(f"### {pregunta}\n")
            for metrica, valor in metricas_pregunta.items():
                if isinstance(valor, float):
                    reporte.append(f"- **{metrica}**: {valor:.2f}")
                else:
                    reporte.append(f"- **{metrica}**: {valor}")
            reporte.append("")
        
        # Distribuciones por pregunta
        reporte.append("## DISTRIBUCIONES DE CÓDIGOS POR PREGUNTA\n")
        for pregunta, distribucion in distribuciones.items():
            reporte.append(f"### {pregunta}\n")
            if not distribucion.empty:
                reporte.append(distribucion.to_string(index=False))
            else:
                reporte.append("No hay códigos válidos para analizar")
            reporte.append("")
        
        # Gráficos
        reporte.append("## GRÁFICOS GENERADOS\n")
        reporte.append(f"- Distribución de códigos multi-pregunta: {ruta_grafico}")
        
        # Guardar reporte
        if ruta_salida is None:
            ruta_salida = os.path.join(RUTA_RESULTADOS, 'metricas', 'reporte_evaluacion_multi.txt')
        
        os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
        
        with open(ruta_salida, 'w', encoding='utf-8') as f:
            f.write('\n'.join(reporte))
        
        print(f"Reporte multi-pregunta generado en: {ruta_salida}")
        return ruta_salida

    def generar_reporte_por_pregunta(self, pregunta: str, ruta_salida: str = None) -> str:
        """
        Genera reporte específico para una pregunta
        """
        if self.resultados is None:
            raise ValueError("Debe cargar resultados primero")
        
        if pregunta not in self.metricas_por_pregunta:
            raise ValueError(f"Pregunta {pregunta} no encontrada")
        
        metricas_pregunta = self.metricas_por_pregunta[pregunta]
        distribuciones = self.analizar_distribucion_codigos()
        distribucion = distribuciones.get(pregunta, pd.DataFrame())
        
        reporte = []
        reporte.append(f"=== REPORTE DE CODIFICACIÓN - {pregunta} ===")
        reporte.append(f"Fecha: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Métricas de la pregunta
        reporte.append("## MÉTRICAS\n")
        for metrica, valor in metricas_pregunta.items():
            if isinstance(valor, float):
                reporte.append(f"- **{metrica}**: {valor:.2f}")
            else:
                reporte.append(f"- **{metrica}**: {valor}")
        
        # Distribución de códigos
        reporte.append("\n## DISTRIBUCIÓN DE CÓDIGOS\n")
        if not distribucion.empty:
            reporte.append(distribucion.to_string(index=False))
        else:
            reporte.append("No hay códigos válidos para analizar")
        
        # Guardar reporte
        if ruta_salida is None:
            ruta_salida = os.path.join(RUTA_RESULTADOS, 'metricas', f'reporte_{pregunta}.txt')
        
        os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
        
        with open(ruta_salida, 'w', encoding='utf-8') as f:
            f.write('\n'.join(reporte))
        
        print(f"Reporte de {pregunta} generado en: {ruta_salida}")
        return ruta_salida


    def comparar_con_sistema_anterior(self, ruta_sistema_anterior: str) -> Dict[str, float]:
        try: 
            resultados_anterior = load_data(ruta_sistema_anterior)

            metricas_actual = self.calcular_metricas_basicas()

            metricas_anterior = {}
            metricas_anterior['total_respuestas'] = len(resultados_anterior)

            if 'codigo_asignado' in resultados_anterior.columns:
                codigos_anterior = resultados_anterior['codigo_asignado'].value_counts()
                metricas_anterior['codigos_unicos'] = len(codigos_anterior)
                metricas_anterior['codigo_mas_frecuente'] = codigos_anterior.index[0] if len(codigos_anterior) > 0 else None
            
            comparacion = {}

            for metrica in metricas_actual:
                if metrica in metricas_anterior:
                    if isinstance(metricas_actual[metrica], (int, float)) and isinstance(metricas_anterior[metrica], (int, float)):
                        comparacion[f'{metrica}_mejora'] = metricas_actual[metrica] - metricas_anterior[metrica]
                        comparacion[f'{metrica}_porcentaje_mejora'] = ((metricas_actual[metrica] - metricas_anterior[metrica]) / metricas_anterior[metrica]) * 100
            
            return comparacion

        except Exception as e:
            print(f"Error al comparar con sistema anterior: {e}")
            return {}
            

