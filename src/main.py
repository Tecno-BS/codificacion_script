import argparse
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict

from config import *
from codificador import SemanticCoder
from evaluador import EvaluadorCodificacion
from utils import verify_codes 

def configurar_argumentos():
    parser = argparse.ArgumentParser(
        description="Sistema de Codificación Semántica Multi-Pregunta",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python -m src.main --respuestas data/raw/respuestas.xlsx
  python -m src.main --respuestas data/raw/respuestas.xlsx --codigos data/raw/codigos_anteriores.xlsx
  python -m src.main --respuestas data/raw/respuestas.xlsx --evaluar
  python -m src.main --respuestas data/raw/respuestas.xlsx --codigos data/raw/codigos_anteriores.xlsx --evaluar
        """
    )

    # Argumentos requeridos
    parser.add_argument('--respuestas', required=True, help="Ruta al archivo de respuestas (Excel o CSV)")
    
    # Argumentos opcionales
    parser.add_argument('--codigos', help="Ruta al archivo de códigos anteriores (opcional)")
    parser.add_argument('--salida', help="Ruta de salida para los resultados (opcional)")
    parser.add_argument('--evaluar', action='store_true', help="Ejecutar evaluación de resultados")
    parser.add_argument('--comparar', help="Ruta a resultados del sistema anterior para comparar")
    parser.add_argument('--umbral', type=float, default=UMBRAL_SIMILITUD, help=f"Umbral de similitud (default: {UMBRAL_SIMILITUD})")
    parser.add_argument('--top-candidatos', type=int, default=TOP_CANDIDATOS, help=f"Número de códigos candidatos (default: {TOP_CANDIDATOS})")
    
    # Nuevos argumentos para multi-pregunta
    parser.add_argument('--mostrar-mapeo', action='store_true', help="Mostrar mapeo de columnas con preguntas")
    parser.add_argument('--preguntas-especificas', nargs='+', help="Lista de preguntas específicas a procesar (ej: P1A P2A P5AC)")

    return parser

def crear_ruta_salida(respuestas_path: str, codigos_path: str = None) -> Dict[str, str]:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = Path(respuestas_path).stem

    rutas = {
        'resultados': os.path.join(RUTA_RESULTADOS, 'codificaciones', f'{base_name}_{timestamp}.xlsx'),
        'metricas': os.path.join(RUTA_RESULTADOS, 'metricas', f'{base_name}_{timestamp}'),
        'graficos': os.path.join(RUTA_RESULTADOS, 'metricas', f'{base_name}_{timestamp}')
    }

    # Crear directorios si no existen
    for ruta in rutas.values():
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
    
    return rutas

def ejecutar_codificacion(args) -> str:
    print("=== SISTEMA DE CODIFICACIÓN SEMÁNTICA MULTI-PREGUNTA ===")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Respuestas: {args.respuestas}")
    print(f"Códigos: {args.codigos if args.codigos else 'No especificados'}")
    print(f"Umbral similitud: {args.umbral}")
    print(f"Top candidatos: {args.top_candidatos}")
    
    if args.preguntas_especificas:
        print(f"Preguntas específicas: {args.preguntas_especificas}")
    
    print()

    # Crear rutas de salida
    rutas = crear_ruta_salida(args.respuestas, args.codigos)

    # Inicializar codificador
    codificador = SemanticCoder()

    # Actualizar configuración si se especificaron parámetros
    if args.umbral != UMBRAL_SIMILITUD:
        print(f"⚠️  Usando umbral personalizado: {args.umbral}")
    
    if args.top_candidatos != TOP_CANDIDATOS:
        print(f"⚠️  Usando top candidatos personalizado: {args.top_candidatos}")

    try:
        # Ejecutar codificación
        print("🚀 Iniciando proceso de codificación multi-pregunta...")
        resultados = codificador.ejecutar_codificacion(
            ruta_respuestas=args.respuestas,
            ruta_codigos=args.codigos
        )
        
        # Mostrar mapeo si se solicitó
        if args.mostrar_mapeo and hasattr(codificador, 'mapeo_columnas'):
            print("\n📋 Mapeo de columnas con preguntas:")
            for columna, pregunta in codificador.mapeo_columnas.items():
                print(f"  - {columna} → {pregunta}")
        
        # Guardar resultados
        ruta_resultados = rutas['resultados']
        codificador.guardar_resultados(resultados, ruta_resultados)
        
        print(f"✅ Codificación completada")
        print(f"📁 Resultados guardados en: {ruta_resultados}")
        
        return ruta_resultados
        
    except Exception as e:
        print(f"❌ Error durante la codificación: {e}")
        sys.exit(1)
    
def ejecutar_evaluacion(ruta_resultados: str, ruta_comparacion: str = None) -> None:
    print("\n=== EVALUACIÓN DE RESULTADOS MULTI-PREGUNTA ===")
    
    # Inicializar evaluador
    evaluador = EvaluadorCodificacion()
    
    try:
        # Cargar resultados
        if not evaluador.cargar_resultados(ruta_resultados):
            print("❌ Error al cargar resultados para evaluación")
            return
        
        # Generar reporte completo
        print("📊 Generando reporte de evaluación...")
        ruta_reporte = evaluador.generar_reporte_completo()
        
        print(f"✅ Evaluación completada")
        print(f"📁 Reporte guardado en: {ruta_reporte}")
        
        # Comparar con sistema anterior si se especificó
        if ruta_comparacion:
            print("\n�� Comparando con sistema anterior...")
            comparacion = evaluador.comparar_con_sistema_anterior(ruta_comparacion)
            
            if comparacion:
                print("📈 Métricas de comparación:")
                for metrica, valor in comparacion.items():
                    if isinstance(valor, float):
                        print(f"  - {metrica}: {valor:.2f}")
                    else:
                        print(f"  - {metrica}: {valor}")
            else:
                print("⚠️  No se pudo realizar la comparación")
        
    except Exception as e:
        print(f"❌ Error durante la evaluación: {e}")

def main():
    """
    Función principal del programa
    """
    # Configurar argumentos
    parser = configurar_argumentos()
    args = parser.parse_args()
    
    # Verificar que existe el archivo de respuestas
    if not os.path.exists(args.respuestas):
        print(f"❌ Error: Archivo de respuestas no encontrado: {args.respuestas}")
        sys.exit(1)
    
    # Verificar que existe el archivo de códigos (si se especificó)
    if args.codigos and not os.path.exists(args.codigos):
        print(f"❌ Error: Archivo de códigos no encontrado: {args.codigos}")
        sys.exit(1)
    
    # Ejecutar codificación
    ruta_resultados = ejecutar_codificacion(args)
    
    # Ejecutar evaluación si se solicitó
    if args.evaluar:
        ejecutar_evaluacion(ruta_resultados, args.comparar)
    
    # Exportar catálogo de códigos nuevos consolidado
    print("\n📦 Exportando catálogo de códigos nuevos...")
    codificador = SemanticCoder()
    ruta_catalogo = codificador.exportar_catalogo_nuevos_consolidado()
    
    if ruta_catalogo:
        print(f"✅ Catálogo de códigos nuevos: {ruta_catalogo}")
    
    print("\n✅ Proceso completado exitosamente!")
    print(f"📁 Resultados disponibles en: {ruta_resultados}")



if __name__ == "__main__":
    main()



