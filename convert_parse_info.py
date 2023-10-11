import csv
import re

# Открываем файл output.csv для чтения
with open('output.csv', mode='r', newline='', encoding='utf-8') as csv_file:
    csv_reader = csv.reader(csv_file)
    next(csv_reader)  # Пропускаем заголовок

    # Создаем файл clear.csv для записи данных в новом формате
    with open('clear.csv', mode='w', newline='', encoding='utf-8') as clear_csv_file:
        csv_writer = csv.writer(clear_csv_file)
        for row in csv_reader:
            url, title = row
            # Извлекаем номер из URL
            url_parts = url.split('/')
            number = url_parts[-1]

            # Извлекаем данные в скобках с помощью регулярного выражения
            match = re.search(r'"(.+)"', title)
            if match:
                data_in_parentheses = match.group(1)
            else:
                data_in_parentheses = ''

            # Записываем данные в новом формате в clear.csv
            csv_writer.writerow([number, data_in_parentheses])

print('Конвертация завершена. Данные сохранены в clear.csv.')
