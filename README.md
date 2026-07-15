# Analizador de Saltos con Visión por Computadora

**Autor:** Santiago Vaccarini  
**Carrera:** Ciencia de Datos  
**Materia:** Programación 1  
**Repositorio:** https://github.com/santiagovaccarini-pixel/analizador-saltos-vision

## 1. Descripción

Aplicación de consola desarrollada en Python que procesa un video de un salto,
detecta 33 puntos corporales mediante **MediaPipe Pose Landmarker**, calcula
ángulos articulares aproximados y genera métricas, gráficos, un archivo Excel y
una conclusión técnica. El proyecto también incluye un modo de demostración
con datos simulados reproducibles.

El objetivo no es diagnosticar lesiones ni reemplazar instrumental de
laboratorio. Es una herramienta exploratoria de análisis cinemático 2D para
organizar información y facilitar la revisión del movimiento.

## 2. Funcionalidades

- Validación de existencia, extensión y tamaño del video.
- Descarga automática del modelo oficial de MediaPipe.
- Lectura frame a frame con OpenCV.
- Detección de pose y exportación de métricas por frame.
- Cálculo de ángulos de rodilla, cadera y tobillo.
- Estimación de preparación, ascenso, descenso y aterrizaje.
- Estimación del tiempo aéreo y desplazamiento vertical de cadera.
- Evaluación de calidad y visibilidad de la detección.
- Exportación a CSV, JSON y Excel.
- Generación de gráficos PNG y conclusión TXT.
- Video anotado con esqueleto corporal.
- Pruebas unitarias y modo demo sin video.

## 3. Estructura

```text
analizador-saltos-vision/
├── main.py
├── requirements.txt
├── README.md
├── src/
│   ├── biomechanics.py
│   ├── constants.py
│   ├── demo_data.py
│   ├── jump_analysis.py
│   ├── model_manager.py
│   ├── pose_detector.py
│   ├── reporting.py
│   └── validation.py
├── tests/
├── videos_entrada/
├── modelos/
├── resultados/
└── docs/
```

## 4. Requisitos

- Windows, Linux o macOS de 64 bits.
- **Python 3.12 recomendado.**
- Conexión a internet en el primer análisis real para descargar el modelo.

MediaPipe 0.10.35 publica compatibilidad declarada para Python 3.9 a 3.12. Por
ese motivo no se recomienda ejecutar este proyecto con Python 3.14.

## 5. Instalación en Windows

Opción automática:

```bat
instalar_windows.bat
```

Opción manual:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

El entorno `.venv` no se sube a GitHub. Se reconstruye con
`requirements.txt`, lo que evita mezclar dependencias entre proyectos.

## 6. Ejecución

### Demostración reproducible

```powershell
python main.py --demo --salida resultados_demo
```

### Video real

1. Copiar el archivo como `videos_entrada/salto.mp4`.
2. Ejecutar:

```powershell
python main.py --video videos_entrada/salto.mp4 --salida resultados
```

También se puede usar cualquier ruta:

```powershell
python main.py --video "C:\Videos\salto_01.mp4" --salida resultados\salto_01
```

## 7. Salidas

- `metricas_por_frame.csv`
- `resumen_salto.csv`
- `resumen_salto.json`
- `informe_salto.xlsx`
- `grafico_desplazamiento_cadera.png`
- `grafico_angulos_rodilla.png`
- `conclusion.txt`
- `video_anotado.mp4` cuando se procesa video real

## 8. Pruebas

```powershell
python -m unittest discover -s tests -v
```

Comprobaciones incluidas:

- ángulo recto de 90°;
- ángulo llano de 180°;
- manejo de vectores sin longitud;
- detección del salto simulado;
- rechazo de secuencias insuficientes.

## 9. Decisiones técnicas

- **Funciones pequeñas y módulos separados:** cada archivo tiene una
  responsabilidad concreta.
- **Importación diferida de MediaPipe:** el modo demo puede ejecutarse sin
  cargar dependencias de video.
- **`try/except` en el punto de entrada:** los errores se comunican con mensajes
  claros y códigos de salida.
- **CSV + JSON + Excel:** se ofrecen formatos legibles, interoperables y aptos
  para análisis posterior.
- **Datos simulados explícitos:** se evita presentar como real una medición que
  no proviene de un video.
- **Modelo fuera de Git:** reduce el tamaño del repositorio y mantiene una
  fuente oficial y reproducible.

## 10. Limitaciones

- Las coordenadas 2D dependen del ángulo de cámara y de la perspectiva.
- La fase aérea se estima con el centro de cadera; no mide contacto con el suelo.
- Las oclusiones, ropa amplia y poca iluminación reducen la calidad.
- Los ángulos no sustituyen un sistema multicámara ni una plataforma de fuerza.
- El programa no realiza diagnóstico médico ni predice lesiones.

## 11. Buen protocolo de filmación

- Cámara fija y perpendicular al plano principal del movimiento.
- Cuerpo completo visible durante todo el salto.
- Buena iluminación y fondo con contraste.
- Evitar zoom digital y movimiento de cámara.
- Grabar a 60 FPS o más cuando sea posible.

## 12. Fuentes principales

- Python Software Foundation. PEP 8 y PEP 257.
- Python Documentation. `venv`.
- Google AI Edge. MediaPipe Pose Landmarker para Python.
- OpenCV Documentation. `VideoCapture`.
- NumPy, pandas, Matplotlib y openpyxl: documentación oficial.

## 13. Uso de herramientas de IA

Durante el desarrollo usé ChatGPT para consultar dudas puntuales sobre la
organización del proyecto, compatibilidad de librerías y preparación de pruebas.
No tomé las respuestas como válidas automáticamente: contrasté las APIs con
documentación oficial, ejecuté las pruebas unitarias y revisé los archivos
generados. Las decisiones de alcance y la explicación del código quedan bajo mi
responsabilidad.
