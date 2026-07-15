"""Pruebas del análisis temporal del salto."""

from src.demo_data import generar_datos_demo
from src.jump_analysis import analizar_salto


def test_demo_detecta_salto() -> None:
    """Comprueba que la señal demo sea reconocida como salto."""
    datos = generar_datos_demo()
    analizados, resumen = analizar_salto(datos)
    assert resumen["jump_detected"] is True
    assert resumen["estimated_flight_time_s"] is not None
    assert "phase" in analizados.columns
