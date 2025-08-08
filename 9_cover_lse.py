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

path = '/Users/jonny.sanchez/Documents/tesis/9-cover_density/santa_marta'

for folder_name in os.listdir(path):
    folder_path = os.path.join(path,folder_name)
    if os.path.isdir(folder_path):
        extra_trees_file = None
        for file_name in os.listdir(folder_path):
            if file_name.endswith("ExtraTrees.TIF"):
                extra_trees_file = os.path.join(folder_path,file_name)
        #{'Agua de mar': 0, 'Agua dulce': 1, 'Construcciones': 2, 'Nubes': 3, 'Suelo desnudo': 4, 'Vegetación': 5}
        cover_0_temp = os.path.join(folder_path, "c0.TIF")
        cover_1_temp = os.path.join(folder_path, "c1.TIF")
        cover_2_temp = os.path.join(folder_path, "c2.TIF")
        cover_3_temp = os.path.join(folder_path, "c3.TIF")
        cover_4_temp = os.path.join(folder_path, "c4.TIF")
        cover_5_temp = os.path.join(folder_path, "c5.TIF")
        
        cover_0 = os.path.join(folder_path, "c0_sea_water.TIF")
        cover_1 = os.path.join(folder_path, "c1_fresh_water.TIF")
        cover_2 = os.path.join(folder_path, "c2_builds.TIF")
        cover_3 = os.path.join(folder_path, "c3_clouds.TIF")
        cover_4 = os.path.join(folder_path, "c4_bare_ground.TIF")
        cover_5 = os.path.join(folder_path, "c5_vegetation.TIF")

        processing.run("gdal:rastercalculator", {
                        'INPUT_A':extra_trees_file,
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
                        'FORMULA':"A==0",
                        'NO_DATA':None,
                        'EXTENT_OPT':0,
                        'PROJWIN':None,
                        'RTYPE':5,
                        'OPTIONS':'',
                        'EXTRA':'',
                        'OUTPUT':cover_0_temp})

        processing.run("grass:r.neighbors", 
                        {'input':cover_0_temp,
                         'selection':None,
                         'method':0,
                         'size':5,
                         'gauss':None,
                         'quantile':'',
                         '-c':False,
                         '-a':False,
                         'weight':'',
                         'output':cover_0,
                         'GRASS_REGION_PARAMETER':None,
                         'GRASS_REGION_CELLSIZE_PARAMETER':0,
                         'GRASS_RASTER_FORMAT_OPT':'',
                         'GRASS_RASTER_FORMAT_META':''})
        
        os.remove(cover_0_temp)
        print(f"Procesado: {cover_0}")

        processing.run("gdal:rastercalculator", {
                        'INPUT_A':extra_trees_file,
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
                        'FORMULA':"A==1",
                        'NO_DATA':None,
                        'EXTENT_OPT':0,
                        'PROJWIN':None,
                        'RTYPE':5,
                        'OPTIONS':'',
                        'EXTRA':'',
                        'OUTPUT':cover_1_temp})

        processing.run("grass:r.neighbors", 
                        {'input':cover_1_temp,
                         'selection':None,
                         'method':0,
                         'size':5,
                         'gauss':None,
                         'quantile':'',
                         '-c':False,
                         '-a':False,
                         'weight':'',
                         'output':cover_1,
                         'GRASS_REGION_PARAMETER':None,
                         'GRASS_REGION_CELLSIZE_PARAMETER':0,
                         'GRASS_RASTER_FORMAT_OPT':'',
                         'GRASS_RASTER_FORMAT_META':''})
        
        os.remove(cover_1_temp)
        print(f"Procesado: {cover_1}")

        processing.run("gdal:rastercalculator", {
                        'INPUT_A':extra_trees_file,
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
                        'FORMULA':"A==2",
                        'NO_DATA':None,
                        'EXTENT_OPT':0,
                        'PROJWIN':None,
                        'RTYPE':5,
                        'OPTIONS':'',
                        'EXTRA':'',
                        'OUTPUT':cover_2_temp})

        processing.run("grass:r.neighbors", 
                        {'input':cover_2_temp,
                         'selection':None,
                         'method':0,
                         'size':5,
                         'gauss':None,
                         'quantile':'',
                         '-c':False,
                         '-a':False,
                         'weight':'',
                         'output':cover_2,
                         'GRASS_REGION_PARAMETER':None,
                         'GRASS_REGION_CELLSIZE_PARAMETER':0,
                         'GRASS_RASTER_FORMAT_OPT':'',
                         'GRASS_RASTER_FORMAT_META':''})
        
        os.remove(cover_2_temp)
        print(f"Procesado: {cover_2}")

        processing.run("gdal:rastercalculator", {
                        'INPUT_A':extra_trees_file,
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
                        'FORMULA':"A==3",
                        'NO_DATA':None,
                        'EXTENT_OPT':0,
                        'PROJWIN':None,
                        'RTYPE':5,
                        'OPTIONS':'',
                        'EXTRA':'',
                        'OUTPUT':cover_3_temp})

        processing.run("grass:r.neighbors", 
                        {'input':cover_3_temp,
                         'selection':None,
                         'method':0,
                         'size':5,
                         'gauss':None,
                         'quantile':'',
                         '-c':False,
                         '-a':False,
                         'weight':'',
                         'output':cover_3,
                         'GRASS_REGION_PARAMETER':None,
                         'GRASS_REGION_CELLSIZE_PARAMETER':0,
                         'GRASS_RASTER_FORMAT_OPT':'',
                         'GRASS_RASTER_FORMAT_META':''})
        
        os.remove(cover_3_temp)
        print(f"Procesado: {cover_3}")

        processing.run("gdal:rastercalculator", {
                        'INPUT_A':extra_trees_file,
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
                        'FORMULA':"A==4",
                        'NO_DATA':None,
                        'EXTENT_OPT':0,
                        'PROJWIN':None,
                        'RTYPE':5,
                        'OPTIONS':'',
                        'EXTRA':'',
                        'OUTPUT':cover_4_temp})

        processing.run("grass:r.neighbors", 
                        {'input':cover_4_temp,
                         'selection':None,
                         'method':0,
                         'size':5,
                         'gauss':None,
                         'quantile':'',
                         '-c':False,
                         '-a':False,
                         'weight':'',
                         'output':cover_4,
                         'GRASS_REGION_PARAMETER':None,
                         'GRASS_REGION_CELLSIZE_PARAMETER':0,
                         'GRASS_RASTER_FORMAT_OPT':'',
                         'GRASS_RASTER_FORMAT_META':''})
        
        os.remove(cover_4_temp)
        print(f"Procesado: {cover_4}")

        processing.run("gdal:rastercalculator", {
                        'INPUT_A':extra_trees_file,
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
                        'FORMULA':"A==5",
                        'NO_DATA':None,
                        'EXTENT_OPT':0,
                        'PROJWIN':None,
                        'RTYPE':5,
                        'OPTIONS':'',
                        'EXTRA':'',
                        'OUTPUT':cover_5_temp})

        processing.run("grass:r.neighbors", 
                        {'input':cover_5_temp,
                         'selection':None,
                         'method':0,
                         'size':5,
                         'gauss':None,
                         'quantile':'',
                         '-c':False,
                         '-a':False,
                         'weight':'',
                         'output':cover_5,
                         'GRASS_REGION_PARAMETER':None,
                         'GRASS_REGION_CELLSIZE_PARAMETER':0,
                         'GRASS_RASTER_FORMAT_OPT':'',
                         'GRASS_RASTER_FORMAT_META':''})
        
        os.remove(cover_5_temp)
        print(f"Procesado: {cover_5}")

qgs.exitQgis()
