import os
import processing
from qgis.core import QgsCoordinateReferenceSystem

path = 'C:/Users/Admin/Documents/MAESTRIA/TESIS/insumos'

for folder_name in os.listdir(path):
    folder_path = os.path.join(path,folder_name)
    if os.path.isdir(folder_path):
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".TIF"):
                input_file = os.path.join(folder_path, file_name)
                temp_file = os.path.join(folder_path, "temp_output.TIF")
                
                processing.run("gdal:warpreproject", {
                    'INPUT': input_file,
                    'SOURCE_CRS': None,
                    'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:9377'),
                    'RESAMPLING': 0,  # Vecino más cercano
                    'NODATA': None,  
                    'TARGET_RESOLUTION': None,  # Mantener resolución original
                    'OPTIONS': '',  
                    'DATA_TYPE': 0, 
                    'TARGET_EXTENT': None,  
                    'TARGET_EXTENT_CRS': None,  
                    'MULTITHREADING': False,  
                    'EXTRA': '',  
                    'OUTPUT': temp_file 
                })
                
                os.replace(temp_file, input_file)
                print(f"Procesado: {input_file}")