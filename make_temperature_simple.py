#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mapas de temperatura con paleta CONSISTENTE por ciudad (usando mínimo y máximo absolutos).
- Busca recursivamente Temperature_ExtraTrees.TIF bajo BASE_PATH.
- Calcula el valor mínimo y máximo por ciudad a partir de todos los archivos.
- Guarda un JSON con los rangos por ciudad.
- Renderiza PNGs usando vmin/vmax fijos por ciudad para asegurar comparabilidad interanual.

Requisitos: rasterio, numpy, matplotlib
"""
import os, re, json
from pathlib import Path
import numpy as np
import rasterio
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# ========= PALETA DE COLORES =========
CUSTOM_COLORS = ["#2b83ba", "#abdda4", "#ffffbf", "#fdae61", "#c80606"]
CUSTOM_CMAP = LinearSegmentedColormap.from_list("temp_city_adapt", CUSTOM_COLORS)
# =====================================

# ============== CONFIGURACIÓN ==============
BASE_PATH   = r"/home/rohi/Downloads/maestria/10-heat_island"  # Ruta raíz
OUTPUT_ROOT = os.path.join(BASE_PATH, "image_temperature_minmax")  # Carpeta de salida
FILENAME    = "Temperature_ExtraTrees.TIF"                      # Nombre del raster de temperatura

CBAR_LABEL  = "Temperatura (°C)"
# ===========================================

RGX_YEAR_ANY = re.compile(r"(19|20)\d{2}")
RGX_CITY = re.compile(r"(barranquilla|cartagena|santa[_\s-]*marta)", re.IGNORECASE)


def infer_city_year_from_path(p: Path):
    """Extrae el nombre de la ciudad y el año a partir de la ruta del archivo."""
    text = " ".join(p.parts)
    mcity = RGX_CITY.search(text)
    city = mcity.group(1).replace("_", " ").replace("-", " ").title() if mcity else "Ciudad"
    myear = RGX_YEAR_ANY.search(text)
    year = myear.group(0) if myear else "YYYY"
    return city, year


def compute_city_ranges(base: Path):
    """
    Busca los archivos de temperatura y calcula el mínimo y máximo por ciudad.
    Devuelve un diccionario con { ciudad: {vmin, vmax} }.
    """
    per_city = {}
    for root, dirs, files in os.walk(base):
        files_lower = {f.lower(): f for f in files}
        if FILENAME in files:
            tif_path = Path(root) / FILENAME
        elif FILENAME.lower() in files_lower:
            tif_path = Path(root) / files_lower[FILENAME.lower()]
        else:
            continue

        city, _ = infer_city_year_from_path(Path(root))
        with rasterio.open(tif_path) as src:
            arr = src.read(1, masked=True).astype(np.float32)
            data = arr.compressed()
            if data.size == 0:
                continue
            lo, hi = float(np.nanmin(data)), float(np.nanmax(data))

        if city not in per_city:
            per_city[city] = {"vmin": lo, "vmax": hi}
        else:
            per_city[city]["vmin"] = min(per_city[city]["vmin"], lo)
            per_city[city]["vmax"] = max(per_city[city]["vmax"], hi)
    return per_city


def save_config(config: dict, output_dir: Path):
    """Guarda el archivo JSON con los rangos por ciudad."""
    output_dir.mkdir(parents=True, exist_ok=True)
    cfg_path = output_dir / "palette_ranges_per_city.json"
    with open(cfg_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    return cfg_path


def render_all_maps(base: Path, ranges: dict, output_dir: Path):
    """Genera los mapas PNG usando vmin/vmax por ciudad."""
    output_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for root, dirs, files in os.walk(base):
        files_lower = {f.lower(): f for f in files}
        if FILENAME in files:
            tif_path = Path(root) / FILENAME
        elif FILENAME.lower() in files_lower:
            tif_path = Path(root) / files_lower[FILENAME.lower()]
        else:
            continue

        city, year = infer_city_year_from_path(Path(root))
        if city not in ranges:
            continue

        vmin, vmax = ranges[city]["vmin"], ranges[city]["vmax"]

        with rasterio.open(tif_path) as src:
            data = src.read(1, masked=True).astype(np.float32).filled(np.nan)

        h, w = data.shape
        fig_w = 8
        fig_h = fig_w * h / w
        fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=300, constrained_layout=True)
        im = ax.imshow(data, cmap=CUSTOM_CMAP, vmin=vmin, vmax=vmax)
        ax.set_axis_off()
        ax.set_title(f"Temperatura — {city} {year}", fontsize=10, weight="bold")

        cbar = fig.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
        cbar.set_label(CBAR_LABEL, fontsize=8)

        city_dir = Path(output_dir) / city
        city_dir.mkdir(parents=True, exist_ok=True)
        out_path = city_dir / f"{year}_Temperature.png"
        fig.savefig(out_path, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        count += 1
    return count


def run():
    base = Path(BASE_PATH)
    out_dir = Path(OUTPUT_ROOT)

    # Calcular los rangos (mínimo y máximo) por ciudad
    ranges = compute_city_ranges(base)
    cfg_path = save_config(ranges, out_dir)

    print(f"Archivo JSON guardado en: {cfg_path}")
    for city, rr in ranges.items():
        print(f"  {city}: vmin={rr['vmin']:.2f}, vmax={rr['vmax']:.2f}")

    # Generar mapas
    n = render_all_maps(base, ranges, out_dir)
    print(f"Mapas generados: {n}")


if __name__ == "__main__":
    run()

