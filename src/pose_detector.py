"""Procesamiento de video y extracción de landmarks con MediaPipe Pose."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import cv2
import numpy as np
import pandas as pd
from ai_edge_litert.interpreter import Interpreter

from src.biomechanics import metricas_de_frame
from src.constants import LANDMARK_NAMES, POSE_CONNECTIONS


@dataclass(frozen=True)
class Landmark:
    """Representa un punto corporal normalizado detectado en un frame."""

    x: float
    y: float
    z: float
    visibility: float


def _sigmoide(valor: float) -> float:
    """Convierte un logit del modelo en una probabilidad entre cero y uno."""
    limitado = float(np.clip(valor, -50.0, 50.0))
    return float(1.0 / (1.0 + np.exp(-limitado)))


def _crear_interprete(ruta_modelo: Path) -> Interpreter:
    """Carga el modelo TFLite y reserva sus tensores."""
    if not ruta_modelo.exists() or ruta_modelo.stat().st_size < 1_000_000:
        raise FileNotFoundError(
            "No se encontró un modelo de pose válido en "
            f"{ruta_modelo}. Use el ZIP completo o permita la descarga automática."
        )
    interprete = Interpreter(model_path=str(ruta_modelo), num_threads=4)
    interprete.allocate_tensors()
    return interprete


def _recorte_cuadrado_central(frame: Any) -> tuple[Any, int, int, int]:
    """Obtiene el mayor recorte cuadrado centrado dentro del frame."""
    alto, ancho = frame.shape[:2]
    lado = min(alto, ancho)
    x_inicio = max(0, (ancho - lado) // 2)
    y_inicio = max(0, (alto - lado) // 2)
    return (
        frame[y_inicio : y_inicio + lado, x_inicio : x_inicio + lado],
        x_inicio,
        y_inicio,
        lado,
    )


def _decodificar_landmarks(
    salida: np.ndarray,
    ancho_frame: int,
    alto_frame: int,
    x_inicio: int,
    y_inicio: int,
    lado: int,
) -> list[Landmark]:
    """Convierte la salida plana del modelo a landmarks normalizados."""
    valores = salida.reshape(39, 5)
    landmarks: list[Landmark] = []
    for indice in range(33):
        x_modelo, y_modelo, z_modelo, logit_vis, logit_presencia = valores[indice]
        x = (x_inicio + (float(x_modelo) / 256.0) * lado) / ancho_frame
        y = (y_inicio + (float(y_modelo) / 256.0) * lado) / alto_frame
        visibilidad = min(_sigmoide(logit_vis), _sigmoide(logit_presencia))
        landmarks.append(
            Landmark(
                x=float(x),
                y=float(y),
                z=float(z_modelo) / 256.0,
                visibility=visibilidad,
            )
        )
    return landmarks


def _dibujar_pose(
    frame: Any,
    landmarks: Sequence[Landmark],
    calidad: float,
) -> Any:
    """Dibuja conexiones y puntos corporales sobre una copia del frame."""
    alto, ancho = frame.shape[:2]
    salida = frame.copy()

    for inicio, fin in POSE_CONNECTIONS:
        p1 = landmarks[inicio]
        p2 = landmarks[fin]
        if min(p1.visibility, p2.visibility) < 0.45:
            continue
        x1, y1 = int(p1.x * ancho), int(p1.y * alto)
        x2, y2 = int(p2.x * ancho), int(p2.y * alto)
        cv2.line(salida, (x1, y1), (x2, y2), (0, 220, 0), 2)

    for indice in LANDMARK_NAMES:
        punto = landmarks[indice]
        if punto.visibility < 0.45:
            continue
        x, y = int(punto.x * ancho), int(punto.y * alto)
        cv2.circle(salida, (x, y), 4, (0, 0, 255), -1)

    cv2.putText(
        salida,
        f"Calidad pose: {calidad:.0%}",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )
    return salida


def procesar_video(
    ruta_video: Path,
    ruta_modelo: Path,
    carpeta_salida: Path,
    generar_video_anotado: bool = True,
) -> pd.DataFrame:
    """Procesa un video y devuelve una fila de métricas por frame.

    Args:
        ruta_video: Video de entrada.
        ruta_modelo: Modelo MediaPipe Pose Landmark en formato TFLite.
        carpeta_salida: Carpeta donde se guardará el video anotado.
        generar_video_anotado: Indica si se crea una copia con el esqueleto.

    Returns:
        DataFrame con métricas geométricas y calidad de detección.

    Raises:
        RuntimeError: Si el video no puede abrirse o no contiene una pose.
    """
    carpeta_salida.mkdir(parents=True, exist_ok=True)
    captura = cv2.VideoCapture(str(ruta_video))
    if not captura.isOpened():
        raise RuntimeError("OpenCV no pudo abrir el video de entrada.")

    fps = float(captura.get(cv2.CAP_PROP_FPS))
    ancho = int(captura.get(cv2.CAP_PROP_FRAME_WIDTH))
    alto = int(captura.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if fps <= 0 or ancho <= 0 or alto <= 0:
        captura.release()
        raise RuntimeError("El video no informa FPS o dimensiones válidas.")

    interprete = _crear_interprete(ruta_modelo)
    entrada = interprete.get_input_details()[0]
    salidas = interprete.get_output_details()
    indice_landmarks = next(
        detalle["index"] for detalle in salidas if detalle["name"] == "Identity"
    )
    indice_presencia = next(
        detalle["index"] for detalle in salidas if detalle["name"] == "Identity_1"
    )

    escala = min(1.0, 960.0 / ancho)
    ancho_salida = int(round(ancho * escala))
    alto_salida = int(round(alto * escala))
    escritor = None
    if generar_video_anotado:
        escritor = cv2.VideoWriter(
            str(carpeta_salida / "video_anotado.mp4"),
            cv2.VideoWriter_fourcc(*"mp4v"),
            fps,
            (ancho_salida, alto_salida),
        )
        if not escritor.isOpened():
            captura.release()
            raise RuntimeError("No se pudo crear el video anotado.")

    registros: list[dict[str, float | int]] = []
    numero_frame = 0
    try:
        while True:
            leido, frame = captura.read()
            if not leido:
                break

            recorte, x_inicio, y_inicio, lado = _recorte_cuadrado_central(frame)
            imagen = cv2.resize(recorte, (256, 256), interpolation=cv2.INTER_AREA)
            imagen = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
            tensor = imagen.astype(np.float32) / 255.0
            interprete.set_tensor(entrada["index"], tensor[None, ...])
            interprete.invoke()

            presencia = float(interprete.get_tensor(indice_presencia)[0, 0])
            if presencia >= 0.50:
                landmarks = _decodificar_landmarks(
                    interprete.get_tensor(indice_landmarks),
                    ancho,
                    alto,
                    x_inicio,
                    y_inicio,
                    lado,
                )
                metricas = metricas_de_frame(
                    landmarks,
                    numero_frame=numero_frame,
                    tiempo_s=numero_frame / fps,
                )
                metricas["pose_presence"] = presencia
                registros.append(metricas)
                if escritor is not None:
                    frame = _dibujar_pose(
                        frame,
                        landmarks,
                        float(metricas["detection_quality"]),
                    )

            if escritor is not None:
                if escala != 1.0:
                    frame = cv2.resize(
                        frame,
                        (ancho_salida, alto_salida),
                        interpolation=cv2.INTER_AREA,
                    )
                escritor.write(frame)
            numero_frame += 1
    finally:
        captura.release()
        if escritor is not None:
            escritor.release()

    if not registros:
        raise RuntimeError(
            "No se detectó una pose. Verifique que el cuerpo esté completo, "
            "centrado y con iluminación suficiente."
        )

    datos = pd.DataFrame(registros)
    datos.attrs["fps"] = fps
    datos.attrs["total_video_frames"] = numero_frame
    return datos
