"""Validaciones de entrada para evitar fallos silenciosos."""

from __future__ import annotations

from pathlib import Path

from src.constants import SUPPORTED_VIDEO_EXTENSIONS


def validar_ruta_video(ruta_video: Path) -> None:
    """Valida existencia, extensión y tamaño básico de un video.

    Args:
        ruta_video: Ruta del archivo de video.

    Raises:
        FileNotFoundError: Si el archivo no existe.
        ValueError: Si la ruta no es un archivo, está vacío o tiene una
            extensión no admitida.
    """
    if not ruta_video.exists():
        raise FileNotFoundError(f"No se encontró el video: {ruta_video}")
    if not ruta_video.is_file():
        raise ValueError(f"La ruta no corresponde a un archivo: {ruta_video}")
    if ruta_video.suffix.lower() not in SUPPORTED_VIDEO_EXTENSIONS:
        extensiones = ", ".join(sorted(SUPPORTED_VIDEO_EXTENSIONS))
        raise ValueError(
            f"Formato no admitido ({ruta_video.suffix}). Use: {extensiones}."
        )
    if ruta_video.stat().st_size == 0:
        raise ValueError("El archivo de video está vacío.")
