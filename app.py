from flask import Flask, render_template, request, send_from_directory
from flask_flatpages import FlatPages
from collections import defaultdict
import markdown
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret'
app.config['FLATPAGES_ROOT'] = 'content'
app.config['FLATPAGES_EXTENSION'] = '.md'
app.config['FLATPAGES_MARKDOWN_EXTENSIONS'] = ['fenced_code', 'tables']
app.config['ACUTE_CASES_FOLDER'] = 'content/acute_cases'
app.config['UPLOAD_FOLDER'] = 'static/images'

# Создаем папку для изображений, если ее нет
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.template_filter('markdown')
def markdown_filter(text):
    return markdown.markdown(text)

pages = FlatPages(app)

# Категории
CATEGORIES = [
    {'name': 'Общие препараты', 'slug': 'general', 'is_acute': False, 'color': '#d1d9d0'},
    {'name': 'Острые случаи', 'slug': 'acute_cases', 'is_acute': True, 'color': '#8c9e7e'}
]

def load_acute_cases():
    acute_cases = []
    for filename in os.listdir(app.config['ACUTE_CASES_FOLDER']):
        if filename.endswith('.md'):
            with open(os.path.join(app.config['ACUTE_CASES_FOLDER'], filename), 'r', encoding='utf-8') as f:
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
    glossary_folder = 'content/glossary'
    # Create categories if it doesn't exist
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


@app.route('/')
def index():
    keyword = request.args.get('keywords', '').lower()
    general_cards = get_cards_by_category('general')

    if keyword:
        general_cards = [
            p for p in general_cards
            if keyword in (p.meta.get('keywords', '') + p.body).lower()
        ]

    return render_template('index.html',
                         cards=general_cards,
                         keyword_filter=keyword,
                         menu_color=CATEGORIES[0]['color'])

@app.route('/acute_cases')
def acute_cases():
    cases = load_acute_cases()
    return render_template('acute_cases.html',
                         acute_cases=cases,
                         menu_color=CATEGORIES[1]['color'])


@app.route('/acute-case/<slug>')
def acute_case_detail(slug):
    cases = load_acute_cases()
    case = next((c for c in cases if c['slug'] == slug), None)
    if not case:
        return "Case not found", 404

    return render_template('acute_case_detail.html',
                           case=case,
                           menu_color=CATEGORIES[1]['color'])

@app.route('/card/<path:slug>')
def card_detail(slug):
    card = next((p for p in pages if p.meta.get('slug') == slug), None)
    if not card:
        return "Card not found", 404

    return render_template('card_detail.html',
                         card=card,
                         categories=CATEGORIES
                         )

@app.route('/category')
def category():
    miasms = get_cards_by_miasm()
    kingdoms = get_cards_by_kingdom()
    return render_template('category.html',
                         miasms=miasms,
                         kingdoms=kingdoms,
                         menu_color=CATEGORIES[0]['color'])

@app.route('/directory')
def directory():  # Make sure this function name matches
    terms = load_glossary_terms()
    return render_template('glossary.html',
                         terms=terms,
                         menu_color=CATEGORIES[0]['color'])



@app.route('/static/images/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
