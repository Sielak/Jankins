from help_functions import sql_queries as query
from help_functions import upload_file_sftp
import time
import unittest
import xmlrunner
import json
import datetime
from shutil import copyfile
import requests


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
        sql_queries = query(env, 'EW1-SQL-711')
        today = datetime.datetime.strftime(datetime.datetime.today(), '%Y%m%d')
        # check if integration was runned today already
        file_version = 1
        prev_filename = self.basic_data['filename_params'].split('-')
        if prev_filename[0][-8:] == today:
            file_version = int(prev_filename[1].split('.')[0]) + 1  # add 1 to file version
        else:
            pass
        filename = 'Orders_HL_1600_poca_1190_{0}-{1}.xml'.format(today, file_version)
        filename_params = 'Parameters_HL_Display_1600_{0}-{1}.xml'.format(today, file_version)
        # prepare data in jeeves
        print('Update item data')
        sql_queries.update_item()
        print('Update item balances')
        sql_queries.update_item_balances()
        # prepare XML file
        xml_for_basic_data = """<?xml version="1.0" encoding="UTF-8"?>
        <Recommended_orders>
            <Supplier>
                <WarehouseCode>1600</WarehouseCode>
                <SupplierCode>1190</SupplierCode>
                <BuyerCode>dawy</BuyerCode>
                <ConfirmedBy>dawid.wybierek@hl-display.com</ConfirmedBy>
            </Supplier>
            <OrderRows>
                <OrderLineCount>1</OrderLineCount>
                <OrderLine>
                    <ItemCode>200088</ItemCode>
                    <OrderQuantity>100</OrderQuantity>
                    <RequestDispatchDate>{0}</RequestDispatchDate>
                </OrderLine>
            </OrderRows>
        </Recommended_orders>""".format(today)
        with open('basic_data_po.xml', 'w') as f:
            f.write(xml_for_basic_data)
        # copy prepared file to server
        upload_file_sftp(filename, 'po')
        upload_file_sftp(filename_params, 'params')
        # copyfile('basic_data_po.xml', self.basic_data['es_root_path'] + filename)
        # copyfile('basic_data_params.xml', self.basic_data['es_root_path'] + filename_params)
        # update filenames in config file
        self.basic_data['filename_po'] = filename
        self.basic_data['filename_params'] = filename_params
        with open("basic_data.json", "w") as jsonFile:
            json.dump(self.basic_data, jsonFile, indent=4, sort_keys=True)
        # run integration
        response = requests.get(self.basic_data['integration_url'])
        response_params = requests.get(self.basic_data['integration_url_params'])
        self.assertListEqual([202, 202], [response.status_code, response_params.status_code])

    def test_02_check_results(self):
        # need to wait 120 sek to integrations
        print('Sleeping for 120 sek...')
        time.sleep(120)
        print('Test resumed')
        # basic data
        # env = self.basic_data['env_prod']  # PROD
        env = self.basic_data['env_test']  # TEST
        sql_queries = query(env, 'EW1-SQL-711')
        # start tests
        tests_results = []
        # check data on item
        print('Fetch data from item')
        results = sql_queries.fetch_item_data()
        db_data = []
        if len(results) == 0:
            print('Somesing is no yes --> item not found')
        else:
            for item in results:
                db_data.append(item)
        test_data = [
            self.basic_data['test_data_Item'],
            self.basic_data['test_data_Cooq'],
            self.basic_data['test_data_BufferStock'],
            self.basic_data['test_data_OrderLevel'],
            self.basic_data['test_data_PickClass'],
            self.basic_data['test_data_VauClass'],
            self.basic_data['test_data_Stocked']
        ]
        for db_field, test_field in zip(db_data, test_data):
            if str(db_field) == test_field:
                tests_results.append('OK')
            else:
                print('[ERROR] Field on item is different')
                print(db_field, '<--->', test_field)
                tests_results.append('NOK')
        # check created PO
        print('Fetch data from PO')
        results = sql_queries.fetch_po_data(self.basic_data['filename_po'])
        if len(results) > 1:
            print('[ERROR] Too many records on PO')
            tests_results.append('NOK')
        elif len(results) == 0:
            print('[ERROR] No PO found')
            tests_results.append('NOK')
        else:
            po_data = results[0]
            item_number = po_data[0]
            item_qty = po_data[1]
            if item_number == self.basic_data['test_data_Item'] and str(item_qty) == self.basic_data['test_data_RowQty']:
                tests_results.append('OK')
            else:
                print('[ERROR] Data on PO is incorrect')
                print('expected: ', self.basic_data['test_data_Item'], '<-->', item_number)
                print('expected: ', self.basic_data['test_data_RowQty'], '<-->', item_qty)
                tests_results.append('NOK')
        self.assertNotIn('NOK', tests_results)

    @classmethod
    def tearDownClass(cls):
        pass


if __name__ == '__main__':
    with open('test-reports/test_results.xml', 'w') as output:
        unittest.main(
            testRunner=xmlrunner.XMLTestRunner(output=output),
            failfast=False, buffer=False, catchbreak=False)