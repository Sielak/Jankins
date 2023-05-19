import json
import pyodbc

# import of configuration file
with open('config.json') as data_file:
    config = json.load(data_file)


def connect_to_sql_server(database_name):
    server = config['Report_DB_server']
    database = database_name
    username = config['Report_DB_username']
    password = config['Report_DB_password']
    # for linux or windows
    driver = '{ODBC Driver 13 for SQL Server}'
    cnxn = pyodbc.connect(
        'DRIVER=' + driver + ';PORT=1433;SERVER=' + server + ';PORT=1443;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
    return cnxn