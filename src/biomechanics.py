"""Funciones matemáticas para métricas biomecánicas aproximadas."""

from __future__ import annotations

import math
from collections.abc import Sequence

import numpy as np


def calcular_angulo(a: Sequence[float], b: Sequence[float], c: Sequence[float]) -> float:
    """Calcula en grados el ángulo ABC usando coordenadas 2D o 3D."""
    punto_a = np.asarray(a, dtype=float)
    punto_b = np.asarray(b, dtype=float)
    punto_c = np.asarray(c, dtype=float)
    vector_ba = punto_a - punto_b
    vector_bc = punto_c - punto_b
    norma = np.linalg.norm(vector_ba) * np.linalg.norm(vector_bc)
    if norma == 0:
        return math.nan
    coseno = float(np.dot(vector_ba, vector_bc) / norma)
    coseno = float(np.clip(coseno, -1.0, 1.0))
    return float(np.degrees(np.arccos(coseno)))


def punto_medio(a: Sequence[float], b: Sequence[float]) -> tuple[float, ...]:
    """Devuelve el punto medio entre dos coordenadas."""
    return tuple((np.asarray(a, dtype=float) + np.asarray(b, dtype=float)) / 2.0)


def diferencia_absoluta(valor_a: float, valor_b: float) -> float:
    """Calcula una diferencia absoluta preservando valores faltantes."""
    if np.isnan(valor_a) or np.isnan(valor_b):
        return math.nan
    return abs(valor_a - valor_b)
