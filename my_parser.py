import csv
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

# Настройки логирования
logging.basicConfig(filename='parser.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger = logging.getLogger()
logger.addHandler(console_handler)

# Функция для выполнения парсинга
def parse_and_save(driver):
    # URL-ы для парсинга (можете добавить нужные URL-ы в список)
    urls_to_parse = [f'https://edu.21-school.ru/calendar/review/{number}' for number in range(0, 99999)]

    try:
        # Выполнение основного сценария
        with open('output.csv', mode='w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['URL', 'Заголовок'])

            for url in urls_to_parse:
                driver.get(url)
                logger.info(f'Открыта страница: {url}')

                try:
                    # Выполняем JavaScript, чтобы получить текст из элемента <h2 class="jss56">
                    time.sleep(4)
                    title = driver.execute_script('return document.querySelector("h2.jss56").textContent')
                    title = title.strip()  # Убираем лишние пробелы

                    csv_writer.writerow([url, title])
                    logger.info(f'Записано: {url}, {title}')

                except Exception as e:
                    logger.error(f'Ошибка на странице {url}: {e}')

    except Exception as e:
        logger.error(f'Ошибка при выполнении парсинга: {e}')


# Проверка, выполняется ли файл напрямую, а не импортируется
if __name__ == "__main__":
    chrome_options = Options()
    chrome_options.binary_location = '/usr/bin/google-chrome'
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.add_argument("--headless")  # Раскомментируйте, чтобы запустить в безголовом режиме
    chrome_options.add_argument("--no-sandbox")

    # Установка переменной окружения PATH для chromedriver
    os.environ['PATH'] = f'{os.environ["PATH"]}:/usr/local/bin'

    with webdriver.Chrome(options=chrome_options) as driver:
        logger.info('Браузер успешно открыт')
        parse_and_save(driver)
