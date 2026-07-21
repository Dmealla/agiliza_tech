@echo off
TITLE AGILIZA TECH - Panel de Control Documental
:: Cambiar al directorio donde se encuentra este archivo .bat
cd /d "%~dp0"

:: Verificar si existe el entorno virtual e iniciarlo
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo [ADVERTENCIA] No se encontro la carpeta .venv local. Ejecutando con Python global...
)

:: Ejecutar la aplicacion principal
python app.py
pause