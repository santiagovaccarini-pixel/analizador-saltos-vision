@echo off
call .venv\Scripts\activate
set /p VIDEO=Ruta completa del video: 
python main.py --video "%VIDEO%" --salida resultados
pause
