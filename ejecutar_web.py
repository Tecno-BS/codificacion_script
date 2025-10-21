#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para ejecutar la interfaz web de Streamlit
Sistema de Codificación Híbrida v0.5
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Ejecutar aplicación Streamlit"""
    
    print("=" * 70)
    print("SISTEMA DE CODIFICACIÓN HÍBRIDA v0.5 - INTERFAZ WEB")
    print("=" * 70)
    print()
    print("Iniciando servidor Streamlit...")
    print()
    print("La interfaz se abrirá automáticamente en tu navegador")
    print("URL: http://localhost:8501")
    print()
    print("Para detener el servidor: Ctrl+C")
    print("=" * 70)
    print()
    
    # Ruta al archivo de la app
    app_path = Path(__file__).parent / "web" / "app.py"
    
    # Ejecutar streamlit
    try:
        subprocess.run([
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(app_path),
            "--server.port=8501",
            "--browser.gatherUsageStats=false"
        ])
    except KeyboardInterrupt:
        print("\n\nServidor detenido por el usuario")
    except Exception as e:
        print(f"\nError al iniciar Streamlit: {e}")
        print("\nAsegúrate de tener Streamlit instalado:")
        print("  pip install streamlit")


if __name__ == "__main__":
    main()

