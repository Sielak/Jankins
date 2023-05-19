from help_functions import SqlQueries
import unittest
import xmlrunner
import json


class ESalesTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # load basic data file
        with open('basic_data.json') as data_file:
            cls.basic_data = json.load(data_file)
        cls.tests_results = []
    
    def test_01_prepare_data(self):
        # basic data
        env = self.basic_data['env_prod']  # PROD
        # env = self.basic_data['env_test']  # TEST
        sql_queries = SqlQueries(env, 'EW1-SQL-711')
        a = 202
        b = 202
        self.assertListEqual([202, 202], [a, b])

    def test_02_check_results(self):
        # basic data
        env = self.basic_data['env_prod']  # PROD
        # env = self.basic_data['env_test']  # TEST
        tests_results = ['OK', 'OK']
        self.assertNotIn('NOK', tests_results)

    @classmethod
    def tearDownClass(cls):
        pass


if __name__ == '__main__':
    with open('test-reports/test_results.xml', 'w') as output:
        unittest.main(
            testRunner=xmlrunner.XMLTestRunner(output=output),
            failfast=False, buffer=False, catchbreak=False)