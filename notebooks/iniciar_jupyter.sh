#!/bin/bash

echo "========================================"
echo " Iniciando Jupyter Lab"
echo " Sistema de Codificación Automatizada"
echo "========================================"
echo ""

# Activar entorno virtual
echo "[1/3] Activando entorno virtual..."
source ../codificacion_env/bin/activate

# Verificar instalación
echo "[2/3] Verificando dependencias..."
python -c "import langgraph" 2>/dev/null
if [ $? -ne 0 ]; then
    echo ""
    echo "[!] LangGraph no está instalado."
    echo "    Instalando dependencias..."
    pip install langchain langchain-openai langgraph jupyter ipython
fi

# Lanzar Jupyter Lab
echo "[3/3] Lanzando Jupyter Lab..."
echo ""
echo "========================================"
echo " Jupyter Lab se abrirá en tu navegador"
echo " Presiona Ctrl+C para detener"
echo "========================================"
echo ""

jupyter lab


