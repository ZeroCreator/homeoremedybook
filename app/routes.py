from flask import render_template, request, send_from_directory
from app import app, pages
from app.models import (
    CATEGORIES,
    load_acute_cases,
    get_cards_by_category,
    get_cards_by_miasm,
    get_cards_by_kingdom,
    load_glossary_terms
)

from flask import current_app
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

@app.route('/glossary')
def glossary():
    terms = load_glossary_terms()
    return render_template('glossary.html',
                         terms=terms,
                         menu_color=CATEGORIES[0]['color'])


@app.route('/static/images/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
