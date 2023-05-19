# Create company and customer in Jeeves and run integration to CRM.
import pyodbc
import json
import time
import subprocess


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
# SQL Statements
update_test_user_email = """
update
    sy2
SET
    YndEmailAddr = 'alina.kolenda@hl-display.com'
WHERE
    ForetagKod = 1
    and PersSign = 'alko'
"""
create_customer = """
EXEC jeeves_init_insert_kus 
    @c_foretagkod = {0}, 
    @c_perssign = 'hlit2', 
    @c_ftgnr = '{1}', 
    @c_kundkategorikod = '20',
    @c_saljare = '{2}'
""".format(data['foretagkod'], data['ftgnr'], data['saljare'])
add_fields2customer = """
UPDATE
    kus
SET
    q_custsegmentcode = '{0}'
    ,q_supergrpcode = '{1}'
    ,q_financialgrpcode = '{2}'
    ,q_hlarea_code = '{3}'
    ,q_salesmarket_code = '{4}' 
    ,kus.q_hl_sync2crm = 1
WHERE
    FtgNr = '{5}'
    and ForetagKod = {6}
""".format(data['q_custsegmentcode'], data['supergrpcode'], data['financialgrpcode'], data['hlarea_code'], data['salesmarket_code'],
           data['ftgnr'], data['foretagkod'])
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
#print('Update user email')
#cursor.execute(update_test_user_email)
#cursor.commit()
print('Creating Customer')
cursor.execute(create_customer)
cursor.commit()
print('Adding fields to customer')
cursor.execute(add_fields2customer)
cursor.commit()
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


