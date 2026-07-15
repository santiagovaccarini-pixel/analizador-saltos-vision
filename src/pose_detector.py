"""Procesamiento de video y extracción de puntos corporales con MediaPipe."""

from __future__ import annotations

from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
import pandas as pd

from src.biomechanics import calcular_angulo
from src.model_manager import asegurar_modelo
from src.validation import preparar_carpeta


def _coordenada(landmarks: list, indice: int) -> tuple[float, float, float]:
    """Extrae las coordenadas normalizadas de un landmark."""
    punto = landmarks[indice]
    return float(punto.x), float(punto.y), float(punto.z)


def _visibilidad_media(landmarks: list, indices: tuple[int, ...]) -> float:
    """Calcula una calidad media basada en la visibilidad de puntos clave."""
    valores = [float(getattr(landmarks[i], "visibility", 0.0)) for i in indices]
    return float(np.mean(valores))


def procesar_video(
    ruta_video: Path,
    ruta_modelo: Path,
    carpeta_salida: Path,
    generar_video_anotado: bool = True,
) -> pd.DataFrame:
    """Detecta la pose frame a frame y devuelve métricas articulares."""
    carpeta_salida = preparar_carpeta(carpeta_salida)
    modelo = asegurar_modelo(ruta_modelo)
    captura = cv2.VideoCapture(str(ruta_video))
    if not captura.isOpened():
        raise RuntimeError(f"OpenCV no pudo abrir el video: {ruta_video}")

    fps = captura.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(captura.get(cv2.CAP_PROP_FRAME_COUNT))
    ancho = int(captura.get(cv2.CAP_PROP_FRAME_WIDTH))
    alto = int(captura.get(cv2.CAP_PROP_FRAME_HEIGHT))
    escritor = None
    if generar_video_anotado:
        salida_video = carpeta_salida / "video_anotado.mp4"
        escritor = cv2.VideoWriter(
            str(salida_video),
            cv2.VideoWriter_fourcc(*"mp4v"),
            fps,
            (ancho, alto),
        )

    opciones_base = mp.tasks.BaseOptions(model_asset_path=str(modelo))
    opciones = mp.tasks.vision.PoseLandmarkerOptions(
        base_options=opciones_base,
        running_mode=mp.tasks.vision.RunningMode.VIDEO,
        num_poses=1,
        min_pose_detection_confidence=0.5,
        min_pose_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )
    filas: list[dict[str, float | int]] = []
    try:
        with mp.tasks.vision.PoseLandmarker.create_from_options(opciones) as detector:
            frame = 0
            while True:
                leido, imagen_bgr = captura.read()
                if not leido:
                    break
                imagen_rgb = cv2.cvtColor(imagen_bgr, cv2.COLOR_BGR2RGB)
                imagen_mp = mp.Image(image_format=mp.ImageFormat.SRGB, data=imagen_rgb)
                marca_tiempo = int((frame / fps) * 1000)
                resultado = detector.detect_for_video(imagen_mp, marca_tiempo)
                if resultado.pose_landmarks:
                    puntos = resultado.pose_landmarks[0]
                    cadera_izq = _coordenada(puntos, 23)
                    cadera_der = _coordenada(puntos, 24)
                    rodilla_izq = _coordenada(puntos, 25)
                    rodilla_der = _coordenada(puntos, 26)
                    tobillo_izq = _coordenada(puntos, 27)
                    tobillo_der = _coordenada(puntos, 28)
                    centro_cadera_y = (cadera_izq[1] + cadera_der[1]) / 2.0
                    filas.append({
                        "frame": frame,
                        "time_s": frame / fps,
                        "hip_center_y": centro_cadera_y,
                        "left_knee_angle": calcular_angulo(cadera_izq, rodilla_izq, tobillo_izq),
                        "right_knee_angle": calcular_angulo(cadera_der, rodilla_der, tobillo_der),
                        "detection_quality": _visibilidad_media(puntos, (23, 24, 25, 26, 27, 28)),
                    })
                if escritor is not None:
                    escritor.write(imagen_bgr)
                frame += 1
    finally:
        captura.release()
        if escritor is not None:
            escritor.release()

    if not filas:
        raise RuntimeError("No se detectó ninguna pose válida en el video.")
    datos = pd.DataFrame(filas)
    datos.attrs["fps"] = float(fps)
    datos.attrs["total_video_frames"] = total_frames
    return datos
