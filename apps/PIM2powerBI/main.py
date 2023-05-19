from sftp_crud import SftpOperations
import json


with open('config.json') as data_file:
    config = json.load(data_file)


sftp_object = SftpOperations(config)
file_list = sftp_object.list_all_files_sftp('/')
for file in file_list:
    new_name = '{0}PIM_{1}.csv'.format(config['path'], file.split('_')[0])
    sftp_object.download_file_sftp(new_name, '/{0}'.format(file))

sftp_object.delete_all_files_sftp('/')
