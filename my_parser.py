import threading
import logging
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import requests
import csv
import connector
import tg_bot
from connector import initialize_driver

# connector.parser_thread = Thread(target=run_parser)
# connector.parser_thread.start()

# Настроим логирование
logging.basicConfig(filename='parser.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger = logging.getLogger()
logger.addHandler(console_handler)

# Добавьте глобальную переменную для хранения состояния парсера (запущен/остановлен)
parser_running = False
parser_thread = None
driver = None

# Функция для запуска парсера
def start_parser():
    global parser_thread
    if parser_thread and parser_thread.is_alive():
        logger.info("Парсер уже запущен из my_parser")
    else:
        parser_thread = threading.Thread(target=run_parser)
        parser_thread.start()

# Функция для остановки парсера
def stop_parser():
    global parser_running
    if parser_running:
        parser_running = False
        if driver:
            try:
                driver.quit()
                logger.info("Парсер остановлен из my_parser")
            except Exception as e:
                logger.error(f"Произошла ошибка при остановке драйвера: {str(e)}", exc_info=True)
    else:
        logger.info("Парсер не был запущен из my_parser")

# Модифицируйте функцию `run_parser` для проверки состояния `parser_running`
def run_parser():
    global driver
    global parser_running
    driver = initialize_driver()
    with open('log_pass.txt', 'r') as login_pass_file:
        lines = login_pass_file.readlines()
        if len(lines) >= 2:
            my_login = lines[0].strip()
            password = lines[1].strip()
        else:
            logger.error("Файл 'log_pass.txt' должен содержать логин и пароль на двух разных строках.")
            return

    login_url = "https://auth.sberclass.ru/auth/realms/EduPowerKeycloak/protocol/openid-connect/auth?client_id=school21&redirect_uri=https%3A%2F%2Fedu.21-school.ru%2F&state=32a4629c-9404-46ca-8729-fb3cae801c1c&response_mode=fragment&response_type=code&scope=openid&nonce=9ca33f99-639f-44a4-8ad3-1b0bad3257f1"

    try:
        connector.login(driver, my_login, password, login_url)
        parse_and_save(driver)
        logger.info(f'Парсинг завершён')
    except ConnectionRefusedError:
        logger.error("Произошла ошибка: Connection refused. Проверьте доступность сервера и интернет-соединения.")
    finally:
        driver.quit()


def parse_and_save(driver):
    
    url = 'https://edu.21-school.ru/projects/'
    driver.get(url)
    logger.info(f'Открыта страница: {url}')

    try:
        while True:
            try:
                
                element1 = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/div/div[2]/div/section/div/div[3]/div[2]/a/div/div[1]/p'))
                )
                element1.click()
                current_url = driver.current_url
                logger.info(f'Открыта страница: {current_url}')

                element2 = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/div/div[2]/div/aside/div[1]/div/div/button/span'))
                )
                element2.click()
                current_url = driver.current_url
                logger.info(f'Открыта страница: {current_url}')

            except NoSuchElementException as e:
                logger.error(f'Элемент не найден: {str(e)}', exc_info=False)
            except TimeoutException as e:
                logger.error(f'Истекло время ожидания: {str(e)}', exc_info=False)
            except ConnectionRefusedError as e:
                logger.error(f'Разрыв соединения: {str(e)}', exc_info=False)
            except ConnectionAbortedError as e:
                logger.error(f'Произошла ошибка + sleep 5: {str(e)}', exc_info=False)
                #time.sleep(5)
            except ConnectionError as e:
                logger.error(f'Произошла ошибка соединения: {str(e)}', exc_info=False)

            while True:
                try:
                    link_elements = driver.find_elements(By.XPATH, '/html/body/div/div[4]/div/div/3/div[4]/div/div[1]')
                    links = [element.get_attribute('href') for element in link_elements]

                    if not links:
                        logger.info(f'Ищем проверяющих на странице: {current_url}')
                    else:
                        logger.info(f'Найден проверяющий для проекта')  # Запись в лог
                        logger.info(f'Найдены следующие проверяющие: {", ".join(links)}')

                        with open('output.csv', mode='w', newline='', encoding='utf-8') as csv_file:
                            csv_writer = csv.writer(csv_file)
                            csv_writer.writerow(['Ссылки'])
                            csv_writer.writerows([[link] for link in links])

                        driver.quit()
                        return

                except requests.exceptions.ConnectionError as e:
                    logger.error(f'Произошла ошибка соединения: {str(e)}', exc_info=False)
                    time.sleep(10)
                finally:
                    break
    except KeyboardInterrupt:
        driver.quit()
        logger.info('Прервано пользователем.')
    except Exception as e:
        driver.quit()
        logger.error(f'Произошла ошибка: {str(e)}', exc_info=False)
    finally:
        driver.quit()

if __name__ == "__main":
    initialize_driver()
