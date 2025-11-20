@echo off
echo ========================================
echo  Iniciando Jupyter Lab
echo  Sistema de Codificacion Automatizada
echo ========================================
echo.

REM Activar entorno virtual
echo [1/3] Activando entorno virtual...
call ..\codificacion_env\Scripts\activate.bat

REM Verificar instalacion
echo [2/3] Verificando dependencias...
python -c "import langgraph" 2>nul
if errorlevel 1 (
    echo.
    echo [!] LangGraph no esta instalado.
    echo     Instalando dependencias...
    pip install langchain langchain-openai langgraph jupyter ipython
)

REM Lanzar Jupyter Lab
echo [3/3] Lanzando Jupyter Lab...
echo.
echo ========================================
echo  Jupyter Lab se abrira en tu navegador
echo  Presiona Ctrl+C para detener
echo ========================================
echo.

jupyter lab

pause


