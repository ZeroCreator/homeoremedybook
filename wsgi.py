from app import app  # Импортируем экземпляр Flask
import os
import logging

# Критически важная строка для Vercel!
# Создаем переменную app на верхнем уровне
application = app

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Диагностика
logger.info(f"Current directory: {os.getcwd()}")
logger.info(f"Files in root: {os.listdir('.')}")

if os.path.exists('app'):
    logger.info(f"Files in app: {os.listdir('app')}")
else:
    logger.error("Directory 'app' does not exist!")

# Для локального запуска
if __name__ == "__main__":
    app.run(port=5000, debug=True)
