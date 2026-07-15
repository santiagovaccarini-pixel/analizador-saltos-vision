# Guía breve para la defensa

## Problema resuelto

El proyecto transforma un video de un salto en datos cuantitativos aproximados. Detecta puntos corporales, calcula ángulos de rodilla, estima fases temporales y exporta resultados.

## Decisiones técnicas

- Se utilizó MediaPipe Pose Landmarker para evitar entrenar un modelo desde cero.
- OpenCV administra el video y los frames.
- pandas organiza y exporta datos.
- NumPy realiza cálculos numéricos.
- matplotlib genera gráficos.
- openpyxl permite crear el informe Excel.
- La lógica se separó en módulos para facilitar mantenimiento y pruebas.

## Limitaciones

No es una herramienta médica ni reemplaza plataformas de fuerza o sistemas 3D. Las coordenadas provienen de una imagen 2D y dependen de cámara, iluminación, ropa y visibilidad corporal.

## Preguntas probables

**¿Por qué existe un modo demo?** Para demostrar la lógica y generar resultados reproducibles sin depender de un video externo.

**¿Qué significa detectar y qué significa predecir?** El sistema detecta puntos y estima métricas a partir de observaciones; no predice el rendimiento futuro ni diagnostica lesiones.

**¿Cómo se controlaron errores?** Con validaciones de rutas, formatos, cantidad mínima de frames, columnas requeridas, apertura del video y detecciones vacías.

**¿Cómo se aplicó el Zen de Python?** Priorizando una solución explícita, simple y modular frente a un único script extenso.
