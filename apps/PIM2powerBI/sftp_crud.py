import paramiko


class SftpOperations():
    def __init__(self, config):
        """Class used to interact with sftp clients

        Args:
            config (Json): json object with configuration
        """
        self.config = config

    def _connect_by_ssh(self):
        """Method used to connect to SFTP

        Returns:
            SSH Client instance: paramiko sftp connection instance
        """
        ssh_client = paramiko.SSHClient()
        ssh_client.load_system_host_keys
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=self.config['host'],
                        username=self.config['username'],
                        password=self.config['password'],
                        timeout=5000)
        return ssh_client

    def delete_all_files_sftp(self, path, test=False):
        """Method used to delete all files from directory

        Args:
            path (string): path to folder
        """
        # Connect by SSH
        ssh_client = self._connect_by_ssh()

        # DELETE file
        ftp_client=ssh_client.open_sftp()
        files_list = ftp_client.listdir(path)
        for file in files_list:
            if test is True:
                print(file)
            else:
                print("Removing file", file)
                ftp_client.remove(path + file)
                print("Done")
        ftp_client.close()

    def upload_file_sftp(self, local_path, remote_path): 
        """Method used to upload file to SFTP server

        Args:
            local_path (string): path to source file
            remote_path (string): path to destination file
        """
        # Connect by SSH
        ssh_client = self._connect_by_ssh()

        # Upload file
        ftp_client=ssh_client.open_sftp()
        ftp_client.put(remote_path,local_path)
        ftp_client.close()

    def download_file_sftp(self, local_path, remote_path): 
        """Method used to download file from SFTP server

        Args:
            local_path (string): path to source file
            remote_path (string): path to destination file
        """
        # Connect by SSH
        ssh_client = self._connect_by_ssh()

        # Download file
        ftp_client=ssh_client.open_sftp()
        ftp_client.get(remote_path,local_path)
        ftp_client.close()


    def list_all_files_sftp(self, path):
        """Method used to list all files from directory

        Args:
            path (string): path to folder
        """
        # Connect by SSH
        ssh_client = self._connect_by_ssh()

        # DELETE file
        ftp_client=ssh_client.open_sftp()
        files_list = ftp_client.listdir(path)
        ftp_client.close()
        return files_list
              

            