import json
from lib.sftp_crud import SftpOperations
from lib.file_encryption import GPGOperations
import os
import time


with open('config.json') as data_file:
    config = json.load(data_file)

gpg_object = GPGOperations(config)

#sftp operation
sftp_objectSEB = SftpOperations(config, 'SEB')
sftp_objectNomentia = SftpOperations(config, 'Nomentia')
file_list = sftp_objectSEB.list_all_files_sftp('/SEB/')
for file in file_list:
    #Download File
    sftp_objectSEB.download_file_sftp(config['pathtemp'],file)

    #Decryption
    gpg_object.decrypt_file_EDI(config['application_dir'],
                                config['pathtemp'] + file,
                                config['pathtemp'] + '/Dectypt/' + file,
                                config['passphraseSEB'])

    #Encryption
    gpg_object.encrypt_file_EDI(config['application_dir'],
                                config['pathtemp'] + '/Dectypt/' + file,
                                config['pathtemp'] + '/Encrypt/' + file,
                                config['passphraseHL'])
    
    #Delete file from Decrypt folder
    os.remove(config['pathtemp'] + '/Dectypt/' + file)

    #Save file to correct folder on sftp
    format_name = file.split('_',1)[0]
    if 'camt' in format_name.casefold():
        sftp_objectNomentia.upload_file_sftp(config['pathtemp'] + '/Encrypt/' + file, '/CAMT.053_Actuals_and_Balances')
    elif 'mt940' in format_name.casefold():
        sftp_objectNomentia.upload_file_sftp(config['pathtemp'] + '/Encrypt/' + file, '/MT940_Actuals_and_Balances')
    elif 'tito' in format_name.casefold():
        sftp_objectNomentia.upload_file_sftp(config['pathtemp'] + '/Encrypt/' + file, '/TITO_Actuals_and_Balances')

    #Save file in archive folder
    sftp_objectSEB.upload_file_sftp(config['pathtemp'] + '/Encrypt/' + file, '/Archive/')
    os.remove(config['pathtemp'] + '/Encrypt/' + file)

sftp_objectSEB.delete_all_files_sftp('/Archive/', 40)  
