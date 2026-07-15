# Analizador de Saltos con Visión por Computadora

**Autor:** Santiago Vaccarini  
**Carrera:** Ciencia de Datos  
**Materia:** Programación 1

## Descripción

Desarrollé una aplicación de consola en Python que analiza videos de saltos. El
programa detecta puntos corporales con un modelo MediaPipe Pose, calcula métricas
cinemáticas 2D y genera reportes en CSV, JSON, Excel, PNG y TXT.

No es una herramienta médica ni reemplaza instrumental de laboratorio. Su
objetivo es organizar información y facilitar una revisión inicial del movimiento.

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

## Estructura

```text
├── main.py
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
├── resultados_demo/
├── resultados_video_real/
└── docs/
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

El ZIP de entrega incluye el modelo. Cuando se clona solamente el repositorio,
el programa intenta descargarlo automáticamente si todavía no está disponible.

## Ejecución

Modo demo:

```powershell
python main.py --demo --salida resultados_demo
```

Video real:

```powershell
python main.py --video videos_entrada/salto.mp4 --salida resultados
```

## Pruebas

```powershell
python -m unittest discover -s tests -v
```

Las cinco pruebas verifican cálculos geométricos, manejo de vectores inválidos,
detección del salto simulado y rechazo de secuencias insuficientes.

## Validación real

Probé el programa con un video de 10,51 segundos, resolución 1920 × 1080 y
119,88 FPS. Se procesaron los 1.260 frames con estos resultados:

- tasa de detección: 100 %;
- calidad media de landmarks: 96,37 %;
- despegue estimado: 6,431 s;
- punto más alto estimado: 6,740 s;
- aterrizaje estimado: 6,823 s;
- tiempo aéreo aproximado: 0,392 s.

La evidencia resumida está en `resultados_video_real`. El video original no se
publica para proteger la privacidad de la persona filmada.

## Limitaciones

- El análisis es 2D y depende del ángulo de cámara.
- Una vista frontal no representa bien la flexión sagital de rodilla.
- El tiempo aéreo se estima con la trayectoria de la cadera.
- El sistema no diagnostica lesiones ni predice rendimiento futuro.

## Uso de inteligencia artificial

Usé ChatGPT para consultar dudas puntuales sobre organización, compatibilidad y
pruebas. Verifiqué las propuestas ejecutando el programa, comparando los
resultados con el video y revisando documentación oficial. Las decisiones finales
y la explicación del código quedan bajo mi responsabilidad.
