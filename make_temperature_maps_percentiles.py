#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mapas de temperatura con paleta CONSISTENTE por ciudad (percentiles robustos).
- Busca recursivamente Temperature_ExtraTrees.TIF bajo BASE_PATH.
- Calcula P_LOW/P_HIGH por ciudad usando un histograma acumulado (robusto y estable).
- Guarda JSON con los rangos por ciudad (redondeados a un step configurable).
- Renderiza PNGs usando vmin/vmax fijos por ciudad (comparabilidad interanual).

Requisitos: rasterio, numpy, matplotlib
"""
import os, re, json, math
from pathlib import Path
import numpy as np
import rasterio
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# ========= PALETA (continua) =========
# Se estira entre vmin y vmax por ciudad
CUSTOM_COLORS = ["#2b83ba", "#abdda4", "#ffffbf", "#fdae61", "#c80606"]
CUSTOM_CMAP = LinearSegmentedColormap.from_list("temp_city_adapt", CUSTOM_COLORS)

# ============== CONFIG EDITABLE ==============
BASE_PATH   = r"/home/rohi/Downloads/maestria/10-heat_island"   # ← Tu raíz
OUTPUT_ROOT = os.path.join(BASE_PATH, "image_temperature_percentil")       # donde guardar PNGs y config
FILENAME    = "Temperature_ExtraTrees.TIF"                        # nombre del raster de temperatura

# Percentiles robustos por ciudad (sobre TODOS los años)
P_LOW  = 2.0
P_HIGH = 98.0

# Redondeo final de vmin/vmax para lectura agradable
ROUND_STEP = 0.5   # 0.5°C; puedes usar 0.2, 1.0, etc.

# Histograma para percentiles robustos (más estable que promediar percentiles por archivo)
HIST_BINS = 512    # si tus datos son muy ruidosos, sube a 1024
# ============================================

CBAR_LABEL = "Temperatura (°C)"
RGX_YEAR_ANY = re.compile(r"(19|20)\d{2}")
RGX_CITY = re.compile(r"(barranquilla|cartagena|santa[_\s-]*marta)", re.IGNORECASE)

def infer_city_year_from_path(p: Path):
    text = " ".join(p.parts)
    # ciudad
    mcity = RGX_CITY.search(text)
    if mcity:
        city = mcity.group(1).replace("_", " ").replace("-", " ").title()
    else:
        city = "Ciudad"
    # año
    myear = RGX_YEAR_ANY.search(text)
    year = myear.group(0) if myear else "YYYY"
    return city, year

def find_city_files(base: Path):
    """Devuelve dict {city: [paths]} con todos los TIF por ciudad."""
    by_city = {}
    for root, dirs, files in os.walk(base):
        files_lower = {f.lower(): f for f in files}
        tif_path = None
        if FILENAME in files:
            tif_path = Path(root) / FILENAME
        elif FILENAME.lower() in files_lower:
            tif_path = Path(root) / files_lower[FILENAME.lower()]
        else:
            continue
        city, _ = infer_city_year_from_path(Path(root))
        by_city.setdefault(city, []).append(tif_path)
    return by_city

def pass_min_max(paths):
    """Primer pase: obtiene (min, max) globales a lo bruto (ignorando NoData) para predefinir bins."""
    gmin, gmax = math.inf, -math.inf
    total_valid = 0
    for p in paths:
        with rasterio.open(p) as src:
            arr = src.read(1, masked=True).astype(np.float32)
            if arr.count() == 0:
                continue
            dmin = float(arr.min())
            dmax = float(arr.max())
            if dmin < gmin: gmin = dmin
            if dmax > gmax: gmax = dmax
            total_valid += int(arr.count())
    if not np.isfinite(gmin) or not np.isfinite(gmax) or total_valid == 0:
        return None, None, 0
    # Acolchado leve para evitar cortar extremos reales por binning
    pad = 1e-3 * max(abs(gmin), abs(gmax), 1.0)
    return gmin - pad, gmax + pad, total_valid

def percentile_from_hist(hist, edges, q):
    """Devuelve el cuantil q (0..1) a partir de un histograma acumulado."""
    c = np.cumsum(hist)
    if c[-1] == 0:
        return np.nan
    target = q * c[-1]
    idx = np.searchsorted(c, target)
    idx = np.clip(idx, 0, len(edges)-2)
    # Interpolación lineal dentro del bin
    c_prev = 0 if idx == 0 else c[idx-1]
    frac = 0 if hist[idx] == 0 else (target - c_prev) / hist[idx]
    return edges[idx] + frac * (edges[idx+1] - edges[idx])

def compute_city_ranges_percentiles(by_city):
    """Calcula percentiles P_LOW/P_HIGH por ciudad usando histograma acumulado (dos pases)."""
    ranges = {}
    for city, paths in by_city.items():
        if not paths:
            continue
        vmin0, vmax0, cnt = pass_min_max(paths)
        if cnt == 0 or vmin0 is None or vmax0 is None or not np.isfinite(vmin0) or not np.isfinite(vmax0):
            continue
        edges = np.linspace(vmin0, vmax0, HIST_BINS + 1, dtype=np.float64)
        hist = np.zeros(HIST_BINS, dtype=np.float64)
        for p in paths:
            with rasterio.open(p) as src:
                arr = src.read(1, masked=True).astype(np.float32)
                data = arr.compressed()
                if data.size == 0:
                    continue
                h, _ = np.histogram(data, bins=edges)
                hist += h
        lo = percentile_from_hist(hist, edges, P_LOW / 100.0)
        hi = percentile_from_hist(hist, edges, P_HIGH / 100.0)
        if not np.isfinite(lo) or not np.isfinite(hi) or lo == hi:
            # fallback a min/max crudos
            lo, hi = vmin0, vmax0
        # Redondeo agradable
        def nice_round(v, step=ROUND_STEP):
            return round(v / step) * step
        lo_r = nice_round(lo, ROUND_STEP)
        hi_r = nice_round(hi, ROUND_STEP)
        # Asegurar separación mínima
        if hi_r <= lo_r:
            hi_r = lo_r + ROUND_STEP
        ranges[city] = {"vmin": float(lo_r), "vmax": float(hi_r)}
    return ranges

def save_config(config: dict, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    cfg_path = output_dir / "palette_ranges_per_city.json"
    with open(cfg_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    return cfg_path

def render_all_maps(base: Path, ranges: dict, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for root, dirs, files in os.walk(base):
        files_lower = {f.lower(): f for f in files}
        if "Temperature_ExtraTrees.TIF" in files:
            tif_path = Path(root) / "Temperature_ExtraTrees.TIF"
        elif "temperature_extratrees.tif" in files_lower:
            tif_path = Path(root) / files_lower["temperature_extratrees.tif"]
        else:
            continue

        city, year = infer_city_year_from_path(Path(root))
        if city not in ranges:
            continue
        vmin = ranges[city]["vmin"]
        vmax = ranges[city]["vmax"]

        with rasterio.open(tif_path) as src:
            arr = src.read(1, masked=True).astype(np.float32)
            data = arr.filled(np.nan)

        h, w = data.shape
        fig_w = 8
        fig_h = fig_w * h / w
        fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=300, constrained_layout=True)
        im = ax.imshow(data, cmap=CUSTOM_CMAP, vmin=vmin, vmax=vmax)
        ax.set_axis_off()
        title = f"Temperatura — {city} {year}"
        ax.set_title(title, fontsize=10, weight="bold")

        cbar = fig.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
        cbar.set_label("Temperatura (°C)", fontsize=8)
        try:
            import matplotlib.ticker as mticker
            cbar.ax.yaxis.set_major_locator(mticker.MaxNLocator(7))
        except Exception:
            pass

        city_dir = Path(output_dir) / city
        city_dir.mkdir(parents=True, exist_ok=True)
        out_name = f"{year}_Temperature.png"
        out_path = city_dir / out_name
        fig.savefig(out_path, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        count += 1
    return count

def run():
    base = Path(BASE_PATH)
    out_dir = Path(OUTPUT_ROOT)

    # 1) Agrupar archivos por ciudad
    by_city = find_city_files(base)
    if not by_city:
        print(f"[!] No se encontraron archivos '{FILENAME}' bajo {BASE_PATH}")
        return

    # 2) Calcular percentiles robustos por ciudad (y redondear)
    ranges = compute_city_ranges_percentiles(by_city)
    cfg_path = save_config(ranges, out_dir)
    print(f"Config de paleta guardada en: {cfg_path}")
    for city, rr in ranges.items():
        print(f"  {city}: vmin={rr['vmin']:.2f}, vmax={rr['vmax']:.2f} (P{P_LOW}–P{P_HIGH}, step={ROUND_STEP})")

    # 3) Renderizar mapas con esos rangos
    n = render_all_maps(base, ranges, out_dir)
    print(f"Mapas generados: {n}")

if __name__ == "__main__":
    run()
