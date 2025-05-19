import os
import json
import processing
import math

path = 'C:/Users/jonny/Documentos/MAESTRIA/TESIS/11-rgb/santa_marta'

for folder_name in os.listdir(path):
    folder_path = os.path.join(path,folder_name)
    if os.path.isdir(folder_path):
        for file_name in os.listdir(folder_path):
            if file_name.endswith("SR_B2.TIF"):
                temp_file_b2 = os.path.join(folder_path,file_name)
            elif file_name.endswith("SR_B3.TIF"):
                temp_file_b3 = os.path.join(folder_path,file_name)
            elif file_name.endswith("SR_B4.TIF"):
                temp_file_b4 = os.path.join(folder_path,file_name)
            elif file_name.endswith("B8.TIF"):
                temp_file_b8 = os.path.join(folder_path,file_name)
        
        temp_output_rgb = os.path.join(folder_path, "RGB.TIF")
        temp_output_rgb_pan = os.path.join(folder_path, "RGB_pansharp.TIF")
        
        processing.run("gdal:merge", {
                        'INPUT':[temp_file_b2,temp_file_b3,temp_file_b4],
                        'PCT':False,
                        'SEPARATE':True,
                        'NODATA_INPUT':None,
                        'NODATA_OUTPUT':None,
                        'OPTIONS':'',
                        'EXTRA':'',
                        'DATA_TYPE':5,
                        'OUTPUT':temp_output_rgb})
        
        processing.run("gdal:pansharp", {
                        'SPECTRAL':temp_output_rgb,
                        'PANCHROMATIC':temp_file_b8,
                        'RESAMPLING':2,
                        'OPTIONS':'',
                        'EXTRA':'',
                        'OUTPUT':temp_output_rgb_pan})
        
        print(f"Procesado: {folder_path}")