import os
import processing

path = 'C:/Users/jonny/Documentos/MAESTRIA/TESIS/10-lst/santa_marta'

for folder_name in os.listdir(path):
    folder_path = os.path.join(path,folder_name)
    if os.path.isdir(folder_path):
        if folder_name.startswith("LC08_"):
            lambda_w = 10.895e-6  # Para Landsat 8
        elif folder_name.startswith("LC09_"):
            lambda_w = 10.902e-6  # Para Landsat 9
        b10_file = None
        ndvi_file = None
        for file_name in os.listdir(folder_path):
            if file_name.endswith("ST_B10.TIF"):
                b10_file = os.path.join(folder_path,file_name)  

            elif file_name.endswith("NDVI.TIF"):
                ndvi_file = os.path.join(folder_path,file_name) 

        lst = os.path.join(folder_path, "LST.TIF")
        
        formula = f"((A) / (1 + ({lambda_w} * (A) / 1.438e-2) * log(0.004 * B + 0.986))) - 273.15"
        processing.run("gdal:rastercalculator", {
                        'INPUT_A':b10_file,
                        'BAND_A':1,
                        'INPUT_B':ndvi_file,
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
                        'OUTPUT':lst})
                        
        print(f"Procesado: {lst}")