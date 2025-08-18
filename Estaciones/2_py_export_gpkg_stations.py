from pathlib import Path
import geopandas as gpd
import pandas as pd
from sqlalchemy import create_engine
import unicodedata, re

# ==== CONFIG (EDITA AQUÍ) ====
PG_USER = "postgres"
PG_PASS = "admi"
PG_HOST = "localhost"
PG_PORT = 5432
PG_DB   = "maestria"

SCHEMA = "estaciones"
TABLE = "estaciones_consolidadas"
COL_CIUDAD = "ciudad"
COL_FECHA  = "fecha_toma"
COL_GEOM   = "geometria"

SALIDA_BASE = Path("/home/rohi/Documents/maestria")  # p.ej. /home/rohi/exports_estaciones
FORCE_CRS = 4326   # EPSG si tu geometría no trae CRS (None para no forzar)
TO_CRS    = None   # EPSG al que quieres reproyectar (None para no reproyectar)
# ==============================

def slugify(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-zA-Z0-9_-]+", "_", s.strip())
    s = re.sub(r"_+", "_", s).strip("_")
    return s.lower()

# Construir la cadena de conexión y engine
PG_CONN = f"postgresql://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}"
engine = create_engine(PG_CONN)

# Crear carpeta base
SALIDA_BASE.mkdir(parents=True, exist_ok=True)

# 1) Listar combinaciones ciudad-año
sql_listado = f"""
    SELECT {COL_CIUDAD} AS ciudad,
           EXTRACT(YEAR FROM {COL_FECHA})::int AS anio,
           COUNT(*) AS n
    FROM {SCHEMA}.{TABLE}
    WHERE {COL_FECHA} IS NOT NULL
    GROUP BY 1,2
    ORDER BY 1,2;
"""
df_idx = pd.read_sql(sql_listado, engine)

# 2) Exportar por ciudad-año
for _, row in df_idx.iterrows():
    ciudad = row["ciudad"]
    anio = int(row["anio"])
    if ciudad is None:
        continue

    # Carpeta /salida/Ciudad/Año
    carpeta = SALIDA_BASE / str(ciudad) / str(anio)
    carpeta.mkdir(parents=True, exist_ok=True)

    # Nombre fijo de archivo y capa
    gpkg_path = carpeta / "estaciones_meteorologicas.gpkg"
    layer_name = "estaciones_meteorologicas"

    # Subconjunto por ciudad-año
    sql_subset = f"""
        SELECT *
        FROM {SCHEMA}.{TABLE}
        WHERE {COL_CIUDAD} = %(ciudad)s
          AND EXTRACT(YEAR FROM {COL_FECHA}) = %(anio)s;
    """
    gdf = gpd.read_postgis(sql_subset, engine, geom_col=COL_GEOM,
                           params={"ciudad": ciudad, "anio": anio})

    if gdf.empty:
        continue

    # Manejo de CRS
    if gdf.crs is None and FORCE_CRS:
        gdf = gdf.set_crs(FORCE_CRS, allow_override=True)
    if TO_CRS:
        gdf = gdf.to_crs(TO_CRS)

    # Exportar a GeoPackage con nombre fijo
    gdf.to_file(gpkg_path, layer=layer_name, driver="GPKG")
    print(f"Exportado: {gpkg_path} ({len(gdf)} features)")

print("Proceso finalizado.")
