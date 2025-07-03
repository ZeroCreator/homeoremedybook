import yaml
import markdown
import os
import re
import logging
from flask import current_app
from app import pages

logger = logging.getLogger(__name__)

# Глобальный список категорий приложения. Определяет основные разделы сайта с их свойствами.
CATEGORIES = [
    {'name': 'Препараты', 'slug': 'general', 'subtypes': ['types', 'miasms']},
    {'name': 'Острые случаи', 'slug': 'acute_cases'},
    {'name': 'Категории', 'slug': 'categories'},
    {'name': 'Справочные материалы', 'slug': 'reference'}
]


def get_cards_by_category(category_slug):
    """Возвращает отсортированные карточки препаратов для указанной категории.
    - Фильтрует страницы по полям category или type в метаданных
    - Обрабатывает ошибки парсинга
    - Сортировка по заголовку с защитой от None
    """
    cards = []
    for p in pages:
        try:
            if hasattr(p, 'meta'):
                meta = p.meta
                if meta.get('category') == category_slug or meta.get('type') == category_slug:
                    cards.append(p)
        except Exception as e:
            logger.error(f"Error processing page {p.path}: {str(e)}")
    # Исправлено: безопасная сортировка с обработкой None
    return sorted(cards, key=lambda p: p.meta.get('title', '') or '')


def parse_md_file(filepath):
    """Парсит Markdown-файл, разделяя фронтматер и контент.
    - Поддерживает два формата разделителей (--- и ---\n)
    - Возвращает очищенные части метаданных и контента
    - Логирует ошибки чтения и невалидные форматы
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        parts = re.split(r'^---\s*$', content, flags=re.MULTILINE)
        if len(parts) < 3:
            # Альтернативный вариант разделителя
            parts = content.split('---\n')
            if len(parts) < 3:
                logger.warning(f"File {os.path.basename(filepath)} has incorrect format")
                return None, None

        return parts[1].strip(), parts[2].strip()
    except Exception as e:
        logger.error(f"Error reading file {filepath}: {str(e)}")
        return None, None


def load_md_files(folder, process_func):
    """Универсальный загрузчик Markdown-файлов из указанной папки.
    - Проверяет существование и тип папки
    - Фильтрует только .md файлы
    - Обрабатывает каждый файл через parse_md_file()
    - Применяет переданную функцию обработки (process_func)
    - Возвращает список обработанных объектов
    """
    items = []
    if not os.path.exists(folder):
        logger.error(f"Folder does not exist: {folder}")
        return items
    if not os.path.isdir(folder):
        logger.error(f"Path is not a directory: {folder}")
        return items

    for filename in os.listdir(folder):
        if not filename.endswith('.md'):
            continue

        filepath = os.path.join(folder, filename)
        if not os.path.isfile(filepath):
            continue

        meta_part, content_part = parse_md_file(filepath)
        if meta_part is None or content_part is None:
            continue

        try:
            meta = yaml.safe_load(meta_part) or {}
            item = process_func(meta, content_part, filename)
            if item:
                items.append(item)
        except Exception as e:
            logger.error(f"Error processing file {filename}: {str(e)}")
            continue

    return items


def process_acute_case(meta, content, filename):
    """Форматирует данные острого случая.
    - Обрабатывает источники (конвертирует строки в словари)
    - Генерирует slug из имени файла при отсутствии
    - Конвертирует Markdown-контент в HTML
    - Возвращает структурированный объект случая
    """
    basename = os.path.splitext(filename)[0]
    sources = meta.get('sources', [])
    if sources and isinstance(sources, list) and sources and isinstance(sources[0], str):
        sources = [{'text': s, 'url': s} for s in sources]

    return {
        'name': meta.get('name') or basename,
        'slug': meta.get('slug') or basename,
        'image': meta.get('image', ''),
        'sources': sources,
        'content': markdown.markdown(content, extensions=['extra', 'tables', 'fenced_code'])
    }


def process_category(meta, content, filename):
    """Форматирует данные категорий (типы/миазмы).
    - Инициализирует парсер Markdown с расширениями
    - Извлекает основное изображение
    - Определяет тип категории (type/miasm)
    - Возвращает объект с HTML-контентом
    """
    basename = os.path.splitext(filename)[0]
    md = markdown.Markdown(extensions=['extra', 'nl2br', 'tables'])
    return {
        'name': meta.get('title') or basename,
        'title': meta.get('title') or '',
        'slug': meta.get('slug') or basename,
        'category': meta.get('category', ''),
        'image': meta.get('image', ''),
        'html': md.convert(content),
        'meta': meta
    }


def process_glossary(meta, content, filename):
    """Форматирует термины глоссария.
    - Извлекает термин из метаданных или имени файла
    - Генерирует slug из имени файла
    - Конвертирует описание в HTML
    - Возвращает объект термина
    """
    basename = os.path.splitext(filename)[0]
    term = meta.get('term') or basename
    return {
        'term': term,
        'content': markdown.markdown(content),
        'slug': basename
    }


def process_reference(meta, content, filename):
    """process_reference(meta, content, filename)
    - Форматирует справочные материалы.
    - Использует Markdown-парсер с расширениями
    - Обеспечивает fallback для заголовка и slug
    - Возвращает объект материала с HTML-контентом
    """
    basename = os.path.splitext(filename)[0]
    md = markdown.Markdown(extensions=['extra', 'nl2br', 'tables'])
    return {
        'title': meta.get('title') or basename,
        'slug': meta.get('slug') or basename,
        'image': meta.get('image', ''),
        'html': md.convert(content),
        'meta': meta
    }


def load_acute_cases():
    """Загружает все острые случаи из настроенной папки.
    - Использует load_md_files() с процессором process_acute_case
    - Возвращает список готовых к отображению случаев
    """
    folder = current_app.config['ACUTE_CASES_FOLDER']
    return load_md_files(folder, process_acute_case)


def load_category():
    """Загружает и классифицирует категории.
    - Разделяет загруженные элементы на типы и миазмы
    - Возвращает словарь с двумя списками: types и miasms
    """
    folder = current_app.config['CATEGORY_FOLDER']
    items = load_md_files(folder, process_category)

    categories = {'types': [], 'miasms': []}
    for item in items:
        category_type = item.get('category', '')
        if category_type == 'type':
            categories['types'].append(item)
        elif category_type == 'miasm':
            categories['miasms'].append(item)
    return categories


def load_glossary_terms():
    """Загружает и сортирует термины глоссария.
    - Создает папку при отсутствии
    - Собирает термины в словарь
    - Сортирует по термину без учета регистра
    - Возвращает отсортированный словарь
    """
    glossary_folder = current_app.config.get('GLOSSARY_FOLDER', 'app/content/glossary')
    os.makedirs(glossary_folder, exist_ok=True)
    items = load_md_files(glossary_folder, process_glossary)

    # Создаем словарь: ключ - термин, значение - данные
    glossary_dict = {}
    for item in items:
        glossary_dict[item['term']] = item

    # Безопасная сортировка
    return dict(sorted(glossary_dict.items(), key=lambda item: (item[0] or '').lower()))


def load_reference_materials():
    """Загружает справочные материалы.
    - Использует load_md_files() с процессором process_reference
    - Сортирует по заголовку с защитой от None
    - Возвращает отсортированный список
    """
    folder = current_app.config['REFERENCE_FOLDER']
    items = load_md_files(folder, process_reference)
    # Безопасная сортировка с обработкой None
    return sorted(items, key=lambda x: (x.get('title') or '').lower())
