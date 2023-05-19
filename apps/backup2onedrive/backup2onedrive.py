import json
import os
import glob
import shutil
from datetime import datetime, timedelta, date
import tarfile

with open('backup2onedrive.json') as data_file:
    folders2backup = json.load(data_file)


def make_backup(item):
    temp_path = "C:/jenkins/apps/backup2onedrive/temp/"
    dest_path = temp_path + item['name'] + "/"
    if os.path.isdir(dest_path) == True:
        print('Removing old folders')
        shutil.rmtree(dest_path)
    print('Start coping of {0} from {1}'.format(item['name'], item['path']))
    if item['is_file'] is True:
        print('Create temp dir')
        os.mkdir(temp_path + item['name'])
        shutil.copy(item['path'], dest_path)
    else:
        shutil.copytree(item['path'], dest_path, symlinks=True, ignore = shutil.ignore_patterns(item['ignore_pattern']))
    print('Copy complete')
    print('Packing')
    date_now = datetime.now().strftime("%Y%m%d_%H%M%S")
    tar_name = "{0}_backup_{1}.tar.gz".format(item['name'], date_now)
    tar = tarfile.open(temp_path + tar_name, "w:gz")
    tar.add(dest_path, arcname=item['name'])
    tar.close()
    print('Packing complete')
    # print('Moving tar file to onedrive')
    onedrive_path = "C:/Users/poca/OneDrive - HL Display AB/backup/" + item['name'] + "/"
    if os.path.isdir(onedrive_path) == False:
        os.mkdir(onedrive_path)
    shutil.move(temp_path + tar_name, onedrive_path)
    print('Moving complete')
    print('Removing files')
    shutil.rmtree(dest_path)
    print('--- Done ---')


def check_last_backup(item):
    list_of_files = glob.glob("C:/Users/poca/OneDrive - HL Display AB/backup/" + item['name'] + "/*") # * means all if need specific format then *.csv
    try:
        latest_file = max(list_of_files, key=os.path.getctime)
    except ValueError:
        return True
    latest_file_date = date.fromtimestamp(os.path.getctime(latest_file))
    if latest_file_date + timedelta(days=item['interval']) <= date.today():
        return True
    else:
        return False


for item in folders2backup['items2backup']:
    if check_last_backup(item) is True:
        make_backup(item)


