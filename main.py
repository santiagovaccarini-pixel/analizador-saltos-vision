"""Punto de entrada del Analizador de Saltos con Visión por Computadora."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.demo_data import generar_datos_demo
from src.jump_analysis import analizar_salto
from src.reporting import generar_salidas
from src.validation import validar_ruta_video


def crear_parser() -> argparse.ArgumentParser:
    """Construye y devuelve el parser de argumentos de la aplicación."""
    parser = argparse.ArgumentParser(
        description=(
            "Analiza un salto desde video mediante MediaPipe Pose o ejecuta "
            "una demostración reproducible con datos simulados."
        )
    )
    grupo = parser.add_mutually_exclusive_group(required=True)
    grupo.add_argument("--video", type=Path, help="Ruta del video que se desea analizar.")
    grupo.add_argument("--demo", action="store_true", help="Ejecuta una demostración sin necesidad de video.")
    parser.add_argument("--salida", type=Path, default=Path("resultados"), help="Carpeta de salida.")
    parser.add_argument("--modelo", type=Path, default=Path("modelos/pose_landmarker_full.task"), help="Ruta del modelo MediaPipe.")
    parser.add_argument("--sin-video-anotado", action="store_true", help="No genera video anotado.")
    return parser


def ejecutar_demo(carpeta_salida: Path) -> int:
    """Genera datos simulados, analiza el salto y produce reportes."""
    datos = generar_datos_demo()
    datos_analizados, resumen = analizar_salto(datos)
    archivos = generar_salidas(datos_analizados, resumen, carpeta_salida, fuente="Demostración con datos simulados")
    print("\nDemostración completada correctamente.")
    for nombre, ruta in archivos.items():
        print(f"- {nombre}: {ruta}")
    return 0


def ejecutar_video(ruta_video: Path, carpeta_salida: Path, ruta_modelo: Path, generar_video_anotado: bool) -> int:
    """Procesa un video real y genera métricas y reportes."""
    validar_ruta_video(ruta_video)
    from src.pose_detector import procesar_video
    datos = procesar_video(ruta_video, ruta_modelo, carpeta_salida, generar_video_anotado)
    datos_analizados, resumen = analizar_salto(datos)
    archivos = generar_salidas(datos_analizados, resumen, carpeta_salida, fuente=str(ruta_video))
    print("\nAnálisis completado correctamente.")
    for nombre, ruta in archivos.items():
        print(f"- {nombre}: {ruta}")
    return 0


def main() -> int:
    """Ejecuta la aplicación y transforma errores en mensajes claros."""
    args = crear_parser().parse_args()
    try:
        if args.demo:
            return ejecutar_demo(args.salida)
        return ejecutar_video(args.video, args.salida, args.modelo, not args.sin_video_anotado)
    except (FileNotFoundError, ValueError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nProceso cancelado por el usuario.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
