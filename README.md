# Analizador de Saltos con Visión por Computadora

**Autor:** Santiago Vaccarini  
**Carrera:** Ciencia de Datos  
**Materia:** Programación 1

Aplicación de consola en Python que analiza videos de saltos mediante MediaPipe Pose Landmarker, calcula ángulos articulares aproximados y genera métricas, gráficos y reportes. Incluye un modo de demostración reproducible sin video.

## Instalación

Se recomienda Python 3.12.

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecución

```bash
python main.py --demo --salida resultados_demo
python main.py --video videos_entrada/salto.mp4 --salida resultados
```

## Pruebas

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

El proyecto utiliza módulos propios, docstrings PEP 257, organización modular, manejo de errores, archivos de entrada/salida y dependencias declaradas.