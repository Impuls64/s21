import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import telebot
from selenium import webdriver
import my_parser
from threading import Thread
import logging
from telebot import types
import sys
from connector import initialize_driver, driver

# Глобальная переменная для хранения драйвера
bot_driver = driver

# Функция для установки драйвера
def set_driver(driver):
    global bot_driver
    bot_driver = driver

# Переменная для хранения потока парсера
parser_thread = None

# Функция для запуска бота
def run_bot():
    try:
        logging.info("Запуск ТГ бота в файле tg_bot")
        bot.polling(none_stop=True)
    except Exception as e:
        logging.error(f"Произошла ошибка при запуске бота: {e}")

# Проверяем наличие опции --debug в аргументах командной строки
debug_mode = "--debug" in sys.argv

# Устанавливаем уровень логирования в зависимости от режима
if debug_mode:
    logging.basicConfig(
        level=logging.DEBUG,
        filename='parser.log',
        filemode='a',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
else:
    logging.basicConfig(
        level=logging.INFO,
        filename='parser.log',
        filemode='a',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def get_bot_token_and_chat_id():
    with open('log_pass.txt', 'r') as login_pass_file:
        lines = login_pass_file.readlines()
        if len(lines) >= 4:
            bot_token = lines[2].strip()  # ВАШ_ТОКЕН_БОТА
            chat_id = lines[3].strip()    # ВАШ_CHAT_ID
            return bot_token, chat_id
        else:
            return None, None

bot_token, chat_id = get_bot_token_and_chat_id()

if not bot_token:
    print("Токен Telegram бота не найден в файле log_pass.txt. Убедитесь, что он находится в третьей строке.")
    exit()

# Инициализация бота
bot = telebot.TeleBot(bot_token)

# Функция для отправки сообщения о времени работы парсера
def send_parser_runtime(message):
    try:
        bot.send_message(chat_id, message)
    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения: {e}")

# Функция для запуска парсера
def start_parser(message):
    global parser_thread

    if parser_thread and parser_thread.is_alive():
        bot.send_message(message.chat.id, "Парсер уже запущен.")
    else:
        bot.send_message(message.chat.id, "Запущен парсер...")
        parser_thread = Thread(target=my_parser.run_parser)
        parser_thread.start()

# Функция для остановки парсера
def stop_parser(driver):
    global parser_thread
    
    if parser_thread and parser_thread.is_alive():
        parser_thread.join()
        bot.send_message(chat_id, "Парсер остановлен в функции stop_parser tg_bot.py.")
    else:
        bot.send_message(chat_id, "Парсер не был запущен tg_bot.py.")

class MyHandler(FileSystemEventHandler):
    def __init__(self, *args, **kwargs):
        super(MyHandler, self).__init__(*args, **kwargs)
        self.last_position = 0

    def on_modified(self, event):
        if event.src_path.endswith('parser.log'):
            with open(event.src_path, 'r', encoding='utf-8') as file:
                file.seek(self.last_position)
                lines = file.readlines()
                self.last_position = file.tell()
                for line in lines:
                    if "Найден проверяющий для проекта" in line:
                        send_parser_runtime("Найден проверяющий для проекта")

# Создание кнопок для запуска и остановки парсера
keyboard = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
btn_start_parser = types.KeyboardButton("/start_parser")
btn_stop_parser = types.KeyboardButton("/stop_parser")
keyboard.add(btn_start_parser, btn_stop_parser)

# Обработка команды /start
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, "Привет! Я бот для управления парсером. Для запуска парсера, используй команду /start_parser.", reply_markup=keyboard)

# Обработчик команды /start_parser для запуска парсера
@bot.message_handler(commands=['start_parser'])
def start_parser_command(message):
    bot.send_message(message.chat.id, "Нажата кнопка запуска парсера из tg_bot")
    start_parser(message)
    bot.send_message(message.chat.id, "Парсер запущен из tg_bot")

# Обработчик команды `/stop_parser` для остановки парсера
@bot.message_handler(commands=['stop_parser'])
def stop_parser_command(message):
    bot.send_message(message.chat.id, "Нажата кнопка останова парсера из tg_bot")
    my_parser.driver.quit()
    bot.send_message(message.chat.id, "Отключен driver")

# Функция для запуска бота в отдельном потоке
def run_bot_thread():
    try:
        logging.info("Запуск ТГ бота в файле tg_bot")
        bot.polling(none_stop=True)
    except Exception as e:
        logging.error(f"Произошла ошибка при запуске бота: {e}")

# Запуск бота и наблюдателя в отдельных потоках
if __name__ == "__main__":
    event_handler = MyHandler()

    bot_thread = Thread(target=run_bot_thread)
    bot_thread.start()
    
    observer = Observer()
    observer.schedule(event_handler, path='parser.log', recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
