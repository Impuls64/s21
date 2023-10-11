#!/bin/bash

# Определите необходимую версию ChromeDriver
required_chrome_version="114.0.5735.90"

# Проверяем, установлен ли Google Chrome
if google-chrome-stable --version &> /dev/null; then
  echo "Удаление Google Chrome..."
  sudo apt remove --purge google-chrome-stable -y
fi

# Убеждаемся, что система обновлена
sudo apt update

# Скачиваем и устанавливаем версию Google Chrome совместимую с ChromeDriver
echo "Установка совместимой версии Google Chrome..."
wget https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${required_chrome_version}-1_amd64.deb
sudo apt -y install ./google-chrome-stable_${required_chrome_version}-1_amd64.deb

# Проверяем, установлен ли ChromeDriver и совместим ли он
installed_chromedriver_version=$(chromedriver --version | awk '{print $2}' | cut -d. -f1,2)
if [ "$installed_chromedriver_version" != "$required_chrome_version" ]; then
  echo "Обновление ChromeDriver до версии $required_chrome_version..."
  
  # Удаляем существующий Chromedriver
  sudo rm -f /usr/local/bin/chromedriver

  # Загружаем и устанавливаем необходимый ChromeDriver
  chromedriver_download_url="https://chromedriver.storage.googleapis.com/${required_chrome_version}/chromedriver_linux64.zip"
  wget "$chromedriver_download_url"
  unzip chromedriver_linux64.zip
  chmod +x chromedriver
  sudo mv chromedriver /usr/local/bin/
  
  # Удаляем загруженные файлы
  rm -f chromedriver_linux64.zip
fi

exit $exit_code
