from src.database import engine, Base
from src.models import user, courier, warehouse, auth

def init_db():
    Base.metadata.create_all(bind=engine)
    print("База данных инициализирована")

if __name__ == "__main__":
    init_db() 