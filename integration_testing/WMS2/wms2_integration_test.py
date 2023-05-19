from os import error
from pydantic import errors
from help_functions import SqlQueries
import unittest
import xmlrunner
import json
import requests
from models import BasicData


class ESalesHealthCheckTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # load basic data file
        with open('basic_data_test.json') as data_file:
            json_data = json.load(data_file)
        cls.basic_data = BasicData(**json_data)
        cls.tests_results = []
    
    def test_01_check_wso2_webhook(self):
        r = requests.get(self.basic_data.url_wso2, verify=False)
        self.assertEqual(b'{"detail":[{"loc":["body"],"msg":"field required","type":"value_error.missing"}]}', r.content)
        self.assertEqual(422, r.status_code)

    def test_02_check_every_endpoint(self):
        r = requests.get(self.basic_data.url_api_root + "/openapi.json")
        endpoint_list = json.loads(r.content)
        print("Checking endpoints")
        print("------------------")
        for endpoint, method in endpoint_list['paths'].items():
            print(self.basic_data.url_api_root + endpoint)
            if "post" in method:
                endpoint_request = requests.get(self.basic_data.url_api_root + endpoint)
                self.assertEqual(405, endpoint_request.status_code)
            elif "get" in method:
                endpoint_request = requests.post(self.basic_data.url_api_root + endpoint)
                self.assertEqual(405, endpoint_request.status_code)
            else:
                print('Unsupported method')
                self.assertEqual(405, 200)
    
    def test_03_check_communication_between_wso2_and_fastAPI(self):
        r = requests.get(self.basic_data.url_api_root + "/openapi.json")
        self.assertIn(b'"info":{"title":"FastAPI"', r.content)

    @classmethod
    def tearDownClass(cls):
        pass


class ESalesHealthCheckProd(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # load basic data file
        with open('basic_data_prod.json') as data_file:
            json_data = json.load(data_file)
        cls.basic_data = BasicData(**json_data)
        cls.tests_results = []
    
    def test_01_check_wso2_webhook(self):
        r = requests.get(self.basic_data.url_wso2, verify=False)
        self.assertEqual(b'{"detail":[{"loc":["body"],"msg":"field required","type":"value_error.missing"}]}', r.content)
        self.assertEqual(422, r.status_code)

    def test_02_check_every_endpoint(self):
        r = requests.get(self.basic_data.url_api_root + "/openapi.json")
        endpoint_list = json.loads(r.content)
        print("Checking endpoints")
        print("------------------")
        for endpoint, method in endpoint_list['paths'].items():
            print(self.basic_data.url_api_root + endpoint)
            if "post" in method:
                endpoint_request = requests.get(self.basic_data.url_api_root + endpoint)
                self.assertEqual(405, endpoint_request.status_code)
            elif "get" in method:
                endpoint_request = requests.post(self.basic_data.url_api_root + endpoint)
                self.assertEqual(405, endpoint_request.status_code)
            else:
                print('Unsupported method')
                self.assertEqual(405, 200)
    
    def test_03_check_communication_between_wso2_and_fastAPI(self):
        r = requests.get(self.basic_data.url_api_root + "/openapi.json")
        self.assertIn(b'"info":{"title":"FastAPI"', r.content)

    @classmethod
    def tearDownClass(cls):
        pass


if __name__ == '__main__':
    with open('test-reports/test_results.xml', 'w') as output:
        unittest.main(
            testRunner=xmlrunner.XMLTestRunner(output=output),
            failfast=False, buffer=False, catchbreak=False)