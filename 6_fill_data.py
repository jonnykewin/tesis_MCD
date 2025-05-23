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

path = '/Users/jonny.sanchez/Documents/tesis/6-fill_data/santa_marta'

for folder_name in os.listdir(path):
    folder_path = os.path.join(path,folder_name)
    if os.path.isdir(folder_path):
        for file_name in os.listdir(folder_path):
            list_sr = ["SR_B2.TIF","SR_B3.TIF","SR_B4.TIF","SR_B5.TIF","SR_B6.TIF","SR_B7.TIF","B8.TIF"]
            for sr in list_sr:
                if file_name.endswith(sr):
                    temp_file = os.path.join(folder_path,file_name)
                    #first_output = os.path.join(folder_path, f"FNGDAL_{file_name}")
                    second_output = os.path.join(folder_path, f"FN_{file_name}")
                    '''
                    processing.run("gdal:fillnodata", {
                    'INPUT':temp_file,
                    'BAND':1,
                    'DISTANCE':3,
                    'ITERATIONS':0,
                    'MASK_LAYER':None,
                    'OPTIONS':None,
                    'EXTRA':'',
                    'OUTPUT':first_output})
                    '''
                    processing.run("grass:r.fillnulls", {
                    'input':temp_file,
                    'method':1,
                    'tension':None,
                    'smooth':None,
                    'edge':3,
                    'npmin':600,
                    'segmax':300,
                    'lambda':None,
                    'output':second_output,
                    'GRASS_REGION_PARAMETER':None,
                    'GRASS_REGION_CELLSIZE_PARAMETER':0,
                    'GRASS_RASTER_FORMAT_OPT':'',
                    'GRASS_RASTER_FORMAT_META':''})
                    
                    os.remove(temp_file)
                    print(f"Procesado: {second_output}")

qgs.exitQgis()
