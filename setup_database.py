import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base, User, Courier, Auth  # Импортируем все модели

# Настройте соединение с вашей базой данных
DATABASE_URL = "sqlite:///./test.db"  # Замените на ваш URL базы данных
print(f"Creating database at: {os.path.abspath('test.db')}")

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)  # Создание всех таблиц 
print("Database tables created successfully") 