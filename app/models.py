import yaml
import markdown
import os
from flask import current_app
from app import pages
import logging

# Настройка логгирования
logger = logging.getLogger(__name__)

CATEGORIES = [
    {
        'name': 'Препараты',
        'slug': 'general',
        'subtypes': ['types', 'miasms']  # Добавляем подтипы
    },
    {
        'name': 'Острые случаи',
        'slug': 'acute_cases',
    },
    {
        'name': 'Категории',
        'slug': 'categories',
    },
    {
        'name': 'Справочные материалы',
        'slug': 'reference',
    }
]


def get_cards_by_category(category_slug):
    cards = []
    for p in pages:
        try:
            # Добавляем проверку на существование meta и обработку ошибок
            if hasattr(p, 'meta'):
                meta = p.meta
                if (meta.get('category') == category_slug or
                        meta.get('type') == category_slug):
                    cards.append(p)
        except Exception as e:
            logger.error(f"Error processing page {p.path}: {str(e)}")
            continue

    return sorted(cards, key=lambda p: p.meta['title'])


import re
import yaml
import markdown
import logging
from flask import current_app


def load_acute_cases():
    acute_cases = []
    folder = current_app.config['ACUTE_CASES_FOLDER']
    logger = logging.getLogger(__name__)

    for filename in os.listdir(folder):
        if filename.endswith('.md'):
            filepath = os.path.join(folder, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                    match = re.split(r'^---\s*$', content, flags=re.MULTILINE)

                    if len(match) < 3:
                        logger.warning(f"File {filename} has incorrect format, skipping")
                        continue

                    # Первый элемент - пустой, второй - метаданные, третий - контент
                    meta_part = match[1].strip()
                    content_part = match[2].strip()

                    # Безопасный парсинг YAML
                    try:
                        meta = yaml.safe_load(meta_part) or {}
                    except yaml.YAMLError as e:
                        logger.error(f"YAML error in {filename}: {str(e)}")
                        meta = {}

                    # Обработка источников
                    sources = meta.get('sources', [])

                    # Если источники заданы как список строк, преобразуем в словари
                    if sources and isinstance(sources, list) and isinstance(sources[0], str):
                        sources = [{'text': s, 'url': s} for s in sources]

                    # Конвертация Markdown в HTML
                    html_content = markdown.markdown(
                        content_part,
                        extensions=['extra', 'tables', 'fenced_code']
                    )

                    case = {
                        'name': meta.get('name', filename.replace('.md', '')),
                        'slug': meta.get('slug', filename.replace('.md', '')),
                        'image': meta.get('image', ''),
                        'sources': sources,
                        'content': html_content
                    }
                    acute_cases.append(case)

            except Exception as e:
                logger.error(f"Error loading acute case {filename}: {str(e)}")
                continue

    return acute_cases


def load_category():
    categories = {
        'types': [],
        'miasms': []
    }

    folder = current_app.config['CATEGORY_FOLDER']
    md = markdown.Markdown(extensions=['extra', 'nl2br', 'tables'])

    for filename in os.listdir(folder):
        if filename.endswith('.md'):
            filepath = os.path.join(folder, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    parts = content.split('---\n')

                    if len(parts) < 3:
                        logger.warning(f"File {filename} has incorrect format, skipping")
                        continue

                    meta_part, content_part = parts[1], parts[2]

                    try:
                        meta = yaml.safe_load(meta_part) or {}
                    except yaml.YAMLError as e:
                        logger.error(f"YAML error in {filename}: {str(e)}")
                        meta = {}

                    item = {
                        'name': meta.get('title', filename.replace('.md', '')),
                        'title': meta.get('title', filename.replace('.md', '')),
                        'slug': meta.get('slug', filename.replace('.md', '')),
                        'category': meta.get('category', ''),
                        'image': meta.get('image', ''),
                        'html': md.convert(content_part),
                        'meta': meta
                    }

                    if item['category'] == 'type':
                        categories['types'].append(item)
                    elif item['category'] == 'miasm':
                        categories['miasms'].append(item)

            except Exception as e:
                logger.error(f"Error loading category {filename}: {str(e)}")
                continue

    return categories


def load_glossary_terms():
    glossary = {}
    sorted_glossary = {}
    glossary_folder = 'app/content/glossary'
    os.makedirs(glossary_folder, exist_ok=True)

    for filename in os.listdir(glossary_folder):
        if filename.endswith('.md'):
            filepath = os.path.join(glossary_folder, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    parts = content.split('---\n')

                    if len(parts) < 3:
                        continue

                    meta_part, content_part = parts[1], parts[2]

                    try:
                        meta = yaml.safe_load(meta_part) or {}
                    except yaml.YAMLError:
                        meta = {}

                    term = meta.get('term', filename.replace('.md', ''))
                    glossary[term] = {
                        'term': term,
                        'content': markdown.markdown(content_part),
                        'slug': filename.replace('.md', '')
                    }

            except Exception as e:
                logger.error(f"Error loading glossary term {filename}: {str(e)}")
                continue

        # Сортируем словарь по ключу (term) и создаем новый OrderedDict
        sorted_glossary = dict(sorted(glossary.items(), key=lambda item: item[0].lower()))

    return sorted_glossary


def load_reference_materials():
    materials = []
    folder = current_app.config['REFERENCE_FOLDER']
    md = markdown.Markdown(extensions=['extra', 'nl2br', 'tables'])

    for filename in os.listdir(folder):
        if filename.endswith('.md'):
            filepath = os.path.join(folder, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    parts = content.split('---\n')

                    if len(parts) < 3:
                        logger.warning(f"File {filename} has incorrect format, skipping")
                        continue

                    meta_part, content_part = parts[1], parts[2]

                    try:
                        meta = yaml.safe_load(meta_part) or {}
                    except yaml.YAMLError as e:
                        logger.error(f"YAML error in {filename}: {str(e)}")
                        meta = {}

                    material = {
                        'title': meta.get('title', filename.replace('.md', '')),
                        'slug': meta.get('slug', filename.replace('.md', '')),
                        'image': meta.get('image', ''),
                        'html': md.convert(content_part),
                        'meta': meta
                    }
                    materials.append(material)

            except Exception as e:
                logger.error(f"Error loading reference material {filename}: {str(e)}")
                continue

    return sorted(materials, key=lambda x: x['title'])
