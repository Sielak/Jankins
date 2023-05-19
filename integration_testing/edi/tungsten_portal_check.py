from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import time
import requests
import json


def check_failed_invoices_tungsten():
    # credentials
    user_name = 'edisupport@hl-display.com'
    user_pass = 'Marian1234%'
    driver.get("https://portal.tungsten-network.com/login.aspx")
    # Login to tungsten portal
    username = driver.find_element_by_name('userName')
    password = driver.find_element_by_name('password')
    username.send_keys(user_name)
    password.send_keys(user_pass)
    login = driver.find_element_by_name('btnLogon')
    login.click()
    time.sleep(5)
    try:
        auth = driver.find_element_by_class_name('text-uppercase')
        print(auth.text)
        if auth.text == 'WE JUST SENT YOU AN EMAIL':
            print('Computer needs authorization')
            driver.close()
            exit(1)
        elif auth.text == 'SET UP PASSWORD':
            print('Password expired. Please set up new one.')
            driver.close()
            exit(1)
    except NoSuchElementException:
        pass
    try:
        message = driver.find_element_by_id('mp_mc_btnClose')
        print('New message from Tungsten network')
        message.click()
    except NoSuchElementException:
        pass
    time.sleep(10)
    # Go to View all failed invoices
    try:
        driver.find_element_by_id('ViewAllFailedInvoices').click()
    except:
        time.sleep(30)
        driver.find_element_by_id('ViewAllFailedInvoices').click()
    time.sleep(5)
    # Retrieve whole table
    table = driver.find_element_by_xpath(
        "//table[@class='rgMasterTable formTable table-responsive']")
    rows = table.find_elements_by_xpath(
        "//tr[contains(@class, 'rgRow') or contains(@class, 'rgAltRow')]")
    header = table.find_elements_by_class_name('rgHeader')
    header_list = []
    for name in header:
        if len(name.text) > 1:
            header_list.append(name.text)

    row_list = [header_list]
    for row in rows:
        data_list = []
        row_data = row.find_elements_by_tag_name('td')
        for data in row_data:
            if len(data.text) > 1:
                data_list.append(data.text)
        data_list.append('x')
        row_list.append(data_list)

    return row_list


def post2monitoring(status):
    url = 'http://bma-iwa-101:8085/logExternalService/ext_edi_reg_portal_tungsten/{0}/test'.format(
        status)
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


driver = webdriver.Chrome()
test = check_failed_invoices_tungsten()
if len(test) == 1:
    print('Nothing to check, closing')
    post2monitoring('OK')
    exit(0)
else:
    print('Failed invoices !')
    for item in test:
        print(item)
    post2monitoring('NOK')
    exit(1)
driver.quit()
