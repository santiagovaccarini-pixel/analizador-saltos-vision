"""Detección heurística de fases y resumen cuantitativo del salto."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Segmento:
    """Representa un intervalo continuo de frames."""

    inicio: int
    fin: int

    @property
    def longitud(self) -> int:
        """Cantidad de posiciones incluidas en el segmento."""
        return self.fin - self.inicio + 1


def _segmento_mas_largo(mascara: np.ndarray) -> Segmento | None:
    """Devuelve el segmento verdadero continuo de mayor longitud."""
    mejor: Segmento | None = None
    inicio: int | None = None
    for indice, activo in enumerate(mascara):
        if activo and inicio is None:
            inicio = indice
        if inicio is not None and (not activo or indice == len(mascara) - 1):
            fin = indice if activo and indice == len(mascara) - 1 else indice - 1
            candidato = Segmento(inicio, fin)
            if mejor is None or candidato.longitud > mejor.longitud:
                mejor = candidato
            inicio = None
    return mejor


def _promedio_columnas(datos: pd.DataFrame, columnas: list[str]) -> pd.Series:
    """Calcula el promedio por fila ignorando datos faltantes."""
    return datos[columnas].mean(axis=1, skipna=True)


def analizar_salto(datos_entrada: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, float | int | str | bool | None]]:
    """Suaviza señales, estima fases y construye un resumen del salto."""
    columnas_requeridas = {
        "frame", "time_s", "hip_center_y", "left_knee_angle",
        "right_knee_angle", "detection_quality",
    }
    faltantes = columnas_requeridas.difference(datos_entrada.columns)
    if faltantes:
        raise ValueError("Faltan columnas necesarias: " + ", ".join(sorted(faltantes)))
    if len(datos_entrada) < 15:
        raise ValueError("Se necesitan al menos 15 frames detectados.")

    datos = datos_entrada.sort_values("frame").reset_index(drop=True).copy()
    fps = float(datos_entrada.attrs.get("fps", 30.0))
    total_video_frames = int(datos_entrada.attrs.get("total_video_frames", len(datos)))
    datos["hip_y_smooth"] = datos["hip_center_y"].interpolate(limit_direction="both").rolling(window=5, center=True, min_periods=1).median()
    cantidad_base = max(5, int(len(datos) * 0.15))
    linea_base = (float(datos["hip_y_smooth"].iloc[:cantidad_base].median()) + float(datos["hip_y_smooth"].iloc[-cantidad_base:].median())) / 2.0
    datos["hip_displacement_norm"] = linea_base - datos["hip_y_smooth"]
    tiempo = datos["time_s"].to_numpy(dtype=float)
    altura = datos["hip_displacement_norm"].to_numpy(dtype=float)
    datos["vertical_velocity_norm_s"] = np.gradient(altura, tiempo)
    amplitud = float(np.nanmax(altura))
    umbral = max(0.012, amplitud * 0.25)
    segmento = _segmento_mas_largo(altura > umbral) if amplitud >= 0.015 else None
    datos["phase"] = "sin_clasificar"
    takeoff_pos: int | None = None
    landing_pos: int | None = None
    peak_pos: int | None = None
    if segmento is not None and segmento.longitud >= max(3, int(fps * 0.08)):
        takeoff_pos = segmento.inicio
        landing_pos = segmento.fin
        peak_pos = int(np.argmax(altura[segmento.inicio:segmento.fin + 1])) + segmento.inicio
        datos.loc[:max(0, takeoff_pos - 1), "phase"] = "preparacion"
        datos.loc[takeoff_pos:peak_pos, "phase"] = "ascenso"
        datos.loc[peak_pos + 1:landing_pos, "phase"] = "descenso"
        datos.loc[landing_pos + 1:, "phase"] = "aterrizaje_recuperacion"
    else:
        datos["phase"] = "salto_no_detectado"

    datos["mean_knee_angle"] = _promedio_columnas(datos, ["left_knee_angle", "right_knee_angle"])
    datos["knee_symmetry_diff"] = (datos["left_knee_angle"] - datos["right_knee_angle"]).abs()

    def valor_tiempo(posicion: int | None) -> float | None:
        """Convierte una posición de fila en tiempo redondeado."""
        if posicion is None:
            return None
        return round(float(datos.loc[posicion, "time_s"]), 3)

    ventana_pre = datos.loc[0:takeoff_pos if takeoff_pos is not None else len(datos) - 1]
    ventana_aterr = datos.loc[landing_pos if landing_pos is not None else len(datos) - 1:]
    vuelo = None
    if takeoff_pos is not None and landing_pos is not None:
        vuelo = float(datos.loc[landing_pos, "time_s"] - datos.loc[takeoff_pos, "time_s"])
    tasa_deteccion = len(datos) / max(total_video_frames, 1)
    calidad_media = float(datos["detection_quality"].mean())
    if tasa_deteccion >= 0.90 and calidad_media >= 0.80:
        evaluacion_calidad = "alta"
    elif tasa_deteccion >= 0.70 and calidad_media >= 0.65:
        evaluacion_calidad = "aceptable"
    else:
        evaluacion_calidad = "limitada"
    resumen = {
        "jump_detected": takeoff_pos is not None,
        "detected_frames": int(len(datos)),
        "total_video_frames": total_video_frames,
        "detection_rate": round(tasa_deteccion, 4),
        "mean_detection_quality": round(calidad_media, 4),
        "quality_assessment": evaluacion_calidad,
        "estimated_takeoff_time_s": valor_tiempo(takeoff_pos),
        "estimated_peak_time_s": valor_tiempo(peak_pos),
        "estimated_landing_time_s": valor_tiempo(landing_pos),
        "estimated_flight_time_s": round(vuelo, 3) if vuelo is not None else None,
        "max_hip_displacement_normalized": round(max(amplitud, 0.0), 4),
        "min_mean_knee_angle_preparation_deg": round(float(ventana_pre["mean_knee_angle"].min()), 2),
        "mean_knee_symmetry_difference_deg": round(float(datos["knee_symmetry_diff"].mean()), 2),
        "min_mean_knee_angle_landing_deg": round(float(ventana_aterr["mean_knee_angle"].min()), 2),
        "methodological_note": "Los tiempos y fases son estimaciones cinemáticas 2D; no constituyen diagnóstico médico.",
    }
    return datos, resumen
