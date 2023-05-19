import unittest
import xmlrunner
import json
import time
import sys
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
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
                filename = 'error-%s.png' % fn.__name__
                driver.get_screenshot_as_file('img/' + filename)
                # print('Screenshot saved as img/%s' % filename)
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
        # basic data
        with open('basic_data.json') as data_file:
            cls.basic_data = json.load(data_file)
        cls.tests_results = []
        # create a new Chrome session
        options = Options()
        options.headless = True
        options.add_argument('--log-level=2')
        cls.driver = webdriver.Chrome(options=options)
        # cls.driver = webdriver.Chrome()
        cls.driver.implicitly_wait(10)
        # navigate to the application home page
        cls.driver.get(cls.basic_data['url'])
        WebDriverWait(cls.driver, 30).until(
            EC.presence_of_element_located((By.NAME, "txtEmail")))

    def test_01_check_messages(self):
        # Login
        time.sleep(1)
        user_name = self.basic_data['username']
        user_pass = self.basic_data['password']
        # user email
        username = self.driver.find_element_by_name("txtEmail")
        username.send_keys(user_name)
        self.driver.find_element_by_name("btnEmail").click()  # click next
        # user pass
        # time.sleep(2)  # change to wait till visible
        password = self.driver.find_element_by_name("txtPassword")
        password.send_keys(user_pass)
        self.driver.find_element_by_name("btnPassword").click()  # click next
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "img[src='/Images/StartMenu/Envelope_arrow_up.png']")))
        self.driver.get(self.basic_data['url'])
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.ID, "ContentPlaceHolder2_Panel5")))
        errors_on_screen = self.driver.find_elements_by_css_selector("input[src='../Images/Other/Status_error.png']")
        # errors_on_screen = self.driver.find_elements_by_css_selector("input[src='../Images/Other/need2fail.jpg']")
        print("There is {0} errors on screen".format(len(errors_on_screen)))
        self.assertEqual(0, len(errors_on_screen))

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
