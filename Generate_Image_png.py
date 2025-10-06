import os, re, numpy as np, rasterio
import matplotlib.pyplot as plt
from rasterio.enums import Resampling
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch

BASE_PATH = "/Users/jonny.sanchez/Documents/tesis/8-classification"
OUTPUT_ROOT = os.path.join(BASE_PATH, "image")

COLORS = {0: "#1592ab", 1: "#35c5e2", 2: "#b53035", 3: "#ffffff", 4: "#ba9272", 5: "#1dba4f",}
LABELS = {0:"Agua de mar", 1:"Agua dulce", 2:"Construcciones", 3:"Nubes", 4:"Suelo desnudo", 5:"Vegetación",}

def save_png(tif_path, out_png, city, anio_file):
    with rasterio.open(tif_path) as src:
        arr = src.read(1, resampling=Resampling.nearest)
        nodata = src.nodata
    
    classes = sorted(set(np.unique(arr)) & set(COLORS))
    if not classes:
        raise ValueError("No hay clases válidas en el raster.")

    cmap = ListedColormap([COLORS[c] for c in classes])
    edges = np.array(classes, dtype=float)
    boundaries = np.r_[edges - 0.5, edges[-1] + 0.5]
    norm = BoundaryNorm(boundaries, cmap.N)
    alpha = None
    if nodata is not None:
        alpha = np.where(arr == nodata, 0.0, 1.0)
        arr = np.where(arr == nodata, classes[0], arr)

    fig = plt.figure(figsize=(8,6), dpi=300)
    ax = plt.axes([0,0,1,1]); ax.set_axis_off()
    ax.imshow(arr, cmap=cmap, norm=norm, interpolation="nearest", alpha=alpha)

    title = f"Clasificación Coberturas {city} {anio_file}"
    ax.text(0.01, 0.99, 
            title,
            transform=ax.transAxes,
            va="top", ha="left",
            multialignment="left",
            fontsize=6, fontweight="bold",
            bbox=dict(facecolor="white", alpha=0.7, edgecolor="none", pad=3))

    handles = [Patch(facecolor=COLORS[c], edgecolor="black", label=LABELS[c]) for c in classes]
    leg = ax.legend(handles=handles,
            loc="upper left",
            bbox_to_anchor=(0.0, 0.97),
            frameon=True,
            framealpha=0.7,
            edgecolor="black",
            fontsize=5,
            labelspacing=0.25,
            borderpad=0.3,
            handlelength=0.9,
            handletextpad=0.4,)
    for p in leg.get_patches(): p.set_linewidth(0.5)

    plt.savefig(out_png, bbox_inches="tight", pad_inches=0, transparent=True)
    plt.close(fig)

path_output = None
for folder in os.listdir(BASE_PATH):
    folder_path = os.path.join(BASE_PATH, folder)
    if folder.startswith('.') or not os.path.isdir(folder_path):
        continue
    path_output = os.path.join(OUTPUT_ROOT,folder)
    os.makedirs(os.path.dirname(path_output), exist_ok=True)
    for folder_name in os.listdir(folder_path):
        subfolder_path = os.path.join(folder_path, folder_name)
        if folder_name.startswith('.') or not os.path.isdir(subfolder_path):
            continue
        print(subfolder_path)
        base = os.path.basename(subfolder_path)
        date = base.split(sep='_')[3]
        anio_file = int(date[0:4])
        file_image = None
        file_output = None
        for file_name in os.listdir(subfolder_path):
            if file_name.endswith('Land_Cover_ExtraTrees.TIF'):
                file_image = os.path.join(subfolder_path,file_name)
                file_output = os.path.join(path_output,"{}_Clasificacion_Coberturas.png".format(anio_file))
                os.makedirs(os.path.dirname(file_output), exist_ok=True)
                save_png(file_image,file_output,folder,anio_file)