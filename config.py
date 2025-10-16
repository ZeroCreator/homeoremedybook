import os
from pathlib import Path

class Config:
    SECRET_KEY = 'secret'

    # Получаем абсолютный путь к текущему файлу (config.py)
    BASE_DIR = Path(__file__).resolve().parent  # Корень проекта

    # Пути для Flask
    STATIC_DIR = BASE_DIR / 'public' / 'static'
    TEMPLATE_DIR = BASE_DIR / 'app' / 'templates'

    # Пути к контенту
    CONTENT_DIR = BASE_DIR / 'app' / 'content'
    ACUTE_CASES_FOLDER = CONTENT_DIR / 'acute_cases'
    CATEGORY_FOLDER = CONTENT_DIR / 'categories'
    REFERENCE_FOLDER = CONTENT_DIR / 'reference'

    # Настройки FlatPages
    FLATPAGES_ROOT = str(CONTENT_DIR)
    FLATPAGES_EXTENSION = '.md'
    FLATPAGES_MARKDOWN_EXTENSIONS = ['fenced_code', 'tables']

    # Путь для загрузки изображений
    UPLOAD_FOLDER = STATIC_DIR / 'images'
