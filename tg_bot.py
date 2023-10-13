import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import telebot
import my_parser
from threading import Thread
import logging
from telebot import types
import time


# my_parser.py
stop_parsing = False

# Установка обработчика журнала для записи в файл
logging.basicConfig(
    level=logging.INFO,
    filename='parser.log',
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Чтение токена бота из файла log_pass.txt
with open('log_pass.txt', 'r') as login_pass_file:
    lines = login_pass_file.readlines()
    if len(lines) >= 3:
        bot_token = lines[2].strip()
        logging.info("Токен Telegram бота найден")
    else:
        logging.error("Токен Telegram бота не найден в файле log_pass.txt. Убедитесь, что он находится в третьей строке.")
        exit()
chat_id = 1273830101

# Инициализация бота
bot = telebot.TeleBot(bot_token)

# Добавьте глобальную переменную для хранения времени запуска парсера
parser_start_time = None
parser_thread = None

# Функция для отправки сообщения о времени работы парсера
def send_parser_runtime(message):
    try:
        bot.send_message(chat_id, message)
    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения: {e}")

def start_parser(message):
    global parser_start_time
    global parser_thread
    if parser_thread and parser_thread.is_alive():
        bot.send_message(message.chat.id, "Парсер уже запущен.")
    else:
        parser_start_time = time.time()
        my_parser.parser_start_time = parser_start_time  # Передайте время начала парсера
        bot.send_message(message.chat.id, "Запущен парсер...")
        parser_thread = Thread(target=my_parser.run_parser)
        parser_thread.start()

def stop_parser(message):
    global parser_start_time
    global parser_thread
    if parser_thread and parser_thread.is_alive():
        parser_thread.join()
        parser_start_time = None
        bot.send_message(message.chat.id, "Парсер остановлен.")
    else:
        bot.send_message(message.chat.id, "Парсер не был запущен.")

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

# Добавьте обработчики команд /start_parser и /stop_parser
@bot.message_handler(commands=['start_parser'])
def start_parser_command(message):
    start_parser(message)

@bot.message_handler(commands=['stop_parser'])
def stop_parser_command(message):
    stop_parser(message)

# Создание кнопок для запуска и остановки парсера
keyboard = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
btn_start_parser = types.KeyboardButton("/start_parser")
btn_stop_parser = types.KeyboardButton("/stop_parser")
keyboard.add(btn_start_parser, btn_stop_parser)

# Обработка команды /start
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, "Привет! Я бот для управления парсером. Для запуска парсера, используй команду /start_parser.", reply_markup=keyboard)

# Обработка команды /help
@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, "Я бот для управления парсером. Для запуска парсера, используй команду /start_parser.", reply_markup=keyboard)

# Функция для запуска бота в отдельном потоке
def run_bot():
    bot.polling()

# Запуск бота в отдельном потоке
if __name__ == "__main__":
    event_handler = MyHandler()

    bot_thread = Thread(target=run_bot)
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