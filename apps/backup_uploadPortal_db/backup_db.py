import os
import json
import paramiko


with open('config.json') as data_file:
    config = json.load(data_file)

# Read variables
host = config['host']
user = config['username']
ssh_key_filepath = config['ssh_key']
remote_path = config['remote_path']
local_file = config['local_path']

# Delete old db file
if os.path.exists(local_file):
  os.remove(local_file)
else:
  print("The file does not exist")

# Connect by SSH
ssh_client = paramiko.SSHClient()
ssh_client.load_system_host_keys
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(hostname=host,
                username=user,
                key_filename=ssh_key_filepath, 
                look_for_keys=True,
                timeout=5000)

# Download file
ftp_client=ssh_client.open_sftp()
ftp_client.get(remote_path, local_file)
ftp_client.close()
