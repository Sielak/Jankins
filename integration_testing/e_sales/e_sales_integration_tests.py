import unittest
import xmlrunner
import time
import random
from helpers.jeeves import Jeeves
from helpers.eshop import create_order
from playwright.sync_api import sync_playwright


class ESalesTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tests_results = []
        cls.ref_number = 'e_sales_{date}_{numbers}'.format(
            date=time.strftime('%Y-%m-%d'),
            numbers=random.randint(1000, 9999)
        )

    def test_01_create_order(self):
        Jeeves().check_pricelist()
        with sync_playwright() as playwright:
            result = create_order(playwright, self.ref_number)

        self.assertEqual(True, result)

    def test_02_check_integration(self):
        jeeves_object = Jeeves()
        time.sleep(10)  # needs to wait for order to create
        jeeves_data = jeeves_object.fetch_data_from_jeeves(self.ref_number)
        self.assertEqual([jeeves_data[1], jeeves_data[2]], [
                         '19 - E-portal', 'Entry in progress'])
        time.sleep(30)  # wait for rows to create
        jeeves_data_row = jeeves_object.count_order_rows(jeeves_data[0])
        self.assertEqual(jeeves_data_row, 'OK')

if __name__ == '__main__':
    with open('test-reports/test_results.xml', 'w') as output:
        unittest.main(
            testRunner=xmlrunner.XMLTestRunner(output=output),
            failfast=False, buffer=False, catchbreak=False)
