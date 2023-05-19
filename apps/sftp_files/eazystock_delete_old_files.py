import json
from lib.sftp_crud import SftpOperations
import sys


with open('config.json') as data_file:
    config = json.load(data_file)


print_only = False
if len(sys.argv) > 1:
    if sys.argv[1] == 'test':
        print_only = True
res = SftpOperations(config)
res.delete_all_files_sftp("/output/", test=print_only)