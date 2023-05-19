import unittest
import xmlrunner
import json
import time
import random
from selenium import webdriver
from help_functions import fetch_data_from_jeeves, count_order_rows, check_pricelist
from functools import partialmethod
from pages.login import eshop_login
from pages.products import eshop_products
from pages.checkout import eshop_checkout


def sreenshotOnFail(browser_attr='driver'):
    def decorator(cls):
        def with_screen_shot(self, fn, *args, **kwargs):
            """Take a Screen-shot of the drive page, when a function fails."""
            try:
                return fn(self, *args, **kwargs)
            except Exception:
                # This will only be reached if the test fails
                driver = getattr(self, browser_attr)
                filename = 'error-%s.png' % fn.__name__
                driver.get_screenshot_as_file('img/' + filename)
                print('Screenshot saved as img/%s' % filename)
                raise

        for attr, fn in cls.__dict__.items():
            if attr[:5] == 'test_' and callable(fn):
                setattr(cls, attr, partialmethod(with_screen_shot, fn))

        return cls
    return decorator
    

@sreenshotOnFail()
class ESalesTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # load basic data file
        with open('basic_data.json') as data_file:
            cls.basic_data = json.load(data_file)
        cls.tests_results = []
        cls.ref_number = 'e_sales_{date}_{numbers}'.format(
            date=time.strftime('%Y-%m-%d'),
            numbers=random.randint(1000, 9999)
        )
        cls.basic_data['ref_number'] = cls.ref_number
        # create a new Chrome session """
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument("--headless")
        cls.driver = webdriver.Chrome(options=options)
        cls.driver.implicitly_wait(30)
        check_pricelist()

    def test_01_login_page(self):
        login_page = eshop_login(self.driver, self.basic_data)
        login_page.open_page()
        login_page.change_language()
        logon_result = login_page.login()
        self.assertEqual('OK', logon_result)
    
    def test_02_add_item_to_basket(self):
        products_page = eshop_products(self.driver, self.basic_data)
        products_page.add_items2basket()
        products_result = products_page.check_basket_counter()
        self.assertEqual(products_result, '2')
    
    def test_03_checkout(self):
        checkout_page = eshop_checkout(self.driver, self.basic_data)
        checkout_page.go2checkout()
        checkout_page.fill_reference_number_and_confirm()
        checkout_result = checkout_page.final_confirmation()

        self.assertEqual(checkout_result, 'OK')

    def test_04_check_integration(self):
        time.sleep(5)  # needs to wait for order to create
        jeeves_data = fetch_data_from_jeeves(self.ref_number)
        self.assertEqual([jeeves_data[1], jeeves_data[2]], [
                         '19 - E-portal', 'Entry in progress'])
        time.sleep(30)  # wait for rows to create
        jeeves_data_row = count_order_rows(jeeves_data[0])
        self.assertEqual(jeeves_data_row, 'OK')

    @classmethod
    def tearDownClass(cls):
        # close the browser window
        cls.driver.quit()
        time.sleep(1)  # 1 second sleep to avoid webdriver error


if __name__ == '__main__':
    with open('test-reports/test_results.xml', 'w') as output:
        unittest.main(
            testRunner=xmlrunner.XMLTestRunner(output=output),
            failfast=False, buffer=False, catchbreak=False)

# playwright codegen https://inriver2euw.productmarketingcloud.com/app/dashboard
