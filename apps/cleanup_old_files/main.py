import os, time, json, datetime


# Config
with open('config.json') as data_file:
    config = json.load(data_file)

now = time.time()


def delete_files_from_path(path, storage_days=30):
    for filename in os.listdir(path):
        if os.path.isfile(os.path.join(path,filename)):
            filestamp = os.stat(os.path.join(path, filename)).st_mtime
            filecompare = now - storage_days * 86400
            if  filestamp < filecompare:
                try:
                    os.remove(os.path.join(path, filename))
                    human_readable_date = datetime.datetime.fromtimestamp(filestamp).strftime('%c')
                    print(filename, human_readable_date)
                except PermissionError:
                    print(f"{filename} was not deleted. Access is denied")
            

for item in config['locations']:
    folder_path = item['path']
    print(f'## DELETING FILES FROM {folder_path} folder')
    delete_files_from_path(folder_path, storage_days=item['data_storage_days'])