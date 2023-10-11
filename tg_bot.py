import os
import re
import csv
import logging
import time
import telebot
from bs4 import BeautifulSoup
import requests
from telebot import types
import pandas as pd

# Инициализация бота с токеном из файла log_pass.txt (токен в третьей строке)
with open('log_pass.txt', 'r') as login_pass_file:
    lines = login_pass_file.readlines()
    if len(lines) >= 3:
        bot_token = lines[2].strip()
        bot = telebot.TeleBot(bot_token)
    else:
        print("Токен Telegram бота не найден в файле log_pass.txt. Убедитесь, что он находится в третьей строке.")
        exit()

# Настройки логирования
logging.basicConfig(filename='parser.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger = logging.getLogger()
logger.addHandler(console_handler)

# Состояния бота
START, GET_LOGIN, GET_PASSWORD, GET_START_TIME, GET_END_TIME, GET_PROJECT, CONFIRMATION = range(7)

# Глобальные переменные для хранения данных
user_data = {"start_time": None, "end_time": None, "project_name": None, "login": None, "password": None}

# Функция, которая начинает диалог и запрашивает логин
@bot.message_handler(commands=['start'])
def start(message):
    user_data.clear()
    bot.send_message(message.chat.id, "Давайте начнем. Введите логин в формате login@student.21-school.ru:")
    bot.register_next_step_handler(message, get_login)

# Функция, которая получает логин и запрашивает пароль
def get_login(message):
    login = message.text
    user_data["login"] = login
    bot.send_message(message.chat.id, "Введите пароль:")
    bot.register_next_step_handler(message, get_password)

# Функция, которая получает пароль и запрашивает начальное время
def get_password(message):
    password = message.text
    user_data["password"] = password
    bot.send_message(message.chat.id, "Введите время начала (например, 09:00):")
    bot.register_next_step_handler(message, get_start_time)

# Функция, которая получает начальное время и запрашивает конечное время
def get_start_time(message):
    start_time = message.text
    user_data["start_time"] = start_time
    bot.send_message(message.chat.id, "Введите время окончания (например, 17:00):")
    bot.register_next_step_handler(message, get_end_time)

# Функция, которая получает конечное время и запрашивает название проекта
def get_end_time(message):
    end_time = message.text
    user_data["end_time"] = end_time
    bot.send_message(message.chat.id, "Введите название проекта:")
    bot.register_next_step_handler(message, get_project)

def get_project(message):
    project_name = message.text
    user_data["project_name"] = project_name

    # Загрузка данных из файла clear.csv
    data = pd.read_csv('clear.csv', header=None)

    # Проверка наличия названия проекта в первом столбце файла
    if project_name in data.iloc[:, 0].values:
        user_data["project_found"] = True  # Добавим признак того, что проект найден
        bot.send_message(message.chat.id, f"Проект '{project_name}' найден. Пожалуйста, подтвердите данные (/confirm) или отмените (/cancel):")
    else:
        user_data["project_found"] = False  # Добавим признак того, что проект не найден
        bot.send_message(message.chat.id, f"Проект '{project_name}' не найден. Пожалуйста, проверьте название проекта и повторите ввод.")

# Функция, которая подтверждает данные и выполняет парсинг
@bot.message_handler(commands=['confirm'])
def confirmation(message):
    if user_data.get("project_found", False):
        # Проект найден, выполните соответствующую логику
        # Например, продолжите с парсингом
        bot.send_message(message.chat.id, "Проект найден. Выполняется парсинг...")

        # Ваши действия при нахождении проекта

    else:
        # Проект не найден, сообщите об этом
        bot.send_message(message.chat.id, "Проект не найден. Операция отменена.")

    # Очистите данные пользователя после завершения
    user_data.clear()

# Функция для обратной связи
@bot.message_handler(func=lambda message: True)
def feedback(message):
    project_name = user_data.get("project_name", "не указан")
    start_time = user_data.get("start_time", "не указано")
    end_time = user_data.get("end_time", "не указано")

    # Здесь вы можете добавить код для отправки сообщения с обратной связью вам
    # Сообщение может содержать имя пользователя, время и текст сообщения
    user_name = message.from_user.first_name
    user_message = message.text

    feedback_message = f"Получена обратная связь от пользователя {user_name}:\n"
    feedback_message += f"Время: {start_time} - {end_time}\n"
    feedback_message += f"Проект: {project_name}\n"
    feedback_message += f"Сообщение: {user_message}"

    # Отправить сообщение с обратной связью на ваш аккаунт или почту
    # Здесь вы можете использовать какой-либо метод доставки сообщений

    bot.send_message(message.chat.id, "Спасибо за ваше сообщение! Мы свяжемся с вами в ближайшее время.")

# Функция для отмены разговора
@bot.message_handler(commands=['cancel'])
def cancel(message):
    bot.send_message(message.chat.id, "Действие отменено.")

# Запуск бота
bot.polling(none_stop=True)
