import os
from pathlib import Path

# Получаем абсолютный путь к текущему файлу (config.py)
current_dir = Path(__file__).resolve().parent # Корень проекта

class Config:
    SECRET_KEY = 'secret'

    BASE_DIR = current_dir

    # Пути для Flask
    STATIC_DIR = BASE_DIR / 'app' / 'static'
    TEMPLATE_DIR = BASE_DIR / 'app' / 'templates'

    # Путь для загрузки изображений
    UPLOAD_FOLDER = 'static/images'

    # Пути к контенту
    CONTENT_DIR = BASE_DIR / 'app' / 'content'
    ACUTE_CASES_FOLDER = CONTENT_DIR / 'acute_cases'
    CATEGORY_FOLDER = CONTENT_DIR / 'categories'
    REFERENCE_FOLDER = CONTENT_DIR / 'reference'

    # Настройки FlatPages
    FLATPAGES_ROOT = str(CONTENT_DIR)
    FLATPAGES_EXTENSION = '.md'
    FLATPAGES_MARKDOWN_EXTENSIONS = ['fenced_code', 'tables']

    @staticmethod
    def init_app(app):
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
