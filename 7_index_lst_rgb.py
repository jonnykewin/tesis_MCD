import os
os.environ['PROJ_LIB'] = '/Applications/QGIS-LTR.app/Contents/Resources/proj'
os.environ['GDAL_DATA'] = '/Applications/QGIS-LTR.app/Contents/Resources/gdal'

import sys
sys.path.append('/Applications/QGIS-LTR.app/Contents/Resources/python')
sys.path.append('/Applications/QGIS-LTR.app/Contents/Resources/python/plugins')

from qgis.core import QgsApplication
QgsApplication.setPrefixPath("/Applications/QGIS-LTR.app/Contents/MacOS", True)
qgs = QgsApplication([], False)
qgs.initQgis()

import processing
from processing.core.Processing import Processing
Processing.initialize()

from qgis.analysis import QgsNativeAlgorithms
provider = QgsNativeAlgorithms()
if not any(p.name() == provider.name() for p in QgsApplication.processingRegistry().providers()):
    QgsApplication.processingRegistry().addProvider(provider)

path = '/Users/jonny.sanchez/Documents/tesis/7-index_lst_rgb/cartagena'

for folder_name in os.listdir(path):
    folder_path = os.path.join(path,folder_name)
    if os.path.isdir(folder_path):
        b3_file = None
        b4_file = None
        b5_file = None
        b6_file = None
        b10_file = None
        for file_name in os.listdir(folder_path):
            if file_name.endswith("B2.TIF"):
                b2_file = os.path.join(folder_path,file_name)
            elif file_name.endswith("B3.TIF"):
                b3_file = os.path.join(folder_path,file_name)
            elif file_name.endswith("B4.TIF"):
                b4_file = os.path.join(folder_path,file_name)  
            elif file_name.endswith("B5.TIF"):
                b5_file = os.path.join(folder_path,file_name)
            elif file_name.endswith("B6.TIF"):
                b6_file = os.path.join(folder_path,file_name)
            elif file_name.endswith("B8.TIF"):
                b8_file = os.path.join(folder_path,file_name)
            elif file_name.endswith("B10.TIF"):
                b10_file = os.path.join(folder_path,file_name)  

        ndvi = os.path.join(folder_path, "NDVI.TIF")
        ndbi = os.path.join(folder_path, "NDBI.TIF")
        ndwi = os.path.join(folder_path, "NDWI.TIF")
        lst = os.path.join(folder_path, "LST.TIF")
        rgb = os.path.join(folder_path, "RGB.TIF")
        rgb_pan = os.path.join(folder_path, "RGB_pansharp.TIF")

        formula = f"((B-A)/(B+A))"
        formula_lst = f"(A) - 273.15" #https://www.usgs.gov/landsat-missions/landsat-collection-2-surface-temperature ya los datos se encontraban en LST en Kelvin se convierte a C

        processing.run("gdal:rastercalculator", {
                        'INPUT_A':b4_file,
                        'BAND_A':1,
                        'INPUT_B':b5_file,
                        'BAND_B':1,
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
                        'OUTPUT':ndvi})
        
        print(f"Procesado: {ndvi}")
        
        processing.run("gdal:rastercalculator", {
                        'INPUT_A':b5_file,
                        'BAND_A':1,
                        'INPUT_B':b6_file,
                        'BAND_B':1,
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
                        'OUTPUT':ndbi})
        
        print(f"Procesado: {ndbi}")
        
        processing.run("gdal:rastercalculator", {
                        'INPUT_A':b5_file,
                        'BAND_A':1,
                        'INPUT_B':b3_file,
                        'BAND_B':1,
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
                        'OUTPUT':ndwi})
        
        print(f"Procesado: {ndwi}")
        
        processing.run("gdal:rastercalculator", {
                        'INPUT_A':b10_file,
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
                        'FORMULA':formula_lst,
                        'NO_DATA':None,
                        'EXTENT_OPT':0,
                        'PROJWIN':None,
                        'RTYPE':5,
                        'OPTIONS':'',
                        'EXTRA':'',
                        'OUTPUT':lst})
                        
        print(f"Procesado: {lst}")

        processing.run("gdal:merge", {
                        'INPUT':[b2_file,b3_file,b4_file],
                        'PCT':False,
                        'SEPARATE':True,
                        'NODATA_INPUT':None,
                        'NODATA_OUTPUT':None,
                        'OPTIONS':'',
                        'EXTRA':'',
                        'DATA_TYPE':5,
                        'OUTPUT':rgb})
        
        print(f"Procesado: {rgb}")

        processing.run("gdal:pansharp", {
                        'SPECTRAL':rgb,
                        'PANCHROMATIC':b8_file,
                        'RESAMPLING':2,
                        'OPTIONS':'',
                        'EXTRA':'',
                        'OUTPUT':rgb_pan})
        
        print(f"Procesado: {rgb_pan}")

qgs.exitQgis()
