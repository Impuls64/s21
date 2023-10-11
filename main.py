import os
import csv
import logging
import connector
import my_parser
#import tg_bot

# Настроим логирование
logging.basicConfig(filename='parser.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger = logging.getLogger()
logger.addHandler(console_handler)

def show_menu():
    print("\nВыберите действие:")
    print("0. Выход")
    print("1. Запуск Telegram бота")
    print("2. Запуск парсинга")
    print("3. Просмотр/очистка log файла")
    print("4. Ввод/изменение логинов и паролей")
    print("5. Установка зависимостей")

def main_menu():
    while True:
        #os.system('clear')
        show_menu()
        choice = input("Введите номер действия: ")

        if choice == '0':
            print("Выход из программы.")
            break

        #elif choice == '1':
            # Запуск Telegram бота
            #tg_bot.bot.polling(none_stop=True)

        elif choice == '2':
            driver = connector.initialize_driver()
            with open('log_pass.txt', 'r') as login_pass_file:
                lines = login_pass_file.readlines()
                if len(lines) >= 2:
                    login = lines[0].strip()
                    password = lines[1].strip()
                else:
                    print("Файл 'log_pass.txt' должен содержать логин и пароль на двух разных строках.")
                    continue
            login_url = "https://auth.sberclass.ru/auth/realms/EduPowerKeycloak/protocol/openid-connect/auth?client_id=school21&redirect_uri=https%3A%2F%2Fedu.21-school.ru%2F&state=32a4629c-9404-46ca-8729-fb3cae801c1c&response_mode=fragment&response_type=code&scope=openid&nonce=9ca33f99-639f-44a4-8ad3-1b0bad3257f1"
            connector.login(driver, login, password, login_url)
            my_parser.parse_and_save(driver)
            print("Парсинг завершен!")

        elif choice == '3':
            os.system('clear')
            print("Выберите действие:")
            print("1. Просмотр log файла")
            print("2. Очистка log файла")

            log_choice = input("Введите номер действия: ")

            if log_choice == '1':
                # Просмотр log файла
                with open('parser.log', 'r') as log_file:
                    print(log_file.read())
            elif log_choice == '2':
                # Очистка log файла
                open('parser.log', 'w').close()
                print("Log файл очищен.")
            else:
                print("Некорректный выбор.")

        elif choice == '4':
            os.system('clear')
            print("Выберите действие:")
            print("1. Ввод логина и пароля для авторизации на сайте")
            print("2. Ввод логина и пароля для Telegram бота")

            login_choice = input("Введите номер действия: ")

            if login_choice == '1':
                login = input("Введите логин для авторизации на сайте: ")
                password = input("Введите пароль для авторизации на сайте: ")

                # Запись логина и пароля в log_pass.txt
                with open('log_pass.txt', 'w') as log_pass_file:
                    log_pass_file.write(f"{login}\n{password}")

                print("Логин и пароль для сайта успешно сохранены в log_pass.txt")

            elif login_choice == '2':
                bot_token = input("Введите токен Telegram бота: ")

                # Запись токена Telegram бота
                with open('log_pass.txt', 'a') as log_pass_file:
                    log_pass_file.write(f"\n{bot_token}")

                print("Токен Telegram бота успешно сохранен в log_pass.txt")

            else:
                print("Некорректный выбор.")
            
        elif choice == '5':
            # Установка зависимостей и запуск webdriver.sh
            try:
                os.system("pip install -r requirements.txt")
                os.system("./webdriver.sh")
                print("Зависимости установлены и webdriver.sh запущен успешно.")
            except Exception as e:
                print(f"Ошибка при установке зависимостей или запуске webdriver.sh: {str(e)}")

        else:
            print("Некорректный выбор. Пожалуйста, введите номер действия из списка.")

if __name__ == "__main__":
    main_menu()
