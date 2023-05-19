from selenium import webdriver
from selenium.common.exceptions import TimeoutException
import time
import pyodbc
import requests
import json
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def connect_to_sql_server(database_name, db_server):
    # Connects to SQL server DB
    server = db_server
    database = database_name
    cnxn = pyodbc.connect(driver='{SQL Server}', server=server, database=database, trusted_connection='yes')
    return cnxn


def login2tieto():
    user_name = 'mattspat'
    user_pass = 'l3r4u9l5'
    driver.get("https://laskuhotelli.tieto.com/")
    # Login to tieto portal
    change_lang = driver.find_element_by_xpath(
        '/html/body/center/table/tbody/tr[2]/td/table/tbody/tr/td[3]/table/tbody/tr[1]/td[2]/table/tbody/tr[2]/td/a[2]')
    change_lang.click()
    time.sleep(1)
    username = driver.find_element_by_name('webUserId')
    password = driver.find_element_by_name('webPassword')
    login = driver.find_element_by_xpath(
        '/html/body/center/table/tbody/tr[2]/td/table/tbody/tr/td[5]/table/tbody/tr[3]/td/center/center/center/form/table/tbody/tr[4]/td[2]/input')
    username.send_keys(user_name)
    password.send_keys(user_pass)
    login.click()
    # normal selenium waits dont work for me so i use sleep from time library
    time.sleep(1)
    # change page
    browse_invoices = driver.find_element_by_link_text('Browse sent invoices').click()
    time.sleep(1)


def check_invoice(inv_no):
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "invoice_id")))
    invoice_no_field = driver.find_element_by_xpath("//input[@name='invoice_id']")
    invoice_no_field.send_keys(inv_no)
    driver.find_element_by_xpath("//input[@value='Browse']").click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@value='Return']")))
    table_rows = driver.find_elements_by_tag_name('span')
    checker = 0
    for item in table_rows:
        if item.text == inv_no:
            checker = 1
    if checker == 1:
        print('[OK] - {0}'.format(inv_no))
    else:
        print('[ERROR] Invoice not found - {0}'.format(inv_no))
    back2search = driver.find_element_by_xpath("//input[@value='Return']")
    back2search.click()
    time.sleep(3)  # need to use this because WbDriverWait is not working properly
    return checker


def retrieve_invoice_list(integration):
    sql = """
    SELECT
        e.FaktNr
    FROM 
        q_hl_einv_log q
        join edib e on e.foretagkod=q.foretagkod and q.DummyUniqueId=e.DummyUniqueId
        join edid on edid.ForetagKod=e.ForetagKod and edid.EdiId=e.EdiId
    WHERE 
        edid.q_hl_edi_serviceproxy='{0}'
        AND q.rowcreateddt >= dateadd(day,datediff(day,1,GETDATE()),0)
        AND q.rowcreateddt < dateadd(day,datediff(day,0,GETDATE()),0)
    ORDER BY 
        q.rowcreateddt DESC
    """.format(integration)
    cnxn = connect_to_sql_server('ErpHlp001', 'EW1-SQL-716')
    cursor = cnxn.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    return data


def post2monitoring(status):
    url = 'http://bma-iwa-101:8085/logExternalService/ext_edi_reg_portal_tieto/{0}/test'.format(status)
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


test = retrieve_invoice_list('EICF')
if len(test) == 0:
    print('Nothing to check, closing')
    post2monitoring('OK')
    exit(0)
else:
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    login2tieto()
    results = []
    for item in test:
        try:
            test_item = check_invoice(str(item[0]))
            results.append(test_item)
        except TimeoutException:
            print("exception, make screenshot")
            filename = "error-{0}.png".format(item[0])
            driver.get_screenshot_as_file('img/' + filename)
            results.append(0)
    if 0 in results:
        post2monitoring('NOK')
        driver.quit()
        exit(1)
    else:
        post2monitoring('OK')
        driver.quit()
        exit(0)


