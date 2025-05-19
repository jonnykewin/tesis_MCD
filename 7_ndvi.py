import os
import processing

path = 'C:/Users/jonny/Documentos/MAESTRIA/TESIS/8-ndvi/santa_marta'

for folder_name in os.listdir(path):
    folder_path = os.path.join(path,folder_name)
    if os.path.isdir(folder_path):
        b4_file = None
        b5_file = None
        for file_name in os.listdir(folder_path):
            if file_name.endswith("SR_B4.TIF"):
                b4_file = os.path.join(folder_path,file_name)  

            if file_name.endswith("SR_B5.TIF"):
                b5_file = os.path.join(folder_path,file_name) 

        ndvi = os.path.join(folder_path, "NDVI.TIF")
        
        formula = f"((B-A)/(B+A))"
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