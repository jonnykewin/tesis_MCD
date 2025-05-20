import os

path = r'C:\Users\jonny\Documentos\MAESTRIA\TESIS\6-clean_outliers\barranquilla'

name_file = [
    "B2.TIF", "B3.TIF", "B4.TIF",
    "B5.TIF", "B6.TIF", "B7.TIF",
    "B10.TIF", "B8.TIF", "MTL.json","ANG.txt",]

print(path)

for folder_name in os.listdir(path):
    folder_path = os.path.join(path,folder_name)
    if os.path.isdir(folder_path):
        for file_name in os.listdir(folder_path):
            if not any(file_name.endswith(end_name) for end_name in name_file):
                os.remove(os.path.join(folder_path, file_name))
                print(f"Eliminado: {os.path.join(folder_path, file_name)}")