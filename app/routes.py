from flask import render_template, request, send_from_directory
from app import app, pages
from app.models import (
    CATEGORIES,
    load_acute_cases,
    get_cards_by_category,
    load_category,
    load_glossary_terms,
    load_reference_materials,
)


@app.route('/')
def index():
    keyword_filter = request.args.get('keywords', '').lower()
    miasm_filter = request.args.get('miasm', '')
    group_filter = request.args.get('group', '')

    # Получаем все карточки
    all_cards = get_cards_by_category('general')

    # Применяем фильтры
    filtered_cards = []
    for card in all_cards:
        match = True

        # Фильтр по ключевым словам
        if keyword_filter:
            search_fields = [
                card.meta.get('title', ''),
                card.meta.get('cirillic', ''),
                card.meta.get('base_description', ''),
                ' '.join(card.meta['description']) if isinstance(card.meta.get('description'), list) else card.meta.get(
                    'description', ''),
                ' '.join(card.meta['symptoms']) if isinstance(card.meta.get('symptoms'), list) else card.meta.get(
                    'symptoms', ''),
                card.meta.get('modalities', ''),
                ' '.join(card.meta['keywords']) if isinstance(card.meta.get('keywords'), list) else card.meta.get(
                    'keywords', ''),
                card.meta.get('personality', ''),
                card.html
            ]

            keyword_match = any(
                keyword_filter in str(field).lower()
                for field in search_fields
                if field
            )

            if not keyword_match:
                match = False

        # Фильтр по миазму (поддержка составных миазмов)
        if miasm_filter:
            card_miasms = card.meta.get('miasm', '')
            if isinstance(card_miasms, str):
                card_miasms = [m.strip() for m in card_miasms.split(',')]
            elif not isinstance(card_miasms, list):
                card_miasms = []

            if not any(miasm_filter == m for m in card_miasms):
                match = False

        # Фильтр по группе
        if group_filter:
            card_group = card.meta.get('group', '')
            if not card_group or card_group != group_filter:
                match = False

        if match:
            filtered_cards.append(card)

    # Получаем уникальные значения для фильтров
    miasms = set()
    groups = set()

    for card in all_cards:
        if card.meta.get('miasm'):
            if isinstance(card.meta['miasm'], str):
                for m in card.meta['miasm'].split(','):
                    miasms.add(m.strip())
            elif isinstance(card.meta['miasm'], list):
                miasms.update(m.strip() for m in card.meta['miasm'])

        if card.meta.get('group'):
            groups.add(card.meta['group'])

    # Сортируем списки фильтров
    miasms = sorted(miasms)
    groups = sorted(groups)

    return render_template('index.html',
                           cards=filtered_cards if any([keyword_filter, miasm_filter, group_filter]) else all_cards,
                           all_cards=all_cards,
                           miasms=miasms,
                           groups=groups,
                           keyword_filter=request.args.get('keywords', ''))


@app.route('/card/<path:slug>')
def card_detail(slug):
    card = next((p for p in pages if p.meta.get('slug') == slug), None)
    if not card:
        return "Card not found", 404

    return render_template(
        'card_detail.html',
        card=card,
        categories=CATEGORIES
    )

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


@app.route('/category')
def category():
    categories = load_category()
    return render_template(
        'category.html',
        types=categories['types'],
        miasms=categories['miasms'],
        menu_color=CATEGORIES[2]['color']
    )


@app.route('/category/<slug>')
def category_detail(slug):
    categories = load_category()
    # Ищем в обоих подкатегориях
    all_items = categories['types'] + categories['miasms']
    item = next((item for item in all_items if item['slug'] == slug), None)

    if not item:
        return "Item not found", 404

    return render_template(
        'category_detail.html',
        category=item,
        menu_color=CATEGORIES[2]['color']
    )


@app.route('/reference')
def reference():
    materials = load_reference_materials()
    return render_template(
        'reference.html',
        materials=materials,
        menu_color=CATEGORIES[3]['color']
    )


@app.route('/reference/<slug>')
def reference_detail(slug):
    materials = load_reference_materials()
    material = next((m for m in materials if m['slug'] == slug), None)

    if not material:
        return "Material not found", 404

    return render_template(
        'reference_detail.html',
        material=material,
        menu_color=CATEGORIES[3]['color']
    )


@app.route('/glossary')
def glossary():
    terms = load_glossary_terms()
    return render_template(
        'glossary.html',
        terms=terms,
        menu_color=CATEGORIES[0]['color']
    )


@app.route('/static/images/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
