import pyodbc
import codecs
import time
import sys


def connect_to_sql_server(database_name, db_server):
    # Connects to SQL server DB
    server = db_server
    database = database_name
    cnxn = pyodbc.connect(driver='{SQL Server}', server=server, database=database, trusted_connection='yes')
    return cnxn


# Basic data
# FaktNr = 2060973  # TEST
# env = 'ErpHlp001'  # TEST
# db_server = 'EW1-SQL-716'  # TEST
FaktNr = sys.argv[1]  # PROD
env = sys.argv[2]  # PROD
try:
    db_server = sys.argv[3]  # PROD
except IndexError:
    db_server = 'EW1-SQL-716'
# SQL Statements
pull_data_for_faktnr = """
SELECT
    q.foretagkod, 
    fh.KundBetalareNr, 
    fh.SprakKod, 
    fh.SendEdi, 
    fh.OrdLevPlats1,
    q.sysediXML
FROM 
    q_hl_einv_log q
    join edib e on e.foretagkod=q.foretagkod and q.DummyUniqueId=e.DummyUniqueId
    join edid on edid.ForetagKod=e.ForetagKod and edid.EdiId=e.EdiId
    join fh on fh.ForetagKod=e.foretagkod and fh.FaktNr=e.FaktNr
WHERE 
    e.FaktNr = {0}
""".format(FaktNr)
truncate_queue = "delete from q_hl_einv_queue"
cancel_in_1210 = "update edib set Makulerad=1 where foretagkod = 1210 and Makulerad=0"
cancel_in_1710 = "update edib set Makulerad=1 where foretagkod = 1710 and Makulerad=0"
cancel_in_1810 = "update edib set Makulerad=1 where foretagkod = 1810 and Makulerad=0"
cancel_in_1600 = "update edib set Makulerad=1 where foretagkod = 1600 and Makulerad=0"
cancel_in_2400 = "update edib set Makulerad=1 where foretagkod = 2400 and Makulerad=0"
create_xml = "EXECUTE q_ProcessSysEdi"
fetch_xml_sql = "SELECT sysediXML FROM q_hl_einv_queue ORDER BY rowcreateddt DESC"
# Send statements to
cnxn = connect_to_sql_server(env, db_server)
print('Connected to SQL DB')
cursor = cnxn.cursor()
print('Retrive basic data for FaktNR = ', FaktNr)
# BASIC DATA FOR DESIRED FAKTNR
cursor.execute(pull_data_for_faktnr)
data = cursor.fetchone()
FK = data[0]
KundBetalareNr = data[1]
SprakKod = data[2]
SendEdi = data[3]
OrdLevPlats1 = data[4]
FaktNrStr = 'fh.FaktNr=' + str(FaktNr)
model_xml = data[5]
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
""".format(KundBetalareNr, FK, FaktNrStr, SprakKod, FaktNr, SendEdi, OrdLevPlats1)
# END OF BASIC DATA
cursor.execute(truncate_queue)
print('Queue truncated')
cursor.commit()
cursor.execute(cancel_in_1210)
cursor.commit()
print('Invoices cancelled in 1210')
cursor.execute(cancel_in_1600)
cursor.commit()
print('Invoices cancelled in 1600')
cursor.execute(cancel_in_1710)
cursor.commit()
print('Invoices cancelled in 1710')
cursor.execute(cancel_in_1810)
cursor.commit()
print('Invoices cancelled in 1810')
cursor.execute(cancel_in_2400)
cursor.commit()
print('Invoices cancelled in 2400')
print('Creating invoice')
cursor.execute(create_invoice)
cursor.commit()
print('Creating XML')
cursor.execute(create_xml)
cursor.commit()
cursor.execute(fetch_xml_sql)
print('Fetch data')
try:
    xml = cursor.fetchone()[0]
except TypeError:
    print('Fetching again')
    time.sleep(10)
    cursor.execute(fetch_xml_sql)
    xml = cursor.fetchone()[0]
f = codecs.open('models/TEMP.xml', mode="w", encoding="UTF-8")
f.write(model_xml)
print('Model file saved')
f1 = codecs.open('to_compare/TEMP.xml', mode="w", encoding="UTF-8")
f1.write(xml)
print('To compare xml file saved')
