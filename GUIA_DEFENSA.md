# Guía breve para la defensa oral

## Presentación en 60 segundos

El proyecto es un analizador de saltos en Python. Recibe un video, usa OpenCV
para leerlo y MediaPipe Pose Landmarker para detectar 33 puntos corporales.
Con esos puntos calcula ángulos de rodilla, cadera y tobillo, estima fases del
salto y genera CSV, JSON, Excel, gráficos y un video anotado. El código está
separado en módulos, tiene docstrings, validaciones, manejo de errores y pruebas.
También incorpora un modo demo reproducible para verificar el pipeline sin
necesitar un video.

## Preguntas probables

### ¿Por qué usaste funciones y módulos?
Para separar responsabilidades: validación, descarga del modelo, visión,
cálculos, análisis y reportes. Esto facilita pruebas, mantenimiento y trabajo
colaborativo.

### ¿Qué módulos externos usaste?
MediaPipe, OpenCV, pandas, NumPy, Matplotlib y openpyxl. Cada uno resuelve una
responsabilidad específica.

### ¿Qué módulo propio creaste?
Todo el paquete `src` es propio. Por ejemplo, `biomechanics.py` contiene los
cálculos geométricos y `jump_analysis.py` la lógica de fases.

### ¿Dónde hay manejo de errores?
En `main.py` se capturan errores previsibles y en las validaciones se rechazan
videos inexistentes, vacíos o con formato no admitido. También se comprueba que
OpenCV pueda abrir el archivo y que existan suficientes frames detectados.

### ¿Cómo calculás un ángulo?
Se forman dos vectores desde el vértice y se utiliza el producto escalar. El
coseno se limita entre -1 y 1 antes de aplicar arccos para evitar errores
numéricos.

### ¿Es machine learning entrenado por vos?
No. MediaPipe usa un modelo preentrenado. Mi programa integra ese modelo y
aplica lógica propia para procesar, validar, medir y reportar. No entrené una
red neuronal nueva.

### ¿El programa predice lesiones?
No. Detecta puntos, mide ángulos aproximados y clasifica fases. No diagnostica
ni infiere riesgo médico.

### ¿Cuál es el principio del Zen elegido?
“Simple is better than complex”. La complejidad se mantiene controlada con
módulos pequeños, una interfaz de consola y una heurística explicable.

### ¿Para qué sirve el entorno virtual?
Aísla las dependencias y permite reconstruir el proyecto con
`requirements.txt`, sin depender de lo instalado globalmente.

### ¿Cómo verificaste las sugerencias de IA?
Contrasté las APIs con documentación oficial, ejecuté el modo demo, agregué
pruebas unitarias y revisé los archivos de salida antes de incorporar cambios.

### ¿Cuál es la principal limitación técnica?
El análisis es 2D y depende de una cámara fija. El tiempo aéreo es una
estimación por desplazamiento de cadera, no una medición de contacto con suelo.
