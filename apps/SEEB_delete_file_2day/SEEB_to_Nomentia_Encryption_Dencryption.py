import json
from lib.sftp_crud import SftpOperations
import sys
import time


with open('config.json') as data_file:
    config = json.load(data_file)

print_only = False
if len(sys.argv) > 1:
    if sys.argv[1] == 'test':
        print_only = True
#sftp operation
sftp_objectSEB = SftpOperations(config, 'SEB')
#delete all file older then 2 day
sftp_objectSEB.delete_all_files_sftp("/SEB/", 2, test=print_only)