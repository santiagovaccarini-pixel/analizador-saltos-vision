"""Pruebas de las funciones biomecánicas."""

import math

from src.biomechanics import calcular_angulo, diferencia_absoluta, punto_medio


def test_angulo_recto() -> None:
    """Verifica un ángulo geométrico de 90 grados."""
    assert calcular_angulo((1, 0), (0, 0), (0, 1)) == 90.0


def test_angulo_con_vector_nulo() -> None:
    """Verifica que un vector nulo produzca un valor no numérico."""
    assert math.isnan(calcular_angulo((0, 0), (0, 0), (1, 0)))


def test_punto_medio() -> None:
    """Verifica el cálculo del punto medio."""
    assert punto_medio((0, 2), (2, 4)) == (1.0, 3.0)


def test_diferencia_absoluta() -> None:
    """Verifica la diferencia absoluta."""
    assert diferencia_absoluta(10.0, 6.5) == 3.5
