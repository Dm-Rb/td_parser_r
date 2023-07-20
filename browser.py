from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from config import ConfigBrowser
import time
from seleniumwire.utils import decode as sw_decode


def explicit_waits(elem, method, driver):
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((method, elem))
        )
        return element
    except Exception(f'explicit_waits-> elem == {elem}'):
        driver.quit()


def authorization(driver):

    print('> get_headers > authorization')
    username_field = '//*[@id="userName"]'
    password_field = '//*[@id="password"]'
    enter_button = '//*[@id="full-width-body"]/scrollable-layout/div/div/div[1]/div[2]/div/div/div/full-width-content/div/login-form/div/div/fieldset/div/form/div[5]/div[2]/div/div[1]/button'
    privacy_settings_button = '#ppms_cm_reject-all'
    explicit_waits(username_field, By.XPATH, driver).send_keys(ConfigBrowser.username)
    explicit_waits(password_field, By.XPATH, driver).send_keys(ConfigBrowser.password)
    explicit_waits(privacy_settings_button, By.CSS_SELECTOR, driver).click()
    explicit_waits(enter_button, By.XPATH, driver).click()

    return driver

def get_headers():
    from config import ConfigBrowser

    # statr Chrome
    print('> get_headers')

    # other Chrome options
    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--ignore-certificate-errors-spki-list')
    # chrome_options.add_argument('--ignore-ssl-errors')

    # service = ChromeService(executable_path=ChromeDriverManager().install())
    # driver = webdriver.Chrome(service=service)
    from selenium.webdriver.chrome.service import Service
    driver_service = Service(executable_path=ConfigBrowser.webdriver)
    driver = webdriver.Chrome(service=driver_service)

    driver.get(ConfigBrowser.url_login)
    time.sleep(2)
    authorization(driver)
    time.sleep(2)
    while True:
        current_url = driver.current_url
        if current_url == ConfigBrowser.url_home and len(driver.requests) >= 85:
            for request in driver.requests:
                if request:
                    body_bytes = sw_decode(request.body, request.headers.get('Content-Encoding', 'identity'))
                    body_str = body_bytes.decode("utf8")
                    if "getArticles" in body_str:
                        headers = dict(request.headers)
                        del headers['content-length']

                        print('headers received and transferred to cls. RequestToAPI')
                        return headers
