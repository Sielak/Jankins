import json
import requests
from dynamics365crm.client import Client
import pyodbc


def connect_to_sql_server(database_name, db_server):
    # Connects to SQL server DB
    server = db_server
    database = database_name
    cnxn = pyodbc.connect(driver='{SQL Server}', server=server, database=database, trusted_connection='yes')
    return cnxn


def post2monitoring(status):
    url = 'http://bma-iwa-101:8085/logExternalService/crm_reg_tests/{0}/test'.format(status)
    r = requests.get(url)
    print('Posting result to:', url)
    if r.status_code == 200:
        data = json.loads(r.text)
        if data['messageNo'] != '0':
            print('ERROR', data['messageStr'])
            exit(1)
        else:
            print('Status:', data['messageStr'])
    else:
        print('returned status not OK')
        exit(1)


def retrive_and_compare_data(accounts_data):
    item = accounts_data['value'][0]
    crm_name = item['name']
    crm_ftgnr = item['accountnumber']
    crm_store_id = item['new_storeid']
    crm_area_id = item['_new_area_value']
    crm_sales_market_id = item['_new_salesmarket_value']
    crm_email = item['emailaddress1']
    crm_address1_line1 = item['address1_line1']
    crm_address1_line2 = item['address1_line2']
    crm_address1_city = item['address1_city']
    crm_address1_postalcode = item['address1_postalcode']
    crm_address1_state = item['address1_stateorprovince']
    crm_address1_country = item['address1_country']
    crm_currency_id = item['_transactioncurrencyid_value']
    crm_owner_id = item['_ownerid_value']
    crm_account_id = item['accountid']
    # to change
    crm_financial_group_id = item['_new_financialgroupjeeves_value']
    crm_super_group_id = item['_new_supergroupjeeves_value']
    crm_customer_segment_id = item['_new_customersegmentjeeves_value']
    # save crm account ID to json
    basic_data['crm_account_id'] = crm_account_id
    with open("basic_data.json", "w") as jsonFile:
        json.dump(basic_data, jsonFile, indent=4, sort_keys=True)
    # retrive data from dictionaries
    get_financial_group = client.get_data(type='new_financialgroups', filter="new_financialgroupid eq {0}".format(crm_financial_group_id))
    if get_financial_group['value'][0]['new_financialgroupid'] == crm_financial_group_id:
        crm_financial_group = get_financial_group['value'][0]['new_name']
    get_super_group = client.get_data(type='new_supergroups',
                                          filter="new_supergroupid eq {0}".format(crm_super_group_id))
    if get_super_group['value'][0]['new_supergroupid'] == crm_super_group_id:
        crm_super_group = get_super_group['value'][0]['new_name']
    get_customer_segment = client.get_data(type='new_customersegments',
                                      filter="new_customersegmentid eq {0}".format(crm_customer_segment_id))
    if get_customer_segment['value'][0]['new_customersegmentid'] == crm_customer_segment_id:
        crm_customer_segment = get_customer_segment['value'][0]['new_name']
    get_sales_market = client.get_data(type='new_salesmarkets',
                                       filter="new_salesmarketid eq {0}".format(crm_sales_market_id))
    if get_sales_market['value'][0]['new_salesmarketid'] == crm_sales_market_id:
        crm_sales_market = get_sales_market['value'][0]['new_name']
        if crm_sales_market == 'Poland':
            crm_sales_market = 'PL'
    get_area = client.get_data(type='new_areas', filter="new_areaid eq {0}".format(crm_area_id))
    if get_area['value'][0]['new_areaid'] == crm_area_id:
        crm_area = get_area['value'][0]['new_name']
        if crm_area == 'Central':
            crm_area = 'EE'
    get_currency = client.get_data(type='transactioncurrencies',
                                   filter="transactioncurrencyid eq {0}".format(crm_currency_id))
    if get_currency['value'][0]['transactioncurrencyid'] == crm_currency_id:
        crm_currency = get_currency['value'][0]['currencysymbol']
    get_owner = client.get_data(type='systemusers', filter="systemuserid eq {0}".format(crm_owner_id))
    if get_owner['value'][0]['systemuserid'] == crm_owner_id:
        crm_owner = get_owner['value'][0]['domainname']
    crm_results = (crm_name,
                   crm_ftgnr,
                   crm_financial_group,
                   crm_super_group,
                   crm_customer_segment,
                   crm_store_id,
                   crm_area,
                   crm_sales_market,
                   crm_email,
                   crm_address1_line1,
                   crm_address1_line2,
                   crm_address1_city,
                   crm_address1_postalcode,
                   crm_address1_state,
                   crm_address1_country,
                   crm_currency,
                   crm_owner
                   )
    fields = ('name',
              'ftgnr',
              'crm_financial_group',
              'crm_super_group',
              'customer_segment',
              'store_id',
              'area',
              'sales_market',
              'email',
              'address1_line1',
              'address1_line2',
              'address1_city',
              'address1_postalcode',
              'address1_state',
              'address1_country',
              'currency',
              'owner'
              )
    cnxn = connect_to_sql_server(env, server)
    print('Connected to SQL DB')
    cursor = cnxn.cursor()
    cursor.execute(select_fields2compare)
    jvs_results = cursor.fetchone()
    test_result = 1
    for crm_field, jvs_field, field_name in zip(crm_results, jvs_results, fields):
        if crm_field != jvs_field:
            try:
                if crm_field.lower() != jvs_field.lower():
                    print(field_name, 'CRM value:', crm_field, '<-->', 'Jeeves value:', jvs_field)
                    test_result = 0
            except AttributeError:
                print(field_name, 'CRM value:', crm_field, '<-->', 'Jeeves value:', jvs_field)
                test_result = 0
        # print(crm_field, '<-->', jvs_field)
    return test_result


