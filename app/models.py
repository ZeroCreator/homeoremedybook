from collections import defaultdict
import markdown
import os
from flask import current_app
from app import pages


CATEGORIES = [
    {'name': 'Общие препараты', 'slug': 'general', 'is_acute': False, 'color': '#d1d9d0'},
    {'name': 'Острые случаи', 'slug': 'acute_cases', 'is_acute': True, 'color': '#8c9e7e'}
]


def load_acute_cases():
    acute_cases = []
    folder = current_app.config['ACUTE_CASES_FOLDER']
    for filename in os.listdir(folder):
        if filename.endswith('.md'):
            with open(os.path.join(folder, filename), 'r', encoding='utf-8') as f:
                content = f.read()
                meta_part, content_part = content.split('---\n', 2)[1:]
                meta = {}
                for line in meta_part.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        meta[key.strip()] = value.strip()

                case = {
                    'name': meta.get('name', 'Без названия'),
                    'slug': meta.get('slug', filename.replace('.md', '')),
                    'image': meta.get('image', ''),
                    'content': markdown.markdown(content_part)
                }
                acute_cases.append(case)
    return acute_cases


def get_cards_by_category(category_slug):
    return sorted(
        [p for p in pages if p.meta.get('category') == category_slug],
        key=lambda p: p.meta['title']
    )


def get_cards_by_miasm():
    miasms = defaultdict(list)
    for page in pages:
        if 'miasm' in page.meta:
            miasms[page.meta['miasm']].append(page)
    return miasms


def get_cards_by_kingdom():
    kingdoms = defaultdict(list)
    for page in pages:
        if 'kingdom' in page.meta:
            kingdoms[page.meta['kingdom']].append(page)
    return kingdoms


def load_glossary_terms():
    glossary = {}
    glossary_folder = 'app/content/glossary'
    os.makedirs(glossary_folder, exist_ok=True)

    for filename in os.listdir(glossary_folder):
        if filename.endswith('.md'):
            with open(os.path.join(glossary_folder, filename), 'r', encoding='utf-8') as f:
                content = f.read()
                parts = content.split('---\n')
                if len(parts) >= 3:
                    meta_part = parts[1]
                    content_part = parts[2]
                    meta = {}
                    for line in meta_part.split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            meta[key.strip()] = value.strip()

                    term = meta.get('term', filename.replace('.md', ''))
                    glossary[term] = {
                        'term': term,
                        'content': markdown.markdown(content_part),
                        'slug': filename.replace('.md', '')
                    }
    return glossary
