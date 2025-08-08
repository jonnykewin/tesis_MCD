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

path = '/Users/jonny.sanchez/Documents/tesis/5-clean_outliers/santa_marta'

formula= f"(A >= 0) * (A <= 2) * A + ((A < 0) + (A > 2)) * -9999"

for folder_name in os.listdir(path):
    folder_path = os.path.join(path,folder_name)
    if os.path.isdir(folder_path):
        for file_name in os.listdir(folder_path):
            list_sr = ["SR_B2.TIF","SR_B3.TIF","SR_B4.TIF","SR_B5.TIF","SR_B6.TIF","SR_B7.TIF","B8.TIF","ST_EMIS.TIF"]
            for sr in list_sr:
                if file_name.endswith(sr):
                    temp_file = os.path.join(folder_path,file_name)
                    temp_output = os.path.join(folder_path, f"CO_{file_name}")

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
                        'NO_DATA':-9999,
                        'EXTENT_OPT':0,
                        'PROJWIN':None,
                        'RTYPE':5,
                        'OPTIONS':'',
                        'EXTRA':'',
                        'OUTPUT':temp_output})
                    os.remove(temp_file)
                    print(f"Procesado: {temp_file}")

qgs.exitQgis()