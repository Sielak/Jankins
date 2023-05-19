from selenium import webdriver
import time


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
	
driver = webdriver.Chrome()
login2tieto()