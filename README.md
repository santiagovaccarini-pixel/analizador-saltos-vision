# Analizador de Saltos con Visión por Computadora

**Autor:** Santiago Vaccarini  
**Carrera:** Ciencia de Datos  
**Materia:** Programación 1

## Descripción

Desarrollé una aplicación de consola en Python que analiza videos de saltos. El programa detecta puntos corporales con un modelo MediaPipe Pose, calcula métricas cinemáticas 2D y genera reportes en CSV, JSON, Excel, PNG y TXT.

No es una herramienta médica ni reemplaza instrumental de laboratorio. Su objetivo es organizar información y facilitar una revisión inicial del movimiento.

## Funcionalidades

- Validación del archivo de video.
- Lectura frame a frame con OpenCV.
- Inferencia de pose con LiteRT y un modelo TFLite preentrenado.
- Extracción de 33 puntos corporales.
- Cálculo aproximado de ángulos de rodilla, cadera y tobillo.
- Detección de preparación, despegue, vuelo y aterrizaje.
- Estimación del tiempo aéreo y del desplazamiento vertical de la cadera.
- Evaluación de calidad de la detección.
- Exportación de resultados y video anotado.
- Modo demo reproducible y pruebas unitarias.
- Video de ejemplo autorizado para probar el flujo completo.

## Estructura principal

```text
├── main.py
├── preparar_video_ejemplo.py
├── probar_video.bat
├── requirements.txt
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
├── modelos/
├── videos_entrada/
│   └── video_ejemplo_base64/
├── resultados_demo/
├── resultados_video_real/
└── docs/
    ├── README.md
    ├── INFORME_FINAL.md
    └── REFERENCIAS.md
```

## Instalación

Se recomienda Python 3.12 o 3.13.

```powershell
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

En Windows también se puede ejecutar `instalar_windows.bat`.

El ZIP de entrega incluye el modelo. Cuando se clona solamente el repositorio, el programa intenta descargarlo automáticamente si todavía no está disponible.

## Prueba completa con el video incluido

En Windows, el método más directo es ejecutar:

```text
probar_video.bat
```

Este archivo realiza automáticamente el siguiente proceso:

1. Crea el entorno virtual si todavía no existe.
2. Instala las dependencias necesarias.
3. Reconstruye el video de ejemplo autorizado desde sus fragmentos Base64.
4. Ejecuta el análisis completo.
5. Guarda los resultados en `resultados_prueba`.
6. Abre el video anotado y la carpeta de resultados.

El video se guarda reconstruido como:

```text
videos_entrada/salto_ejemplo.mp4
```

La versión publicada fue optimizada para respetar los límites de tamaño de GitHub, pero conserva el salto utilizado para comprobar el funcionamiento del programa.

## Ejecución manual

Modo demo:

```powershell
python main.py --demo --salida resultados_demo
```

Video incluido:

```powershell
python preparar_video_ejemplo.py
python main.py --video videos_entrada/salto_ejemplo.mp4 --salida resultados_prueba
```

Otro video:

```powershell
python main.py --video "C:\Videos\salto.mp4" --salida resultados
```

## Archivos generados

El análisis produce, según la configuración:

- `metricas_por_frame.csv`
- `resumen_salto.csv`
- `resumen_salto.json`
- `informe_salto.xlsx`
- gráficos PNG
- `conclusion.txt`
- `video_anotado.mp4`

## Pruebas unitarias

```powershell
python -m unittest discover -s tests -v
```

Las cinco pruebas verifican cálculos geométricos, manejo de vectores inválidos, detección del salto simulado y rechazo de secuencias insuficientes.

## Validación real

Probé el programa con el video original de 10,51 segundos, resolución 1920 × 1080 y 119,88 FPS. Se procesaron los 1.260 frames con estos resultados:

- tasa de detección: 100 %;
- calidad media de landmarks: 96,37 %;
- despegue estimado: 6,431 s;
- punto más alto estimado: 6,740 s;
- aterrizaje estimado: 6,823 s;
- tiempo aéreo aproximado: 0,392 s.

Además, ejecuté el flujo con la copia optimizada incluida en GitHub. El sistema reconstruyó el video, procesó los frames y generó correctamente el video anotado y los reportes.

## Limitaciones

- El análisis es 2D y depende del ángulo de cámara.
- Una vista frontal no representa bien la flexión sagital de rodilla.
- El tiempo aéreo se estima con la trayectoria de la cadera.
- La calidad depende de la iluminación, la visibilidad corporal y la estabilidad de la cámara.
- El sistema no diagnostica lesiones ni predice rendimiento futuro.

## Uso de inteligencia artificial

Usé ChatGPT para consultar dudas puntuales sobre organización, compatibilidad y pruebas. Verifiqué las propuestas ejecutando el programa, comparando los resultados con el video y revisando documentación oficial. Las decisiones finales y la explicación del código quedan bajo mi responsabilidad.
