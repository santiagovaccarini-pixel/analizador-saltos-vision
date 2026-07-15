"""Descarga y valida el modelo usado por MediaPipe Pose Landmarker."""

from __future__ import annotations

from pathlib import Path
from urllib.error import URLError
from urllib.request import urlretrieve

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
    "pose_landmarker_full/float16/latest/pose_landmarker_full.task"
)


def asegurar_modelo(ruta_modelo: Path) -> Path:
    """Devuelve el modelo local y lo descarga cuando todavía no existe."""
    if ruta_modelo.exists() and ruta_modelo.stat().st_size > 0:
        return ruta_modelo
    ruta_modelo.parent.mkdir(parents=True, exist_ok=True)
    try:
        urlretrieve(MODEL_URL, ruta_modelo)
    except (URLError, OSError) as error:
        raise RuntimeError(
            "No se pudo descargar el modelo de MediaPipe. Revise la conexión "
            "o descargue manualmente pose_landmarker_full.task."
        ) from error
    if not ruta_modelo.exists() or ruta_modelo.stat().st_size == 0:
        raise RuntimeError("El modelo descargado está vacío o no es válido.")
    return ruta_modelo
