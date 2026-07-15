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


def _promedio_columnas(datos: pd.DataFrame, columnas: list[str]) -> pd.Series:
    """Calcula el promedio por fila ignorando datos faltantes."""
    return datos[columnas].mean(axis=1, skipna=True)


def _tiempo(datos: pd.DataFrame, posicion: int | None) -> float | None:
    """Devuelve el tiempo redondeado de una posición o ``None``."""
    if posicion is None:
        return None
    return round(float(datos.loc[posicion, "time_s"]), 3)


def analizar_salto(
    datos_entrada: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, float | int | str | bool | None]]:
    """Suaviza señales, estima fases y construye un resumen del salto.

    La fase aérea se estima mediante el desplazamiento vertical del centro de
    cadera. El método no reemplaza una plataforma de fuerza y los ángulos 2D
    dependen de la perspectiva de cámara.
    """
    columnas_requeridas = {
        "frame",
        "time_s",
        "hip_center_y",
        "left_knee_angle",
        "right_knee_angle",
        "detection_quality",
    }
    faltantes = columnas_requeridas.difference(datos_entrada.columns)
    if faltantes:
        raise ValueError("Faltan columnas necesarias: " + ", ".join(sorted(faltantes)))
    if len(datos_entrada) < 15:
        raise ValueError("Se necesitan al menos 15 frames detectados.")

    datos = datos_entrada.sort_values("frame").reset_index(drop=True).copy()
    fps = float(datos_entrada.attrs.get("fps", 30.0))
    total_video_frames = int(datos_entrada.attrs.get("total_video_frames", len(datos)))
    ventana = max(5, int(round(fps * 0.075)))
    if ventana % 2 == 0:
        ventana += 1

    datos["hip_y_smooth"] = (
        datos["hip_center_y"]
        .interpolate(limit_direction="both")
        .rolling(window=ventana, center=True, min_periods=1)
        .median()
    )
    tiempo = datos["time_s"].to_numpy(dtype=float)
    posicion_y = datos["hip_y_smooth"].to_numpy(dtype=float)
    velocidad_y = np.gradient(posicion_y, tiempo)
    datos["vertical_velocity_norm_s"] = -velocidad_y

    margen = max(2, int(round(fps * 0.4)))
    inicio_busqueda = min(margen, len(datos) - 2)
    fin_busqueda = max(inicio_busqueda + 1, len(datos) - margen)
    tramo_velocidad = velocidad_y[inicio_busqueda:fin_busqueda]
    indice_impulso = inicio_busqueda + int(np.argmin(tramo_velocidad))

    retroceso = max(3, int(round(fps * 1.2)))
    avance = max(3, int(round(fps * 1.2)))
    inicio_preparacion = max(0, indice_impulso - retroceso)
    posicion_crouch = inicio_preparacion + int(
        np.argmax(posicion_y[inicio_preparacion : indice_impulso + 1])
    )
    fin_pico = min(len(datos), indice_impulso + avance + 1)
    posicion_pico = indice_impulso + int(np.argmin(posicion_y[indice_impulso:fin_pico]))

    fin_base = max(1, posicion_crouch - int(round(fps * 0.4)))
    inicio_base = max(0, fin_base - int(round(fps * 1.8)))
    if fin_base - inicio_base < 3:
        inicio_base = 0
        fin_base = max(3, int(len(datos) * 0.15))
    linea_base = float(np.median(posicion_y[inicio_base:fin_base]))
    datos["hip_displacement_norm"] = linea_base - datos["hip_y_smooth"]

    posicion_despegue: int | None = None
    for indice in range(posicion_crouch + 1, posicion_pico + 1):
        if posicion_y[indice] <= linea_base < posicion_y[indice - 1]:
            posicion_despegue = indice
            break

    fin_aterrizaje = min(len(datos), posicion_pico + max(3, int(round(fps * 0.85))) + 1)
    posicion_flexion_aterrizaje = posicion_pico + int(
        np.argmax(posicion_y[posicion_pico:fin_aterrizaje])
    )
    posicion_aterrizaje: int | None = None
    for indice in range(posicion_pico + 1, posicion_flexion_aterrizaje + 1):
        if posicion_y[indice] >= linea_base > posicion_y[indice - 1]:
            posicion_aterrizaje = indice
            break

    amplitud = max(0.0, linea_base - float(posicion_y[posicion_pico]))
    profundidad_crouch = max(0.0, float(posicion_y[posicion_crouch]) - linea_base)
    velocidad_ascenso = max(0.0, -float(velocidad_y[indice_impulso]))
    salto_detectado = (
        posicion_despegue is not None
        and posicion_aterrizaje is not None
        and amplitud >= 0.008
        and profundidad_crouch >= 0.015
        and velocidad_ascenso >= 0.05
    )

    datos["phase"] = "sin_clasificar"
    if salto_detectado:
        datos.loc[:posicion_crouch, "phase"] = "preparacion"
        datos.loc[posicion_crouch + 1 : posicion_despegue - 1, "phase"] = "impulso"
        datos.loc[posicion_despegue:posicion_pico, "phase"] = "ascenso"
        datos.loc[posicion_pico + 1 : posicion_aterrizaje, "phase"] = "descenso"
        datos.loc[posicion_aterrizaje + 1 : posicion_flexion_aterrizaje, "phase"] = "aterrizaje"
        datos.loc[posicion_flexion_aterrizaje + 1 :, "phase"] = "recuperacion"
    else:
        datos["phase"] = "salto_no_detectado"

    datos["mean_knee_angle"] = _promedio_columnas(
        datos, ["left_knee_angle", "right_knee_angle"]
    )
    datos["knee_symmetry_diff"] = (
        datos["left_knee_angle"] - datos["right_knee_angle"]
    ).abs()

    if salto_detectado:
        inicio_ventana_pre = max(0, posicion_crouch - int(fps * 0.15))
        fin_ventana_pre = posicion_despegue
        inicio_ventana_aterr = posicion_aterrizaje
        fin_ventana_aterr = min(
            len(datos) - 1,
            posicion_flexion_aterrizaje + int(fps * 0.15),
        )
        ventana_pre = datos.loc[inicio_ventana_pre:fin_ventana_pre]
        ventana_aterr = datos.loc[inicio_ventana_aterr:fin_ventana_aterr]
        ventana_evento = datos.loc[posicion_crouch:fin_ventana_aterr]
        vuelo = float(
            datos.loc[posicion_aterrizaje, "time_s"]
            - datos.loc[posicion_despegue, "time_s"]
        )
    else:
        ventana_pre = datos
        ventana_aterr = datos
        ventana_evento = datos
        vuelo = None

    tasa_deteccion = len(datos) / max(total_video_frames, 1)
    calidad_media = float(datos["detection_quality"].mean())
    if tasa_deteccion >= 0.90 and calidad_media >= 0.80:
        evaluacion_calidad = "alta"
    elif tasa_deteccion >= 0.70 and calidad_media >= 0.65:
        evaluacion_calidad = "aceptable"
    else:
        evaluacion_calidad = "limitada"

    resumen: dict[str, float | int | str | bool | None] = {
        "jump_detected": salto_detectado,
        "detected_frames": int(len(datos)),
        "total_video_frames": total_video_frames,
        "detection_rate": round(tasa_deteccion, 4),
        "mean_detection_quality": round(calidad_media, 4),
        "quality_assessment": evaluacion_calidad,
        "estimated_crouch_time_s": _tiempo(datos, posicion_crouch),
        "estimated_takeoff_time_s": _tiempo(datos, posicion_despegue),
        "estimated_peak_time_s": _tiempo(datos, posicion_pico),
        "estimated_landing_time_s": _tiempo(datos, posicion_aterrizaje),
        "estimated_landing_flexion_time_s": _tiempo(datos, posicion_flexion_aterrizaje),
        "estimated_flight_time_s": round(vuelo, 3) if vuelo is not None else None,
        "max_hip_displacement_normalized": round(amplitud, 4),
        "crouch_depth_normalized": round(profundidad_crouch, 4),
        "peak_upward_velocity_normalized_s": round(velocidad_ascenso, 4),
        "min_mean_knee_angle_preparation_deg": round(
            float(ventana_pre["mean_knee_angle"].min()), 2
        ),
        "mean_knee_symmetry_difference_deg": round(
            float(ventana_evento["knee_symmetry_diff"].mean()), 2
        ),
        "min_mean_knee_angle_landing_deg": round(
            float(ventana_aterr["mean_knee_angle"].min()), 2
        ),
        "methodological_note": (
            "Los tiempos y fases son estimaciones cinemáticas 2D basadas en "
            "el centro de cadera. Los ángulos dependen de la perspectiva; "
            "una vista frontal no representa bien la flexión sagital. No "
            "equivale a una plataforma de fuerza ni constituye diagnóstico."
        ),
    }
    return datos, resumen
