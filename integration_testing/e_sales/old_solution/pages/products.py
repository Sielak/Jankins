import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By


class eshop_products:

    def __init__(self, browser, basic_data):
        self.browser = browser
        self.basic_data = basic_data

    def add_items2basket(self):
        self.browser.find_element_by_xpath(
            "//a[contains(text(),'Products')]").click()
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(text(),'Add')]")))
        items_list = self.browser.find_elements_by_xpath(
            "//button[contains(text(),'Add')]")
        items_list[0].click()
        items_list[1].click()

    def check_basket_counter(self):
        # need to add this wait because webshop sometimes have lags
        time.sleep(5)
        badge = self.browser.find_element_by_xpath(
            "//span[contains(@class, 'badge badge-pill badge-primary badge-indicator')]")
        
        return badge.text