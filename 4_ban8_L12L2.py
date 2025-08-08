import os
os.environ['PROJ_LIB'] = '/Applications/QGIS.app/Contents/Resources/proj'
os.environ['GDAL_DATA'] = '/Applications/QGIS.app/Contents/Resources/gdal'

import sys
sys.path.append('/Applications/QGIS.app/Contents/Resources/python')
sys.path.append('/Applications/QGIS.app/Contents/Resources/python/plugins')

from qgis.core import QgsApplication
QgsApplication.setPrefixPath("/Applications/QGIS.app/Contents/MacOS", True)
qgs = QgsApplication([], False)
qgs.initQgis()

import processing
from processing.core.Processing import Processing
Processing.initialize()

from qgis.analysis import QgsNativeAlgorithms
provider = QgsNativeAlgorithms()
if not any(p.name() == provider.name() for p in QgsApplication.processingRegistry().providers()):
    QgsApplication.processingRegistry().addProvider(provider)

import json
import math

path = '/Users/jonny.sanchez/Documents/tesis/4-b8_sr/santa_marta'

for folder_name in os.listdir(path):
    folder_path = os.path.join(path,folder_name)
    if os.path.isdir(folder_path):
        data = None
        temp_file = None
        temp_output = None
        for file_name in os.listdir(folder_path):
            if file_name.endswith("MTL.json"):
                json_file = os.path.join(folder_path,file_name)
                with open(json_file,'r') as json_file:
                    data = json.load(json_file)
            
            elif file_name.endswith("T1_B8.TIF"):
                temp_file = os.path.join(folder_path,file_name)
                temp_output = os.path.join(folder_path, f"SC_{file_name}")
      
        radiance_mult_band_8 = float(data["LANDSAT_METADATA_FILE"]["LEVEL1_RADIOMETRIC_RESCALING"]["RADIANCE_MULT_BAND_8"])
        radiance_add_band_8 = float(data["LANDSAT_METADATA_FILE"]["LEVEL1_RADIOMETRIC_RESCALING"]["RADIANCE_ADD_BAND_8"])
        reflectance_mult_band_8 = float(data["LANDSAT_METADATA_FILE"]["LEVEL1_RADIOMETRIC_RESCALING"]["REFLECTANCE_MULT_BAND_8"])
        reflectance_add_band_8 = float(data["LANDSAT_METADATA_FILE"]["LEVEL1_RADIOMETRIC_RESCALING"]["REFLECTANCE_ADD_BAND_8"])
        sun_elevation = float(data["LANDSAT_METADATA_FILE"]["IMAGE_ATTRIBUTES"]["SUN_ELEVATION"])
        earth_sun_distance = float(data["LANDSAT_METADATA_FILE"]["IMAGE_ATTRIBUTES"]["EARTH_SUN_DISTANCE"])
        sin_sun_elevation = math.sin(math.radians(sun_elevation))
        
        formula = f"(({reflectance_mult_band_8}*A + {reflectance_add_band_8})/ {sin_sun_elevation})"
        processing.run("gdal:rastercalculator", {
                        'INPUT_A':temp_file,
                        'BAND_A':1,
                        'INPUT_B':None,
                        'BAND_B':None,
                        'INPUT_C':None,
                        'BAND_C':None,
                        'INPUT_D':None,
                        'BAND_D':None,
                        'INPUT_E':None,
                        'BAND_E':None,
                        'INPUT_F':None,
                        'BAND_F':None,
                        'FORMULA':formula,
                        'NO_DATA':None,
                        'EXTENT_OPT':0,
                        'PROJWIN':None,
                        'RTYPE':5,
                        'OPTIONS':'',
                        'EXTRA':'',
                        'OUTPUT':temp_output})
                        
        os.remove(temp_file)
        print(f"Procesado: {temp_file}")

qgs.exitQgis()
