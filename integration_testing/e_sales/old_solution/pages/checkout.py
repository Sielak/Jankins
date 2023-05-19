from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


class eshop_checkout:

    def __init__(self, browser, basic_data):
        self.browser = browser
        self.basic_data = basic_data

    def go2checkout(self):
        self.browser.find_element_by_css_selector(
            "a[routerlink='/checkout']").click()
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(text(),'Continue to shipping')]")))
        button = self.browser.find_element_by_xpath(
            "//button[contains(text(),'Continue to shipping')]")
        button.send_keys("\n")  # workaround because click() dont work for this

    def fill_reference_number_and_confirm(self):
        reference_number = self.browser.find_element_by_id("oh.kundbestnr")
        reference_number.send_keys(self.basic_data['ref_number'])
        self.browser.find_element_by_xpath("//span[contains(text(),'Confirm')]").click()
        
    def final_confirmation(self):
        self.browser.find_element_by_xpath(
            "//button[contains(text(),'Confirm order')]").click()  # send order to prod
        try:
            WebDriverWait(self.browser, 60).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'Thank you for your order!')]")))
            results = 'OK'
        except TimeoutException:
            results = 'NOK'
        
        return results