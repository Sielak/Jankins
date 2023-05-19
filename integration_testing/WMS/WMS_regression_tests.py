import unittest
import xmlrunner
import json
import time
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from help_functions import check_info_about_item, compare_item_bin_info, check_results
from functools import partialmethod


def sreenshotOnFail(browser_attr='driver'):
    def decorator(cls):
        def with_screen_shot(self, fn, *args, **kwargs):
            """Take a Screen-shot of the drive page, when a function fails."""
            try:
                return fn(self, *args, **kwargs)
            except Exception:
                # This will only be reached if the test fails
                driver = getattr(self, browser_attr)
                filename = 'error-{0}.png'.format(fn.__name__)
                driver.get_screenshot_as_file('img/' + filename)
                print('Screenshot saved as img/{0}'.format(filename))
                raise

        for attr, fn in cls.__dict__.items():
            if attr[:5] == 'test_' and callable(fn):
                setattr(cls, attr, partialmethod(with_screen_shot, fn))

        return cls
    return decorator


class Object(object):
    pass


@sreenshotOnFail()
class WMStest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # load basic data file
        with open('basic_data.json') as data_file:
            cls.basic_data = json.load(data_file)
        # create a new Firefox session """
        cls.driver = webdriver.Chrome()
        # navigate to the application home page """
        cls.driver.get("http://192.165.17.83/WMS/signIn")
        WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "j_username")))

    def test_01_login_page(self):
        user_name = 'dawy'
        user_pass = '<put_pass_here>'
        username = self.driver.find_element_by_name('j_username')
        password = self.driver.find_element_by_name('j_password')
        username.send_keys(user_name)
        password.send_keys(user_pass)
        self.driver.find_element_by_xpath('//*[@id="form"]/img').click()  # click login
        try:
            WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, "img[alt='STOCK TRANSFER']")))
            logon_result = 'OK'
        except NoSuchElementException:
            logon_result_raw = self.driver.find_element_by_class_name('errorblock')
            logon_result = logon_result_raw.text
        self.assertEqual('OK', logon_result)

    def test_02_change_company(self):
        WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, 'CompanyID')))
        company_drop_down_list = Select(self.driver.find_element_by_id('CompanyID'))
        company_drop_down_list.select_by_value(self.basic_data['foretagkod'])

    def test_03_item_bin_information(self):
        item_no = self.basic_data['item_number']
        jeeves_results = check_info_about_item(item_no)  # fetch data from jeeves
        # basic data START
        wms_balance_info = []
        wms_bin_info = []
        jvs_balance_info = jeeves_results['balance_info']
        jvs_bin_info = jeeves_results['bin_info']
        jvs_bin_name = jvs_bin_info[0]
        # basic data END
        self.driver.find_element_by_xpath('//*[@id="container"]/div[2]/div/div[4]/a/img').click()  # click item/bin info
        search_filed = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="container"]/div[2]/div/center/form/input[1]'))
        )  # wait for input loads
        search_filed.send_keys(item_no)  # fill input with item number
        self.driver.find_element_by_xpath('//*[@id="container"]/div[2]/div/center/form/input[2]').click()  # click submit
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="summaryTable"]/tbody/tr'))
        )  # Wait until table will be loaded
        item_rows = self.driver.find_elements_by_xpath('//*[@id="summaryTable"]/tbody/tr')  # search for all rows in body of table
        main_warehouse_row = ''
        for i in item_rows:
            # search only for main warehouse
            if 'Main warehouse (0)' in i.text:
                inventory_row = i.find_elements_by_tag_name('td')
                for item in inventory_row:
                    wms_balance_info.append(item.text)
                main_warehouse_row = i  # assign item to mainwarehouse to avoid stale element not in DOM error
        main_warehouse_row.click()  # click on row with main warehouse
        bin_table_rows = self.driver.find_elements_by_xpath('//*[@id="itemonbins"]/tbody/tr')
        for bin in bin_table_rows:
            if jvs_bin_name in bin.text:
                bin_row = bin.find_elements_by_tag_name('td')
                for item in bin_row:
                    wms_bin_info.append(item.text)
        # compare data
        a = compare_item_bin_info(wms_balance_info, jvs_balance_info)
        b = compare_item_bin_info(wms_bin_info, jvs_bin_info)
        if 'NOK' in [a, b]:
            test_results = 'NOK'
        else:
            test_results = 'OK'
        self.assertEqual('OK', test_results)

    def test_04_indelivery(self):
        po_number = self.basic_data['po_number']
        self.driver.find_element_by_css_selector("a[href='/WMS/']").click()  # go to main page
        indelivery_button = self.driver.find_element_by_xpath('//*[@id="container"]/div[2]/div/div[3]/a/img')
        indelivery_button.click()
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.ID, "searchForm"))
        )
        search_form = self.driver.find_element_by_name('searchString')
        search_form.send_keys(po_number)
        self.driver.find_element_by_xpath('//*[@id="searchForm"]/input[2]').click()
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="indeliveryTable"]'))
        )
        try:
            self.driver.find_element_by_xpath('//*[@id="indeliveryTable"]/tbody/tr[1]').click()  # table_first_row
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="form"]'))
            )
            bin_table_first_row = self.driver.find_element_by_xpath(
                '//*[@id="itemOnBinsIndeliveryTable"]/tbody/tr[1]')
            bin_table_first_row_list = bin_table_first_row.find_elements_by_tag_name('td')
            self.basic_data['bin_from'] = bin_table_first_row_list[0].text  # collect bin name for test_05
            bin_table_first_row.click()  # Click first row of table to choose bin
            self.driver.find_element_by_id('button').click()  # Click confirm indelivery
            try:
                error_indelivery = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'errorblock'))
                )  # check if error exists
            except TimeoutException:
                error_indelivery = Object()
                error_indelivery.text = 'OK'
            if 'Error' not in error_indelivery.text:
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="dialog"]/p'))
                )
                self.driver.find_element_by_xpath('/html/body/div[2]/div[11]/div/button').click()  # Click OK
            else:
                print(error_indelivery.text)
            test_results_raw = check_results(po_number)
            test_results = 'NOK'
            if test_results_raw == 70:
                test_results = 'OK'
        except NoSuchElementException:
            print('[ERROR] PO not found in WMS')
            test_results = 'NOK'
        self.assertEqual('OK', test_results)

    def test_05_stock_transfer(self):
        test_results = 'NOK'
        self.driver.find_element_by_css_selector("a[href='/WMS/']").click()  # go to main page
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "img[alt='INDELIVERY']")))  # wait for homepage
        self.driver.find_element_by_css_selector("a[href='/WMS/stockTransfer']").click()  # go to stock transfer
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'ItemNumber')))  # wait for form load
        item_number = self.driver.find_element_by_id('ItemNumber')
        bin_from = self.driver.find_element_by_id('fromBin')
        bin_to = self.driver.find_element_by_id('toBin')
        quantity = self.driver.find_element_by_id('quantity')
        item_number.send_keys(self.basic_data['item_number'])
        bin_from.send_keys(self.basic_data['bin_from'])
        bin_to.send_keys(self.basic_data['bin_to'])
        quantity.send_keys(self.basic_data['qty'])
        self.driver.find_element_by_id('button').click()
        try:
            print(self.driver.find_element_by_class_name('errorblock').text)
        except NoSuchElementException:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'dialog')))  # wait for confirmation
            dialog_box = self.driver.find_element_by_id("dialog")
            dialog_text = dialog_box.find_element_by_tag_name('p')
            if 'successfully' in dialog_text.text:
                test_results = 'OK'
            button_div = self.driver.find_element_by_class_name('ui-dialog-buttonset')
            button_div.find_element_by_tag_name('button').click()  # click OK on dialog

        self.assertEqual('OK', test_results)

    @classmethod
    def tearDownClass(cls):
        # close the browser window
        cls.driver.quit()
        time.sleep(1)  # 1 second sleep to avoid webdriver error

    def is_element_present(self, how, what):
        """
        Helper method to confirm the presence of an element on page
        :params how: By locator type
        :params what: locator value
        """
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException:
            return False
        return True


if __name__ == '__main__':
    with open('test-reports/test_results.xml', 'w') as output:
        unittest.main(
            testRunner=xmlrunner.XMLTestRunner(output=output),
            failfast=False, buffer=False, catchbreak=False)
