import sys
import signal
from pathlib import Path
import socket
import uvicorn

# Добавляем корневую директорию проекта в PYTHONPATH
sys.path.append(str(Path(__file__).parent))

def handle_exit(signum, frame):
    print("\nЗавершение работы сервера...")
    sys.exit(0)

if __name__ == "__main__":
    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    # Получаем локальный IP адрес
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    # Настройки сервера
    HOST = "0.0.0.0"
    PORT = 8000
    
    print(f"\nСервер доступен по адресам:")
    print(f"Локальный доступ: http://localhost:{PORT}")
    print(f"Доступ по сети: http://{local_ip}:{PORT}")
    
    # Запускаем сервер
    config = uvicorn.Config(
        "src.main:app",
        host=HOST,
        port=PORT,
        reload=True,
        reload_includes=['*.py', '*.html', '*.js', '*.css'],
        log_level="info"
    )
    server = uvicorn.Server(config)
    server.run() 