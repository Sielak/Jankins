import pyodbc
import json
import paramiko
import datetime


def upload_file_sftp(filename, file_type):
    with open('basic_data.json') as data_file:
        config = json.load(data_file)

    # Read variables
    host = config['es_host']
    user = config['es_username']
    password = config['es_password']
    if file_type == 'params':
        local_file = 'basic_data_params.xml'
    else:
        local_file = 'basic_data_po.xml'
    
    # Connect by SSH
    ssh_client = paramiko.SSHClient()
    ssh_client.load_system_host_keys
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=host,
                    username=user,
                    password=password,
                    timeout=5000)

    # Download file
    ftp_client=ssh_client.open_sftp()
    ftp_client.put(local_file, f"/EazyStock/output/{filename}")
    ftp_client.close()


class sql_queries:
    def __init__(self, database_name, db_server):
        # Connects to SQL server DB
        self.server = db_server
        self.database = database_name
        cnxn = pyodbc.connect(driver='{SQL Server}', server=self.server, database=self.database, trusted_connection='yes')
        self.cursor = cnxn.cursor()

    def update_item(self):
        query =  """
        UPDATE
            ar
        SET
            q_hl_es_pickclass = ''
            ,q_hl_es_vau = ''
            ,q_hl_es_stockeditem = 0
        WHERE
            ar.ArtNr = '200088'
            and ar.ForetagKod = 1600
        """
        self.cursor.execute(query)
        self.cursor.commit()
        return query

    def update_item_balances(self): 
        query = """
        UPDATE
            ars
        SET
            ars.eoq = 0
            ,ars.ArtSecLager = 0
            ,ars.LagBestPkt = 0
        WHERE
            ars.ArtNr = '200088'
            and ars.LagStalle = 0
            and ars.ForetagKod = 1600
        """
        self.cursor.execute(query)
        self.cursor.commit()
        return query

    def fetch_item_data(self): 
        query = """
        SELECT
            ar.ArtNr
            ,ars.eoq as Cooq
            ,ars.ArtSecLager as BufferStock
            ,ars.LagBestPkt as OrderLevel
            ,ar.q_hl_es_pickclass as PickClass 
            ,ar.q_hl_es_vau as VauClass
            ,ar.q_hl_es_stockeditem as Stocked
        FROM
            ar
            join ars on ar.ForetagKod = ars.ForetagKod and ar.ArtNr = ars.ArtNr
        WHERE
            ar.ArtNr = '200088'
            and ar.ForetagKod = 1600
            and ars.LagStalle = 0
        """
        self.cursor.execute(query)
        results = self.cursor.fetchone()
        return results

    def fetch_po_data(self, filename_po): 
        query = """
        SELECT
            bp.artnr
            ,bp.bestantextqty
        FROM
            bp
            join bh on bp.ForetagKod = bh.ForetagKod and bp.BestNr = bh.BestNr
        WHERE
            bh.q_hl_es_filename = '{0}'
            AND bh.foretagkod = 1600
        """.format(filename_po)
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        return results


# file_version = 1
# today = datetime.datetime.strftime(datetime.datetime.today(), '%Y%m%d')
# filename_params = 'Parameters_HL_Display_1600_{0}-{1}.xml'.format(today, file_version)
# upload_file_sftp(filename_params, 'params')