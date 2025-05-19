import os
import processing

path = 'C:/Users/jonny/Documentos/MAESTRIA/TESIS/9-ndbi/santa_marta'

for folder_name in os.listdir(path):
    folder_path = os.path.join(path,folder_name)
    if os.path.isdir(folder_path):
        b6_file = None
        b5_file = None
        for file_name in os.listdir(folder_path):
            if file_name.endswith("SR_B6.TIF"):
                b6_file = os.path.join(folder_path,file_name)  

            if file_name.endswith("SR_B5.TIF"):
                b5_file = os.path.join(folder_path,file_name) 

        ndbi = os.path.join(folder_path, "NDBI.TIF")
        
        formula = f"((B-A)/(B+A))"
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