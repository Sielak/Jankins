import pymysql
import codecs
import sys
import pyodbc
import time


def connect_to_sql_server(database_name, db_server):
    # Connects to SQL server DB
    cnxn = pyodbc.connect(driver='{SQL Server}', server=db_server, database=database_name, trusted_connection='yes')
    return cnxn


def connect_to_mysql(database_name, db_server):
    # Connects to SQL server DB
    cnxn = pymysql.connect(host=db_server,
                           user='hlguest',
                           password='hlguest123A!',
                           db=database_name,
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)
    return cnxn


# Basic data
# invoiceNO = 2185836  # TEST for tesco
# env = 'ErpTst002'  # TEST for tesco
invoiceNO = sys.argv[1]  # PROD for tesco
env = sys.argv[2]  # PROD for tesco

# Fetch model file
# Connect to the database
print('connecting to mySQL DB')
connection = connect_to_mysql('hl', 'BMA-ESB-702')
cursor = connection.cursor()
sql = "SELECT content FROM hl.track_inv_sei_file WHERE status = 'INPUT' AND content LIKE '%{0}%' ORDER BY create_timestamp ASC;".format(invoiceNO)
print('Run query and fetch XML')
cursor.execute(sql)
model_xml = cursor.fetchone()
# print(result['content'])
f = codecs.open('models/tesco.xml', mode="w", encoding="UTF-8")
f.write(model_xml['content'])
print('Model file saved')

# Basic data for resend
print('connecting to SQL server DB for basic data')
mssql_connection = connect_to_sql_server(env, 'EW1-SQL-711')
mssql_cursor = mssql_connection.cursor()
retrieve_basic_data = """
SELECT 
    fh.ForetagKod,
    fh.KundBetalareNr, 
    fh.SprakKod, 
    fh.SendEdi, 
    fh.OrdLevPlats1, 
    edid.q_hl_edi_serviceproxy
from edib e     
join edid on edid.ForetagKod=e.ForetagKod and edid.EdiId=e.EdiId
join fh on fh.ForetagKod=e.foretagkod and fh.FaktNr=e.FaktNr
where fh.FaktNr = {0}
order by fh.RowCreatedDT  desc
""".format(invoiceNO)
mssql_cursor.execute(retrieve_basic_data)
data = mssql_cursor.fetchone()
FK = data[0]
KundBetalareNr = data[1]
SprakKod = data[2]
SendEdi = data[3]
OrdLevPlats1 = data[4]
FaktNrStr = 'fh.FaktNr=' + str(invoiceNO)
model_xml = data[5]

# SQL statments
create_invoice = """
EXECUTE JEEVES_New_Doc
    'hlit2',
    'rInvoicU',
    {0},
    NULL,
    NULL,
    {1},
    '{2}',
    {3},
    {4},
    {5},
    {6},
    'rInvoicU',
    NULL,
    NULL
""".format(KundBetalareNr, FK, FaktNrStr, SprakKod, invoiceNO, SendEdi, OrdLevPlats1)
truncate_queue = "delete from q_hl_einv_queue"
cancel_in_1210 = "update edib set Makulerad=1 where foretagkod = 1210 and Makulerad=0"
cancel_in_1710 = "update edib set Makulerad=1 where foretagkod = 1710 and Makulerad=0"
cancel_in_1810 = "update edib set Makulerad=1 where foretagkod = 1810 and Makulerad=0"
cancel_in_1600 = "update edib set Makulerad=1 where foretagkod = 1600 and Makulerad=0"
create_xml = "EXECUTE q_hl_EDI_SendEdiInvoice"
fetch_new_xml = "SELECT content FROM hl.track_inv_sei_file WHERE status = 'INPUT' AND content LIKE '%{0}%' ORDER BY create_timestamp DESC;".format(invoiceNO)
# Resend invoice
mssql_cursor.execute(truncate_queue)
print('Queue truncated')
mssql_cursor.commit()
mssql_cursor.execute(cancel_in_1210)
mssql_cursor.commit()
print('Invoices cancelled in 1210')
mssql_cursor.execute(cancel_in_1600)
mssql_cursor.commit()
print('Invoices cancelled in 1600')
mssql_cursor.execute(cancel_in_1710)
mssql_cursor.commit()
print('Invoices cancelled in 1710')
mssql_cursor.execute(cancel_in_1810)
mssql_cursor.commit()
print('Invoices cancelled in 1810')
print('Creating invoice')
mssql_cursor.execute(create_invoice)
mssql_cursor.commit()
print('Creating XML')
mssql_cursor.execute(create_xml)
mssql_cursor.commit()
print('Buffor for integration')
time.sleep(20)
# Fetch file to compare
print('Run query and fetch XML to compare')
cursor.execute(fetch_new_xml)
compare_xml = cursor.fetchone()
# print(compare_xml)
f = codecs.open('to_compare/tesco.xml', mode="w", encoding="UTF-8")
f.write(compare_xml['content'])
print('Model file saved')