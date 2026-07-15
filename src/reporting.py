"""Generación de archivos tabulares, gráficos y conclusión técnica."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.validation import preparar_carpeta


def _crear_conclusion(resumen: dict) -> str:
    """Construye una conclusión prudente a partir de las métricas."""
    if not resumen.get("jump_detected"):
        return "No se detectó un salto con los criterios configurados."
    return (
        "Se detectó un patrón compatible con un salto. "
        f"La calidad de detección fue {resumen.get('quality_assessment')}. "
        f"El tiempo de vuelo estimado fue {resumen.get('estimated_flight_time_s')} s. "
        "Las métricas son aproximaciones cinemáticas y deben interpretarse "
        "junto con observación profesional y herramientas validadas."
    )


def generar_salidas(
    datos: pd.DataFrame,
    resumen: dict,
    carpeta_salida: Path,
    fuente: str,
) -> dict[str, Path]:
    """Exporta resultados a CSV, JSON, Excel, imágenes y texto."""
    carpeta = preparar_carpeta(carpeta_salida)
    rutas = {
        "metricas_csv": carpeta / "metricas_por_frame.csv",
        "resumen_csv": carpeta / "resumen_salto.csv",
        "resumen_json": carpeta / "resumen_salto.json",
        "excel": carpeta / "informe_salto.xlsx",
        "grafico_cadera": carpeta / "grafico_desplazamiento_cadera.png",
        "grafico_rodillas": carpeta / "grafico_angulos_rodilla.png",
        "conclusion": carpeta / "conclusion.txt",
    }
    datos.to_csv(rutas["metricas_csv"], index=False)
    resumen_tabla = pd.DataFrame([{"fuente": fuente, **resumen}])
    resumen_tabla.to_csv(rutas["resumen_csv"], index=False)
    rutas["resumen_json"].write_text(
        json.dumps({"fuente": fuente, **resumen}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    with pd.ExcelWriter(rutas["excel"], engine="openpyxl") as escritor:
        resumen_tabla.to_excel(escritor, sheet_name="Resumen", index=False)
        datos.to_excel(escritor, sheet_name="Metricas", index=False)

    plt.figure(figsize=(10, 5))
    plt.plot(datos["time_s"], datos["hip_displacement_norm"])
    plt.xlabel("Tiempo (s)")
    plt.ylabel("Desplazamiento normalizado")
    plt.title("Desplazamiento vertical aproximado del centro de cadera")
    plt.tight_layout()
    plt.savefig(rutas["grafico_cadera"], dpi=160)
    plt.close()

    plt.figure(figsize=(10, 5))
    plt.plot(datos["time_s"], datos["left_knee_angle"], label="Rodilla izquierda")
    plt.plot(datos["time_s"], datos["right_knee_angle"], label="Rodilla derecha")
    plt.xlabel("Tiempo (s)")
    plt.ylabel("Ángulo (grados)")
    plt.title("Ángulos de rodilla durante el salto")
    plt.legend()
    plt.tight_layout()
    plt.savefig(rutas["grafico_rodillas"], dpi=160)
    plt.close()

    rutas["conclusion"].write_text(_crear_conclusion(resumen), encoding="utf-8")
    return rutas
