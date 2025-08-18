
from pathlib import Path
import geopandas as gpd
from sqlalchemy import create_engine, text
import fiona, re
import unicodedata

# ========= CONFIGURA AQUÍ =========
BASE_DIR = Path("/home/rohi/Documents/maestria/santa_marta")  # raíz donde buscar recursivamente
GPKG_FILENAME = "estaciones_meteorologicas_final.gpkg"
LAYER_NAME = None  # si sabes el nombre exacto de la capa; si no, autodetecta


PG_USER = "postgres"
PG_PASS = "admi"
PG_HOST = "localhost"
PG_PORT = 5432
PG_DB   = "maestria"

SCHEMA  = "estaciones_nuevas"  # esquema destino
FORCE_CRS = None        # ej. 4326 si los GPKG no traen CRS
TO_CRS    = None        # ej. 4326 para unificar proyección
CREATE_INDEXES = True   # crea índices al terminar cada tabla
# ===================================

def slugify(s: str) -> str:
    out = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode("ascii")
    out = re.sub(r"[^a-zA-Z0-9_-]+", "_", out.strip())
    out = re.sub(r"_+", "_", out).strip("_")
    return out.lower()

def detect_layer(gpkg_path: Path) -> str:
    if LAYER_NAME:
        return LAYER_NAME
    layers = fiona.listlayers(gpkg_path.as_posix())
    if not layers:
        raise RuntimeError(f"Sin capas en {gpkg_path}")
    for lyr in layers:
        if re.search(r"estaciones", lyr, re.IGNORECASE):
            return lyr
    return layers[0]

def parse_ciudad_anio_from_path(gpkg_path: Path):
    """
    Busca un directorio 'anio' (4 dígitos) en el path y toma la carpeta anterior como 'ciudad'.
    Ej: .../santa_marta/2015/LC08.../estaciones_meteorologicas_final.gpkg -> ('santa_marta', 2015)
    """
    parts = list(gpkg_path.resolve().parts)
    for i, p in enumerate(parts):
        if re.fullmatch(r"\d{4}", p):
            anio = int(p)
            ciudad = parts[i-1] if i-1 >= 0 else None
            return ciudad, anio
    return None, None

def ensure_schema(engine, schema: str):
    with engine.begin() as conn:
        conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}";'))

def create_indexes(engine, schema: str, table: str):
    # Índices útiles si las columnas existen
    stmts = [
        f'CREATE INDEX IF NOT EXISTS idx_{table}_ciudad ON "{schema}"."{table}" (ciudad);',
        f'CREATE INDEX IF NOT EXISTS idx_{table}_anio   ON "{schema}"."{table}" (anio);'
    ]
    with engine.begin() as conn:
        for s in stmts:
            try:
                conn.execute(text(s))
            except Exception:
                pass

def main():
    PG_CONN = f"postgresql://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}"
    engine = create_engine(PG_CONN)
    ensure_schema(engine, SCHEMA)

    gpkg_files = list(BASE_DIR.rglob(GPKG_FILENAME))
    print(f"Encontrados {len(gpkg_files)} archivos '{GPKG_FILENAME}' bajo {BASE_DIR}")

    # Para controlar replace/append por (ciudad, anio)
    seen = set()
    total = 0

    for gpkg in sorted(gpkg_files):
        try:
            layer = detect_layer(gpkg)
            gdf = gpd.read_file(gpkg.as_posix(), layer=layer)

            ciudad, anio = parse_ciudad_anio_from_path(gpkg)
            if ciudad is None or anio is None:
                print(f"✗ Omitido (no pude inferir ciudad/año): {gpkg}")
                continue

            # Añadir columnas contexto si no existen
            if "ciudad" not in gdf.columns:
                gdf["ciudad"] = ciudad
            if "anio" not in gdf.columns:
                gdf["anio"] = anio

            # CRS
            if gdf.crs is None and FORCE_CRS:
                gdf = gdf.set_crs(FORCE_CRS, allow_override=True)
            if TO_CRS:
                gdf = gdf.to_crs(TO_CRS)

            # Tabla por ciudad-año
            table_name = f"estaciones_meteorologicas_final_{slugify(ciudad)}_{anio}"

            # replace en el primer encuentro de esa tabla; luego append
            mode = "replace" if (ciudad, anio) not in seen else "append"
            gdf.to_postgis(table_name, engine, schema=SCHEMA, if_exists=mode, index=False)

            if CREATE_INDEXES and mode == "replace":
                create_indexes(engine, SCHEMA, table_name)

            seen.add((ciudad, anio))
            total += len(gdf)
            print(f"✓ {mode.upper():8s} -> {SCHEMA}.{table_name:40s} filas={len(gdf)}  ({gpkg.name})")

        except Exception as e:
            print(f"✗ Error importando {gpkg}: {e}")

    print(f"Listo. Filas totales importadas: {total}. Tablas creadas/actualizadas: {len(seen)}")

if __name__ == "__main__":
    main()
