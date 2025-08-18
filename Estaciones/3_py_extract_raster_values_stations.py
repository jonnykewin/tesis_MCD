import os
import processing
from qgis.core import QgsVectorLayer

# === CONFIG ===
ruta_raiz = '/home/rohi/Documents/maestria/'  # <-- ajusta si hace falta
gpkg_nombre = 'estaciones_meteorologicas.gpkg'
gpkg_final  = 'estaciones_meteorologicas_final.gpkg'

# Raster -> (nombre_archivo, prefijo_columna)
rasteres_def = [
    ('LST.TIF',             'lst'),
    ('c0_sea_water.TIF',    'sea_water'),
    ('c1_fresh_water.TIF',   'fresh_water'),
    ('c2_builds.TIF',       'builds'),
    ('c3_clouds.TIF',       'clouds'),
    ('c4_bare_ground.TIF',  'bare'),
    ('c5_vegetation.TIF',   'veg'),
    ('NDBI.TIF',            'ndbi'),
    ('NDWI.TIF',            'ndwi'),
    ('NDVI.TIF',            'ndvi'),
    ('ST_EMIS.TIF',         'st_emissivity')
]

def find_case_insensitive(root, target_name):
    """Devuelve la ruta al archivo cuyo basename coincide con target_name ignorando mayúsculas/minúsculas."""
    t = target_name.lower()
    for f in os.listdir(root):
        if f.lower() == t:
            return os.path.join(root, f)
    return None

for root, dirs, files in os.walk(ruta_raiz):
    if gpkg_nombre in files:
        print(f"\n🔍 Carpeta: {root}")
        gpkg_inicial = os.path.join(root, gpkg_nombre)
        gpkg_actual  = gpkg_inicial
        gpkg_salida_final = os.path.join(root, gpkg_final)

        # Cargar capa base como objeto
        vlayer = QgsVectorLayer(gpkg_actual, "base", "ogr")
        if not vlayer.isValid():
            print(f"❌ No se pudo abrir {gpkg_actual} como capa vectorial.")
            continue
        print(f"✅ Capa base cargada: {vlayer.name()}")

        intermedios = []
        vistos = set()

        for i, (r_name, pref) in enumerate(rasteres_def, start=1):
            if r_name in vistos:
                print(f"↪️  Duplicado ignorado: {r_name}")
                continue
            vistos.add(r_name)

            raster_path = find_case_insensitive(root, r_name)
            if not raster_path or not os.path.exists(raster_path):
                print(f"⚠️ No encontrado: {r_name} (se omite)")
                continue

            # ¿Es el último raster presente? Si sí, escribir al final; si no, a un tmp intermedio
            ultimo = (i == len(rasteres_def))
            salida_path = gpkg_salida_final if ultimo else os.path.join(root, f'_tmp_{pref}.gpkg')

            # Si ya existe, reemplazar
            if os.path.exists(salida_path):
                try: os.remove(salida_path)
                except Exception: pass

            print(f"🌀 Muestreando: {os.path.basename(raster_path)}  →  {os.path.basename(salida_path)}  (prefijo='{pref}_')")

            try:
                processing.run("native:rastersampling", {
                    'INPUT': vlayer,                 # ← objeto capa, no string
                    'RASTERCOPY': raster_path,
                    'COLUMN_PREFIX': pref,           # QGIS añade '_' automáticamente
                    'OUTPUT': salida_path
                }, is_child_algorithm=True)

                if salida_path != gpkg_salida_final:
                    intermedios.append(salida_path)

                # Preparar siguiente iteración: recargar como capa para encadenar columnas
                vlayer = QgsVectorLayer(salida_path, "intermedio", "ogr")
                if not vlayer.isValid():
                    raise Exception("Salida intermedia inválida; no se pudo recargar como capa.")

            except Exception as e:
                print(f"❌ Error con {r_name}: {e}")
                # seguir con el siguiente raster
                continue

        # Limpiar intermedios
        for tmp in intermedios:
            try:
                os.remove(tmp)
                print(f"🗑️ Eliminado intermedio: {os.path.basename(tmp)}")
            except Exception as e:
                print(f"⚠️ No se pudo eliminar {tmp}: {e}")

        if os.path.exists(gpkg_salida_final):
            print(f"✅ Finalizado: {gpkg_salida_final}")
        else:
            print("ℹ️ No se generó archivo final (faltaron rasters o hubo errores).")

print("\n🎯 Proceso completado.")
