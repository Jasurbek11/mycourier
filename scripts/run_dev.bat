@echo off

echo Инициализация базы данных...
python -m scripts.init_db

echo Создание тестовых пользователей...
python -m scripts.create_test_users

echo Запуск приложения...
python run.py 