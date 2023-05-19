import pyodbc
import json
import subprocess
import time


def connect_to_sql_server(database_name, db_server):
    # Connects to SQL server DB
    server = db_server
    database = database_name
    cnxn = pyodbc.connect(driver='{SQL Server}', server=server, database=database, trusted_connection='yes')
    return cnxn


with open('config.json') as data_file:
    config = json.load(data_file)
with open('basic_data.json') as data_file:
    data = json.load(data_file)
# env = config['env_test'] # TEST
# server = config['srv_test']  # TEST
env = config['env_prod']  # PROD
server = config['srv_prod']  # PROD
update_kus = """
UPDATE
    kus
SET
    q_butiknr = 'store_123'
    ,q_hl_default_email = 'crm_integration@test.com'
WHERE
    kus.FtgNr = '{0}'
    and kus.ForetagKod = {1}
""".format(data['ftgnr'], data['foretagkod'])
check_customer_data = """
SELECT
    FtgNr
    ,kus.q_hl_jeevestimestamp
    ,kus.q_hl_crmtimestamp
FROM
    kus
WHERE
    kus.ForetagKod = {0}
    and kus.FtgNr = '{1}'
""".format(data['foretagkod'], data['ftgnr'])
run_integration = """
exec [ErpJvs001].[dbo].q_hl_crm_CreateUpdateAccountsCRM '{0}'
""".format(data['ftgnr'])
check_response_from_jeeves = """
SELECT
    ID
    ,ProcesId
    ,ProcesName
    ,ProcesType
    ,Text1
    ,Text2 
    ,Text3
    ,Text4
    ,Text5
    ,Text6
    ,Message
    ,MessageSQL
    ,RowCreationDate 
FROM 
    q_hl_dp_data 
WHERE 
    ProcesName = 'CrmDynamics365'
    and Text2 = 'ForetagKod: {0} FtgNr: {1} SalesMarket: {2}'
""".format(data['foretagkod'], data['ftgnr'], data['salesmarket_code'])
# Send statements to SQL
cnxn = connect_to_sql_server(env, server)
print('Connected to SQL DB')
cursor = cnxn.cursor()
print('Updating Customer')
cursor.execute(update_kus)
cursor.commit()
print('DEBUG --> Check customer')
cursor.execute(check_customer_data)
results = cursor.fetchone()
print(results)
# print('Run integration procedure')
# subprocess.run([r'runIntegration.bat'], shell=True)
# print('Retrieve data from Jeeves')
# time.sleep(5)
# cursor.execute(check_response_from_jeeves)
# results = cursor.fetchone()
# if results is None:
#     time.sleep(20)
#     print('Retrieve data from Jeeves 2nd attempt')
#     cursor.execute(check_response_from_jeeves)
#     results2 = cursor.fetchone()
#     if results2 is None:
#         print('[ERROR] account not created in CRM')
#         exit(1)
#     else:
#         print('##############################')
#         print('####    DATA FROM WSO2    ####')
#         print('##############################')
#         print(results[9])
# else:
#     print('##############################')
#     print('####    DATA FROM WSO2    ####')
#     print('##############################')
#     print(results[9])

