"""Cálculos geométricos utilizados para estimar variables biomecánicas."""

from __future__ import annotations

import math
from typing import Any, Sequence

import numpy as np

from src.constants import LOWER_BODY_INDICES, MIN_VISIBILITY


def _valor(landmark: Any, atributo: str, predeterminado: float = 0.0) -> float:
    """Obtiene un atributo de un landmark como objeto o diccionario."""
    if isinstance(landmark, dict):
        return float(landmark.get(atributo, predeterminado))
    return float(getattr(landmark, atributo, predeterminado))


def punto_xy(landmarks: Sequence[Any], indice: int) -> np.ndarray:
    """Devuelve las coordenadas bidimensionales de un landmark."""
    punto = landmarks[indice]
    return np.array([_valor(punto, "x"), _valor(punto, "y")], dtype=float)


def visibilidad(landmarks: Sequence[Any], indice: int) -> float:
    """Devuelve la visibilidad estimada de un landmark."""
    return _valor(landmarks[indice], "visibility", 1.0)


def calcular_angulo(
    punto_a: np.ndarray,
    vertice_b: np.ndarray,
    punto_c: np.ndarray,
) -> float:
    """Calcula el ángulo ABC en grados dentro del rango 0-180.

    Devuelve ``nan`` cuando algún vector tiene longitud prácticamente nula.
    """
    vector_ba = np.asarray(punto_a, dtype=float) - np.asarray(vertice_b, dtype=float)
    vector_bc = np.asarray(punto_c, dtype=float) - np.asarray(vertice_b, dtype=float)
    norma = np.linalg.norm(vector_ba) * np.linalg.norm(vector_bc)
    if norma <= 1e-12:
        return float("nan")
    coseno = float(np.dot(vector_ba, vector_bc) / norma)
    coseno = float(np.clip(coseno, -1.0, 1.0))
    return math.degrees(math.acos(coseno))


def punto_medio(a: Sequence[float], b: Sequence[float]) -> tuple[float, ...]:
    """Devuelve el punto medio entre dos coordenadas."""
    return tuple((np.asarray(a, dtype=float) + np.asarray(b, dtype=float)) / 2.0)


def diferencia_absoluta(valor_a: float, valor_b: float) -> float:
    """Calcula una diferencia absoluta preservando valores faltantes."""
    if np.isnan(valor_a) or np.isnan(valor_b):
        return math.nan
    return abs(valor_a - valor_b)


def angulo_articular(
    landmarks: Sequence[Any],
    indices: tuple[int, int, int],
    visibilidad_minima: float = MIN_VISIBILITY,
) -> float:
    """Calcula un ángulo si sus tres landmarks tienen visibilidad suficiente."""
    if any(visibilidad(landmarks, i) < visibilidad_minima for i in indices):
        return float("nan")
    a, b, c = (punto_xy(landmarks, i) for i in indices)
    return calcular_angulo(a, b, c)


def centro(landmarks: Sequence[Any], indice_a: int, indice_b: int) -> np.ndarray:
    """Calcula el punto medio de dos landmarks."""
    return (punto_xy(landmarks, indice_a) + punto_xy(landmarks, indice_b)) / 2.0


def calidad_deteccion(landmarks: Sequence[Any]) -> float:
    """Promedia la visibilidad de los landmarks del tren inferior."""
    valores = [visibilidad(landmarks, indice) for indice in LOWER_BODY_INDICES]
    return float(np.mean(valores))


def metricas_de_frame(
    landmarks: Sequence[Any],
    numero_frame: int,
    tiempo_s: float,
) -> dict[str, float | int]:
    """Calcula las métricas principales de un frame detectado."""
    cadera = centro(landmarks, 23, 24)
    return {
        "frame": numero_frame,
        "time_s": tiempo_s,
        "hip_center_x": float(cadera[0]),
        "hip_center_y": float(cadera[1]),
        "left_knee_angle": angulo_articular(landmarks, (23, 25, 27)),
        "right_knee_angle": angulo_articular(landmarks, (24, 26, 28)),
        "left_hip_angle": angulo_articular(landmarks, (11, 23, 25)),
        "right_hip_angle": angulo_articular(landmarks, (12, 24, 26)),
        "left_ankle_angle": angulo_articular(landmarks, (25, 27, 31)),
        "right_ankle_angle": angulo_articular(landmarks, (26, 28, 32)),
        "detection_quality": calidad_deteccion(landmarks),
    }
