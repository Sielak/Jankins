# Delete all test data from Jeeves and CRM
import pyodbc
import sys
from dynamics365crm.client import Client
import json


def connect_to_sql_server(database_name, db_server):
    # Connects to SQL server DB
    server = db_server
    database = database_name
    cnxn = pyodbc.connect(driver='{SQL Server}', server=server, database=database, trusted_connection='yes')
    return cnxn


# config
with open('config.json') as data_file:
    config = json.load(data_file)
with open('basic_data.json') as data_file:
    basic_data = json.load(data_file)
# env = config['env_test'] # TEST
# server = config['srv_test']  # TEST
env = config['env_prod']  # PROD
server = config['srv_prod']  # PROD
url = config['url_prod']
token = config['token']
# SQL Statements
delete_customer = """
DELETE FROM 
    kus
WHERE
    ForetagKod = {0}
    and FtgNr = '{1}'
""".format(basic_data['foretagkod'], basic_data['ftgnr'])
delete_log = """
DELETE FROM 
    q_hl_dp_data
WHERE
    ProcesName = 'CrmDynamics365'
    and Text2 = 'ForetagKod: {0} FtgNr: {1} SalesMarket: {2}'
""".format(basic_data['foretagkod'], basic_data['ftgnr'], basic_data['salesmarket_code'])
check_customer = """
SELECT
    ftgnr 
    ,kundkategorikod 
    ,saljare
    ,q_custsegmentcode 
    ,q_supergrpcode
    ,q_financialgrpcode 
    ,q_hlarea_code
    ,q_salesmarket_code 
    ,foretagkod
FROM 
    kus
WHERE
    ForetagKod = {0} and
    FtgNr = '{1}'
""".format(basic_data['foretagkod'], basic_data['ftgnr'])
# Send statements to SQL
cnxn = connect_to_sql_server(env, server)
print('Connected to SQL DB')
cursor = cnxn.cursor()
print('Deleting log')
cursor.execute(delete_log)
cursor.commit()
print('Deleting customer')
cursor.execute(delete_customer)
cursor.commit()
print('Checking deletion results - customer')
cursor.execute(check_customer)
results_customer = cursor.fetchall()
deletion_result = []
if len(results_customer) != 0:
    print('[ERROR] Problem with customer deletion')
    deletion_result.append(1)
else:
    print('[OK] customer deleted successfully')
    deletion_result.append(0)
# delete account from CRM
account_id = basic_data['crm_account_id']
if account_id == '':
    print('[ERROR] lack of account id to delete')
    deletion_result.append(1)
else:
    client = Client(url, token)
    token = client.set_token(token)
    client.delete_account(account_id)
    print('[OK] account deleted from CRM')
    deletion_result.append(0)
    basic_data['crm_account_id'] = ''
    with open("basic_data.json", "w") as jsonFile:
        json.dump(basic_data, jsonFile, indent=4, sort_keys=True)
if 1 in deletion_result:
    exit(1)
else:
    exit(0)
