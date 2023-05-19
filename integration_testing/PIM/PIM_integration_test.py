import help_functions
import unittest
import xmlrunner
import json
import time


class PIMTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # load basic data file
        with open('config.json') as data_file:
            cls.config = json.load(data_file)

    def test_01_jeeves2pim(self):
        jeeves_object = help_functions.SqlQueries(self.config)
        # jeeves_object.clear_dp_data()
        jeeves_object.change_product_data_in_jeeves()
        time.sleep(10)
        self.assertEqual(True, jeeves_object.check_dp_data_created()) 
        record_posted = False
        for _ in range(0, 10):
            if jeeves_object.check_dp_data_posted() != None:
                record_posted = True
                break
            time.sleep(60)
        self.assertEqual(True, record_posted)
        time.sleep(60)  # wait for changes in PIM
        product_data_in_pim = help_functions.PimChecker(self.config).check_product_data()
        expected_results = {
            "Name": "Auto test to PIM",
            "Assortment": "Other",
            "Status": "Sellable",
            "Owner": "Lennart Johansson",
            "Trademark": "Next™",
            "Function": "Alarm",
            "Attribute": "1008"
        }
        self.assertEqual(expected_results, product_data_in_pim)

        
    def test_02_pim2jeeves(self):
        jeeves_object = help_functions.SqlQueries(self.config)
        # jeeves_object.clear_dp_data()
        help_functions.PimChecker(self.config).change_product_data()
        record_posted = False
        for _ in range(0, 10):
            if jeeves_object.check_dp_data_created(pim2jeeves=True) is True:
                if jeeves_object.check_dp_data_posted(pim2jeeves=True) == "I":
                    record_posted = True
                    break
            time.sleep(60)
        self.assertEqual(True, record_posted)
        time.sleep(30)  # wait for changes in Jeeves
        product_data_in_jeeves = jeeves_object.check_product_data_in_jeeves()
        expected_data = {
            "Name": "Auto test to Jeeves",
            "Assortment": "BASE",
            "Status": "Pending",
            "Owner": '7',
            "Trademark": "iDisplay",
            "ItemClass": 130,
            "KeyConcept": "Fresh",
            "System": "DigitalScreens",
            "ProductHeadline": "Fixture kit for banners for automated test"
        }
        self.assertEqual(expected_data, product_data_in_jeeves)

    @classmethod
    def tearDownClass(cls):
        jeeves_object = help_functions.SqlQueries(cls.config)
        jeeves_object.change_product_data_in_jeeves(original_value=True)
        print("[INFO] Data in jeeves changed to original values")
        help_functions.PimChecker(cls.config).change_product_data(original_value=True)
        print("[INFO] Data in PIM changed to original values")

if __name__ == '__main__':
    with open('test-reports/test_results.xml', 'w', encoding="utf-8") as output:
        unittest.main(
            testRunner=xmlrunner.XMLTestRunner(output=output),
            failfast=False, buffer=False, catchbreak=False)
