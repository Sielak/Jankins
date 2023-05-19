from help_functions import SqlQueries, tesco_order
import unittest
import xmlrunner
import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import time


class ESalesTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # load basic data file
        with open('basic_data.json') as data_file:
            cls.basic_data = json.load(data_file)
        cls.tests_results = []
        # cls.customer_order_number = uuid1()
        cls.customer_order_number = str(int(datetime.timestamp(datetime.now())))
    
    def test_01_prepare_data_in_Jeeves(self):
        env = self.basic_data['jeeves_env']
        res = SqlQueries(env, 'EW1-SQL-711').prepare_data_in_jeeves()
        self.assertEqual(res, 'OK')

    def test_02_post_order_to_wso2(self):
        # basic data
        headers = {
            'Content-Type': 'application/xml'
        }
        print("customer_order_number", self.customer_order_number)
        r = requests.post(
            self.basic_data['wso2_endpoint'], 
            headers=headers, 
            data=tesco_order.format(customer_order_number=self.customer_order_number), 
            auth=(
                self.basic_data['wso2_username'], 
                self.basic_data['wso2_password']
            )
        )
        print("[DEBUG]", r.text)
        root = ET.fromstring(r.text)
        status = root.find("./Response/Status")
        result_status_code = status.get('code')
        result_status_text = status.get('text')
        self.assertListEqual(["200", "OK"], [result_status_code, result_status_text])

    def test_03_check_result_in_jeeves(self):
        print("[DEBUG] customer order number:", self.customer_order_number)
        env = self.basic_data['jeeves_env']
        sql_queries = SqlQueries(env, 'EW1-SQL-711')
        results = sql_queries.check_created_order(self.customer_order_number)
        self.assertNotIn(False, results)

    @classmethod
    def tearDownClass(cls):
        pass


if __name__ == '__main__':
    with open('test-reports/test_results.xml', 'w') as output:
        unittest.main(
            testRunner=xmlrunner.XMLTestRunner(output=output),
            failfast=False, buffer=False, catchbreak=False)


