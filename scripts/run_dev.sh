#!/bin/bash

# Инициализация базы данных
echo "Инициализация базы данных..."
python -m scripts.init_db

# Создание тестовых пользователей
echo "Создание тестовых пользователей..."
python -m scripts.create_test_users

# Запуск приложения
echo "Запуск приложения..."
python src/run.py 