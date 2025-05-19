import os
import geopandas as gpd
import processing

file_gpkg = "C:/Users/Admin/Documents/MAESTRIA/TESIS/cartagena.gpkg"
feature = "bounding_box"
path = 'C:/Users/Admin/Documents/MAESTRIA/TESIS/insumos'

def bounding_box(file_gpkg , feature):
    gdf = gpd.read_file(file_gpkg, layer = feature)
    bbox = gdf.total_bounds
    return bbox

xmin, ymin, xmax, ymax = bounding_box(file_gpkg,feature)

for folder_name in os.listdir(path):
    folder_path = os.path.join(path,folder_name)
    if os.path.isdir(folder_path):
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".TIF"):
                input_file = os.path.join(folder_path, file_name)
                temp_file = os.path.join(folder_path, "temp_output.TIF")

                processing.run("gdal:cliprasterbyextent", {
                                'INPUT': input_file,
                                'PROJWIN': f"{xmin},{xmax},{ymax},{ymin}",  # Coordenadas transformadas
                                'NODATA': None,  # Sin valor nodata
                                'OPTIONS': '',  # Opciones adicionales de GDAL
                                'DATA_TYPE': 0,  # Mantener tipo de datos original
                                'OUTPUT': temp_file  # Archivo de salida
                                }
                                )
                os.replace(temp_file, input_file)
                print(f"Procesado: {path_file}")