# Prueba completa con video

El repositorio incluye una copia optimizada del video real utilizado durante la
validación. El archivo original pesaba 129 MB, por encima del límite individual
de GitHub, por lo que se almacenó una versión comprimida del mismo contenido.

## Windows

1. Descargar o clonar el repositorio.
2. Hacer doble clic en `probar_video.bat`.
3. Esperar a que finalice la instalación y el análisis.

El ejecutor:

- crea el entorno virtual cuando no existe;
- instala las dependencias de `requirements.txt`;
- reconstruye `videos_entrada/salto_ejemplo.mp4`;
- ejecuta el programa;
- guarda las salidas en `resultados_prueba`;
- abre automáticamente `video_anotado.mp4`.

## Ejecución manual

```powershell
python preparar_video_ejemplo.py
python main.py --video videos_entrada/salto_ejemplo.mp4 --salida resultados_prueba
```

La versión optimizada conserva el salto completo y permite verificar el flujo
real de lectura, inferencia, cálculo, reportes y generación del video anotado.
