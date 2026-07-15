"""Validaciones de rutas y archivos de entrada."""

from pathlib import Path

from src.constants import VIDEO_EXTENSIONS


def validar_ruta_video(ruta: Path) -> None:
    """Valida que la ruta apunte a un video existente y compatible."""
    if ruta is None:
        raise ValueError("Debe indicarse la ruta de un video.")
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")
    if not ruta.is_file():
        raise ValueError(f"La ruta no corresponde a un archivo: {ruta}")
    if ruta.suffix.lower() not in VIDEO_EXTENSIONS:
        extensiones = ", ".join(sorted(VIDEO_EXTENSIONS))
        raise ValueError(f"Formato no admitido. Use: {extensiones}")


def preparar_carpeta(ruta: Path) -> Path:
    """Crea una carpeta de salida y devuelve su ruta normalizada."""
    ruta.mkdir(parents=True, exist_ok=True)
    return ruta
