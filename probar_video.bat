@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Preparando entorno virtual...
    py -3.13 --version >nul 2>&1
    if not errorlevel 1 (
        set PYTHON=py -3.13
    ) else (
        set PYTHON=py -3.12
    )
    %PYTHON% -m venv .venv
    if errorlevel 1 goto :error
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 goto :error
)

echo Reconstruyendo video de ejemplo...
".venv\Scripts\python.exe" preparar_video_ejemplo.py
if errorlevel 1 goto :error

echo Ejecutando analisis...
if exist "resultados_prueba" rmdir /s /q "resultados_prueba"
".venv\Scripts\python.exe" main.py --video "videos_entrada\salto_ejemplo.mp4" --salida "resultados_prueba"
if errorlevel 1 goto :error

echo.
echo Prueba finalizada correctamente.
echo Los resultados se encuentran en resultados_prueba.
start "" "resultados_prueba\video_anotado.mp4"
start "" "resultados_prueba"
pause
exit /b 0

:error
echo.
echo La prueba termino con errores. Revise los mensajes anteriores.
pause
exit /b 1