with open('config.json') as data_file:
    config = json.load(data_file)
with open('basic_data.json') as data_file:
    basic_data = json.load(data_file)
# Basic data
env = config['env_test'] # TEST
# server = config['srv_test']  # TEST
env = config['env_prod'] # PROD
server = config['srv_prod']  # PROD
# variables
crm_name = ''
crm_ftgnr = ''
crm_financial_group = ''
crm_super_group = ''
crm_customer_segment = ''
crm_store_id = ''
crm_email = ''
crm_address1_line1 = ''
crm_address1_line2 = ''
crm_address1_city = ''
crm_address1_postalcode = ''
crm_address1_state = ''
crm_address1_country = ''
crm_sales_market_id = ''
crm_sales_market = ''
crm_area_id = ''
crm_area = ''
crm_currency_id = ''
crm_currency = ''
crm_owner_id = ''
crm_owner = ''
crm_account_id = ''
# sql queries
select_fields2compare = """
SELECT
    fr.ftgnamn 
    ,kus.ftgnr 
    ,fin.q_financialgrpdesc
    ,sup.q_supergrpdesc 
    ,seg.q_custsegmentdesc
    ,kus.q_butiknr 
    ,kus.q_hlarea_code 
    ,kus.q_salesmarket_code 
    ,kus.q_hl_default_email 
    ,fr.ftgpostadr2 
    ,fr.ftgpostadr1 
    ,fr.ftgpostadr3 
    ,fr.ftgpostnr 
    ,fr.distrkod 
    ,fr.Landskod
    ,kus.valkod 
    ,sy2.YndEmailAddr 
FROM
    kus
    join fr on kus.ForetagKod = fr.ForetagKod and kus.FtgNr = fr.FtgNr
    join sy2 on kus.Saljare = sy2.PersSign
    join q_custsegment seg on kus.ForetagKod = seg.foretagkod and kus.q_custsegmentcode = seg.q_custsegmentcode
    join q_supergrp sup on kus.ForetagKod = sup.foretagkod and kus.q_supergrpcode = sup.q_supergrpcode
    join q_financialgrp fin on kus.ForetagKod = fin.foretagkod and kus.q_financialgrpcode = fin.q_financialgrpcode
WHERE
    kus.FtgNr = '{0}'
    and kus.ForetagKod = {1}
""".format(basic_data['ftgnr'], basic_data['foretagkod'])

# LOGIN --> TOKEN
# set these values to retrieve the oauth token
crmorg = config['crm_base_url_prod']  # base url for crm org
clientid = config['client_id']  # application client id
username = config['crm_username']
userpassword = config['crm_password']
tokenendpoint = config['token_endpoint']  # oauth token endpoint

# build the authorization token request
tokenpost = {
    'client_id': clientid,
    'resource': crmorg,
    'username': username,
    'password': userpassword,
    'grant_type': 'password'
}

# make the token request
tokenres = requests.post(tokenendpoint, data=tokenpost)

# set accesstoken variable to empty string
accesstoken = ''

# extract the access token
try:
    accesstoken = tokenres.json()['access_token']
    print('access token retrived ')
    config['token'] = accesstoken
    with open("config.json", "w") as jsonFile:
        json.dump(config, jsonFile, indent=4, sort_keys=True)
except KeyError:
    # handle any missing key errors
    print('Could not get access token')
    # print('[DEBUG]')
    # print(tokenres.text)

# LOGIC

url = config['url_prod']
token2 = accesstoken
client = Client(url, token2)
token = client.set_token(token2)
get_accounts = client.get_data(type='accounts', filter="name eq 'CRM_test_company'")
accounts_count = len(get_accounts['value'])
print('number of companies:', accounts_count)
if accounts_count == 0:
    print('[ERROR] Test account not found')
    post2monitoring('NOK')
    exit(1)
elif accounts_count > 1:
    print('[ERROR] more then 1 account in CRM with this name')
    post2monitoring('NOK')
    exit(1)
else:
    result = retrive_and_compare_data(get_accounts)
    if result == 1:
        print('[OK]')
        post2monitoring('OK')
    elif result == 0:
        print('[ERROR] Some fields are different')
        post2monitoring('NOK')
        exit(1)
    else:
        print('[ERROR] Somsing is no yes.')
        post2monitoring('NOK')
        exit(1)
