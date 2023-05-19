from help_functions import SqlQueries
import unittest
import xmlrunner
import json
import subprocess
import time
import requests


class PIMTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # load basic data file
        with open('basic_data.json') as data_file:
            cls.basic_data = json.load(data_file)
        cls.tests_results = []
        print('[INFO] Change data in pim')
        subprocess.run(["EntityValueSetter/EntityValueSetter.exe", "EntityValueSetter/ConfigChange.txt"])
        print('[INFO] Time buffer for PIM')
        time.sleep(20)
        print('[INFO] Run integration')
        response = requests.get(cls.basic_data['integration_url'])
        print(response.text)
        print('[INFO] Time buffer for integration')
        time.sleep(10)

    def test_01_compare_data(self):
        # basic data
        # env = self.basic_data['env_prod']  # PROD
        env = self.basic_data['env_test']  # TEST
        sql_queries = SqlQueries(env, 'EW1-SQL-716')
        tests_results = []
        data_file = {}
        with open("EntityValueSetter/ConfigChange.txt", encoding='utf-8-sig') as f:
            for line in f:
                (key, val) = line.split('=')
                data_file[key] = val.rstrip()
        data_sql_original = sql_queries.fetch_product_info(data_file['EntityID'])
        for key, value in data_sql_original.items():
            if str(data_file[key]) != str(value):
                print('ERROR on field', key, data_file[key], '<==>', value)
                tests_results.append('NOK')

        self.assertNotIn('NOK', tests_results)

    @classmethod
    def tearDownClass(cls):
        print('[INFO] Change data in pim to original values')
        subprocess.run(["EntityValueSetter/EntityValueSetter.exe", "EntityValueSetter/ConfigOrg.txt"])
        print('[INFO] Time buffer for PIM')
        time.sleep(20)
        print('[INFO] Run integration')
        response = requests.get(cls.basic_data['integration_url'])
        print(response.text)


if __name__ == '__main__':
    with open('test-reports/test_results.xml', 'w') as output:
        unittest.main(
            testRunner=xmlrunner.XMLTestRunner(output=output),
            failfast=False, buffer=False, catchbreak=False)


"""
TEST1
test5
zmieniasz sobie cos na q_product (najlepiej description)
generuje sie wpis do dp_data
i chodzi job ktory wysyla dane do PIM
i moge sprawdzic w dp_data czy poszlo ok
a potem wchodzisz na PIM web portal i sprawdzsz czy widac zmiany.

TEST2
zmieniasz dane w PIM WEB portal
kredki:
email + "yw5_Z9mi-BU5fU*"
leci strzal do API
zapisuje do DP data
i aktualizuje dane q_product

URL test = http://bma-dev-705:8103/docs
"""