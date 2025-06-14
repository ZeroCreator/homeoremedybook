from collections import defaultdict
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
        'color': '#d1d9d0',
        'subtypes': ['types', 'miasms']  # Добавляем подтипы
    },
    {
        'name': 'Острые случаи',
        'slug': 'acute_cases',
        'color': '#8c9e7e'
    },
    {
        'name': 'Категории',
        'slug': 'categories',
        'color': '#8c9e7e'
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


def load_acute_cases():
    acute_cases = []
    folder = current_app.config['ACUTE_CASES_FOLDER']

    for filename in os.listdir(folder):
        if filename.endswith('.md'):
            filepath = os.path.join(folder, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                    # Более надежное разделение на метаданные и контент
                    parts = content.split('---\n')
                    if len(parts) < 3:
                        logger.warning(f"File {filename} has incorrect format, skipping")
                        continue

                    meta_part, content_part = parts[1], parts[2]

                    # Безопасный парсинг YAML
                    try:
                        meta = yaml.safe_load(meta_part) or {}
                    except yaml.YAMLError as e:
                        logger.error(f"YAML error in {filename}: {str(e)}")
                        meta = {}

                    case = {
                        'name': meta.get('name', filename.replace('.md', '')),
                        'slug': meta.get('slug', filename.replace('.md', '')),
                        'image': meta.get('image', ''),
                        'content': markdown.markdown(content_part)
                    }
                    acute_cases.append(case)

            except Exception as e:
                logger.error(f"Error loading acute case {filename}: {str(e)}")
                continue

    return acute_cases


# models.py (updated parts)
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

    return glossary
