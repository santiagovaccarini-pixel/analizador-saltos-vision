"""Reconstruye el video de ejemplo almacenado en fragmentos Base64."""

from __future__ import annotations

import base64
from pathlib import Path


def reconstruir_video() -> Path:
    """Une los fragmentos Base64 y genera el MP4 utilizado en la prueba."""
    raiz = Path(__file__).resolve().parent
    carpeta_partes = raiz / "videos_entrada" / "video_ejemplo_base64"
    destino = raiz / "videos_entrada" / "salto_ejemplo.mp4"
    partes = sorted(carpeta_partes.glob("parte_*.b64"))
    if not partes:
        raise FileNotFoundError("No se encontraron los fragmentos del video de ejemplo.")
    contenido = "".join(parte.read_text(encoding="ascii") for parte in partes)
    destino.write_bytes(base64.b64decode(contenido, validate=True))
    print(f"Video de ejemplo preparado: {destino}")
    return destino


if __name__ == "__main__":
    reconstruir_video()
