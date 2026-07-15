"""Generación reproducible de señales simuladas para la demostración."""

from __future__ import annotations

import numpy as np
import pandas as pd


def generar_datos_demo(cantidad_frames: int = 120, fps: float = 30.0) -> pd.DataFrame:
    """Genera un salto sintético con señales suaves y reproducibles."""
    if cantidad_frames < 30:
        raise ValueError("La demostración requiere al menos 30 frames.")
    frames = np.arange(cantidad_frames)
    tiempo = frames / fps
    centro = cantidad_frames * 0.52
    ancho = cantidad_frames * 0.13
    elevacion = 0.11 * np.exp(-0.5 * ((frames - centro) / ancho) ** 2)
    preparacion = 28 * np.exp(-0.5 * ((frames - cantidad_frames * 0.35) / 10) ** 2)
    aterrizaje = 20 * np.exp(-0.5 * ((frames - cantidad_frames * 0.72) / 8) ** 2)
    angulo_base = 168 - preparacion - aterrizaje
    datos = pd.DataFrame({
        "frame": frames,
        "time_s": tiempo,
        "hip_center_y": 0.58 - elevacion,
        "left_knee_angle": angulo_base + 1.8 * np.sin(frames / 8),
        "right_knee_angle": angulo_base - 1.5 * np.sin(frames / 9),
        "detection_quality": np.full(cantidad_frames, 0.96),
    })
    datos.attrs["fps"] = fps
    datos.attrs["total_video_frames"] = cantidad_frames
    return datos
