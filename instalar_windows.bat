@echo off
setlocal

py -3.13 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON=py -3.13
) else (
    py -3.12 --version >nul 2>&1
    if errorlevel 1 (
        echo ERROR: se requiere Python 3.12 o 3.13 de 64 bits.
        pause
        exit /b 1
    )
    set PYTHON=py -3.12
)

%PYTHON% -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo Instalacion finalizada.
echo Ejecute: ejecutar_demo.bat
pause
