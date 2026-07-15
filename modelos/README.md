# Modelo de pose

El ZIP de entrega incluye `pose_landmark_full.tflite`, por lo que el análisis
puede ejecutarse sin descargar archivos adicionales.

Para mantener el repositorio liviano, si el archivo no está presente el programa
intenta descargarlo automáticamente desde el paquete oficial `@mediapipe/pose`.
El modelo es preentrenado; la lógica de validación, cálculo de métricas, detección
de fases y generación de reportes pertenece a este proyecto.
