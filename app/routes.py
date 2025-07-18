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


def get_card_miasms(card):
    """Извлекает миазмы карточки в унифицированном формате.
    - Обрабатывает строковые и списковые форматы
    - Разбивает строки по запятым
    - Всегда возвращает список
    """
    miasms = card.meta.get('miasm', '')
    if isinstance(miasms, str):
        return [m.strip() for m in miasms.split(',')]
    return miasms if isinstance(miasms, list) else []


def matches_keyword(card, keyword):
    """Проверяет совпадение ключевого слова с полями карточки.
    - Анализирует текстовые и списковые поля
    - Ищет вхождения в заголовке, описании, симптомах и др.
    - Возвращает булево значение совпадения
    """
    if not keyword:
        return True

    search_fields = [
        card.meta.get('title', ''),
        card.meta.get('cirillic', ''),
        card.meta.get('base_description', ''),
        card.meta.get('personality', ''),
        card.meta.get('modalities', ''),
        card.html
    ]

    # Обработка списковых полей
    for field in ['description', 'symptoms', 'keywords']:
        value = card.meta.get(field, [])
        if isinstance(value, list):
            search_fields.append(' '.join(value))
        else:
            search_fields.append(str(value))

    return any(keyword in (str(field) or '').lower() for field in search_fields)


@app.route('/')
def index():
    """Главная страница с фильтрацией препаратов.
    - Фильтрует карточки по ключевому слову, миазму и группе
    - Собирает уникальные значения для фильтров
    - Передает данные в шаблон index.html
    """
    keyword_filter = request.args.get('keywords', '').lower()
    miasm_filter = request.args.get('miasm', '')
    group_filter = request.args.get('group', '')

    all_cards = get_cards_by_category('general')

    # Применяем фильтры
    filtered_cards = all_cards

    # Фильтр по ключевым словам
    if keyword_filter:
        filtered_cards = [c for c in filtered_cards if matches_keyword(c, keyword_filter)]

    # Фильтр по миазму
    if miasm_filter:
        filtered_cards = [c for c in filtered_cards if miasm_filter in get_card_miasms(c)]

    # Фильтр по группе
    if group_filter:
        filtered_cards = [c for c in filtered_cards if c.meta.get('group') == group_filter]

    # Сбор уникальных значений для фильтров
    miasms, groups = set(), set()
    for card in all_cards:
        miasms.update(get_card_miasms(card))
        if card.meta.get('group'):
            groups.add(card.meta['group'])

    return render_template(
        'index.html',
        cards=filtered_cards,
        all_cards=all_cards,
        miasms=sorted(miasms),
        groups=sorted(groups),
        keyword_filter=request.args.get('keywords', '')
    )


@app.route('/card/<path:slug>')
def card_detail(slug):
    """Страница детализации препарата.
    - Находит карточку по slug
    - Возвращает 404 при отсутствии
    - Отображает шаблон card_detail.html
    """
    card = next((p for p in pages if p.meta.get('slug') == slug), None)
    if not card:
        return "Card not found", 404
    return render_template('card_detail.html', card=card, categories=CATEGORIES)


@app.route('/acute_cases')
def acute_cases():
    """Страница списка острых случаев.
    - Загружает все острые случаи
    - Отображает шаблон acute_cases.html
    """
    return render_template('acute_cases.html', acute_cases=load_acute_cases())


@app.route('/acute-case/<slug>')
def acute_case_detail(slug):
    """Страница детализации острого случая.
    - Ищет случай по slug
    - Возвращает 404 при отсутствии
    - Отображает шаблон acute_case_detail.html
    """
    case = next((c for c in load_acute_cases() if c['slug'] == slug), None)
    if not case:
        return "Case not found", 404
    return render_template('acute_case_detail.html', case=case)


@app.route('/category')
def category():
    """Страница категорий (типы/миазмы).
    - Загружает классифицированные категории
    - Отображает шаблон category.html
    """
    categories = load_category()
    return render_template('category.html',
                           types=categories['types'],
                           miasms=categories['miasms'])


# Явно задаем имя endpoint, чтобы избежать конфликта
@app.route('/category/<slug>', endpoint='category_detail')
def category_detail(slug):
    """Страница детализации категории.
    - Ищет категорию по slug среди типов и миазмов
    - Возвращает 404 при отсутствии
    - Отображает шаблон category_detail.html
    """
    categories = load_category()
    all_items = categories['types'] + categories['miasms']
    item = next((item for item in all_items if item['slug'] == slug), None)
    if not item:
        return "Item not found", 404
    return render_template('category_detail.html', category=item)


@app.route('/reference')
def reference():
    """Страница справочных материалов.
    - Загружает все справочные материалы
    - Отображает шаблон reference.html
    """
    return render_template('reference.html', materials=load_reference_materials())


@app.route('/reference/<slug>')
def reference_detail(slug):
    """Страница детализации справочного материала.
    - Ищет материал по slug
    - Возвращает 404 при отсутствии
    - Отображает шаблон reference_detail.html
    """
    material = next((m for m in load_reference_materials() if m['slug'] == slug), None)
    if not material:
        return "Material not found", 404
    return render_template('reference_detail.html', material=material)


@app.route('/glossary')
def glossary():
    """Страница глоссария.
    - Загружает и сортирует термины
    - Отображает шаблон glossary.html
    """
    return render_template('glossary.html', terms=load_glossary_terms())


@app.route('/images/<filename>')
def uploaded_file(filename):
    """Отдача статических изображений.
    - Возвращает файлы из настроенной папки UPLOAD_FOLDER
    - Используется для отображения загруженных изображений
    """
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
