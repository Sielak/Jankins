from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class eshop_login:

    def __init__(self, browser, basic_data):
        self.browser = browser
        self.basic_data = basic_data

    def open_page(self):
        # navigate to the application home page """
        self.browser.get(self.basic_data['shop_URL'])
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[formcontrolname='username']")))

    def change_language(self):
        # Change language of webpage to eng
        self.browser.find_element_by_css_selector(
            "button[class='btn dropdown-toggle']").click()
        language_drop_down = self.browser.find_element_by_css_selector(
            "div[class='dropdown-menu show']")
        language_drop_down.find_elements_by_tag_name('button')[0].click()

    def login(self):
        user_name = self.basic_data['user']
        user_pass = self.basic_data['pass']
        username = self.browser.find_element_by_css_selector(
            "input[formcontrolname='username']")
        password = self.browser.find_element_by_css_selector(
            "input[formcontrolname='password']")
        username.send_keys(user_name)
        password.send_keys(user_pass)
        self.browser.find_element_by_xpath(
            "//button[contains(@class, 'btn btn-primary')]").click()  # click login
        try:
            WebDriverWait(self.browser, 30).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'Products')]")))
            logon_result = 'OK'
        except NoSuchElementException:
            logon_result = 'NOK'
        
        return logon_result