from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Инициализация драйвера Chrome
def initialize_driver():
    chrome_options = Options()
    chrome_options.binary_location = '/usr/bin/google-chrome'
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--headless")  # Раскомментируйте, чтобы запустить в безголовом режиме

    driver = webdriver.Chrome(options=chrome_options)
    return driver

# Вход на сайт
def login(driver, login, password, login_url):
    driver.get(login_url)
    login_element = driver.find_element(By.ID, "mui-1")
    password_element = driver.find_element(By.ID, "mui-2")

    login_element.send_keys(login)
    password_element.send_keys(password)
    password_element.send_keys(Keys.ENTER)
