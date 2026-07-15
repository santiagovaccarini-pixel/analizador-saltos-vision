"""Generación reproducible de una señal de salto simulada para demostración."""

from __future__ import annotations

import numpy as np
import pandas as pd


def generar_datos_demo(fps: int = 30, duracion_s: float = 4.0) -> pd.DataFrame:
    """Crea un conjunto sintético que imita las fases de un salto vertical.

    Los datos simulados no se presentan como mediciones reales. Su objetivo es
    permitir probar el pipeline completo y verificar la generación de salidas.
    """
    cantidad = int(fps * duracion_s)
    frames = np.arange(cantidad)
    tiempo = frames / fps
    rng = np.random.default_rng(42)

    hip_y = np.full(cantidad, 0.56, dtype=float)
    knee = np.full(cantidad, 168.0, dtype=float)
    hip_angle = np.full(cantidad, 165.0, dtype=float)
    ankle = np.full(cantidad, 95.0, dtype=float)

    prep = (tiempo >= 0.8) & (tiempo < 1.25)
    fase_prep = (tiempo[prep] - 0.8) / 0.45
    hip_y[prep] += 0.055 * np.sin(np.pi * fase_prep)
    knee[prep] -= 78 * np.sin(np.pi * fase_prep)
    hip_angle[prep] -= 65 * np.sin(np.pi * fase_prep)

    vuelo = (tiempo >= 1.25) & (tiempo <= 1.92)
    fase_vuelo = (tiempo[vuelo] - 1.25) / 0.67
    hip_y[vuelo] -= 0.145 * np.sin(np.pi * fase_vuelo)
    knee[vuelo] = 170 - 8 * np.sin(np.pi * fase_vuelo)
    hip_angle[vuelo] = 170 - 6 * np.sin(np.pi * fase_vuelo)
    ankle[vuelo] = 112 + 8 * np.sin(np.pi * fase_vuelo)

    aterr = (tiempo > 1.92) & (tiempo <= 2.65)
    fase_aterr = (tiempo[aterr] - 1.92) / 0.73
    hip_y[aterr] += 0.045 * np.sin(np.pi * fase_aterr)
    knee[aterr] -= 62 * np.sin(np.pi * fase_aterr)
    hip_angle[aterr] -= 45 * np.sin(np.pi * fase_aterr)

    hip_y += rng.normal(0, 0.0015, cantidad)
    left_knee = knee + rng.normal(0, 1.2, cantidad)
    right_knee = knee + 3.0 + rng.normal(0, 1.2, cantidad)

    datos = pd.DataFrame(
        {
            "frame": frames,
            "time_s": tiempo,
            "hip_center_x": 0.50 + rng.normal(0, 0.001, cantidad),
            "hip_center_y": hip_y,
            "left_knee_angle": left_knee,
            "right_knee_angle": right_knee,
            "left_hip_angle": hip_angle + rng.normal(0, 1.0, cantidad),
            "right_hip_angle": hip_angle + 2 + rng.normal(0, 1.0, cantidad),
            "left_ankle_angle": ankle + rng.normal(0, 1.0, cantidad),
            "right_ankle_angle": ankle + rng.normal(0, 1.0, cantidad),
            "detection_quality": np.clip(
                rng.normal(0.93, 0.025, cantidad), 0.75, 0.99
            ),
        }
    )
    datos.attrs["fps"] = float(fps)
    datos.attrs["total_video_frames"] = cantidad
    return datos
