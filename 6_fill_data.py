import os
import processing

path = 'C:/Users/jonny/Documentos/MAESTRIA/TESIS/7-fill_data/barranquilla'

for folder_name in os.listdir(path):
    folder_path = os.path.join(path,folder_name)
    if os.path.isdir(folder_path):
        for file_name in os.listdir(folder_path):
            list_sr = ["SR_B1.TIF","SR_B2.TIF","SR_B3.TIF","SR_B4.TIF","SR_B5.TIF","SR_B6.TIF","SR_B7.TIF","B8.TIF"]
            for sr in list_sr:
                if file_name.endswith(sr):
                    temp_file = os.path.join(folder_path,file_name)
                    first_output = os.path.join(folder_path, f"FN_{file_name}")
                    
                    processing.run("gdal:fillnodata", {
                    'INPUT':temp_file,
                    'BAND':1,
                    'DISTANCE':10,
                    'ITERATIONS':0,
                    'MASK_LAYER':None,
                    'OPTIONS':None,
                    'EXTRA':'',
                    'OUTPUT':first_output})
                    
                    second_output = os.path.join(folder_path, f"ND0_{file_name}")

                    processing.run("native:fillnodata", {
                    'INPUT':first_output,
                    'BAND':1,
                    'FILL_VALUE':0,
                    'CREATE_OPTIONS':None,
                    'OUTPUT':second_output})

                    os.remove(first_output)
                    os.remove(temp_file)
                    print(f"Procesado: {second_output}")