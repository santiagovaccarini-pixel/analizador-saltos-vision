"""Gestión del modelo TFLite utilizado para detectar la pose."""

from __future__ import annotations

from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

MODEL_URL = "https://unpkg.com/@mediapipe/pose/pose_landmark_full.tflite"
MIN_MODEL_SIZE = 1_000_000


def asegurar_modelo(ruta_modelo: Path) -> Path:
    """Devuelve un modelo válido y lo descarga si todavía no existe.

    El paquete de entrega incluye el modelo. Esta descarga funciona como respaldo
    para quienes clonen únicamente el repositorio de GitHub.

    Args:
        ruta_modelo: Ubicación donde se espera encontrar el archivo TFLite.

    Returns:
        Ruta del modelo listo para utilizar.

    Raises:
        RuntimeError: Si el archivo no existe y no puede descargarse.
    """
    if ruta_modelo.exists() and ruta_modelo.stat().st_size >= MIN_MODEL_SIZE:
        return ruta_modelo

    ruta_modelo.parent.mkdir(parents=True, exist_ok=True)
    archivo_temporal = ruta_modelo.with_suffix(ruta_modelo.suffix + ".part")
    try:
        with urlopen(MODEL_URL, timeout=60) as respuesta:  # noqa: S310
            archivo_temporal.write_bytes(respuesta.read())
        if archivo_temporal.stat().st_size < MIN_MODEL_SIZE:
            raise RuntimeError("El modelo descargado no tiene un tamaño válido.")
        archivo_temporal.replace(ruta_modelo)
    except (HTTPError, URLError, OSError, RuntimeError) as error:
        archivo_temporal.unlink(missing_ok=True)
        raise RuntimeError(
            "No se encontró el modelo de pose y no fue posible descargarlo. "
            "Use el ZIP de entrega completo o copie pose_landmark_full.tflite "
            f"dentro de {ruta_modelo.parent}."
        ) from error
    return ruta_modelo
