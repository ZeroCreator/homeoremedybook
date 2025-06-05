from flask import render_template, request
from app import app, pages
from app.models import CATEGORIES
from pathlib import Path


@app.route('/')
def index():
    # Получаем все карточки
    all_cards = [p for p in pages if 'category' in p.meta]

    # Фильтрация
    category_filter = request.args.get('category')
    keyword_filter = request.args.get('keywords', '').lower()

    filtered_cards = []
    for card in all_cards:
        if category_filter and card.meta['category'] != category_filter:
            continue
        if keyword_filter and keyword_filter not in card.body.lower():
            continue
        filtered_cards.append(card)

    return render_template('index.html',
                           cards=filtered_cards,
                           categories=CATEGORIES,
                           selected_category=category_filter,
                           keyword_filter=keyword_filter
                           )


@app.route('/category/<slug>')
def category(slug):
    category = next((c for c in CATEGORIES if c.slug == slug), None)
    if not category:
        return "Категория не найдена", 404

    category_cards = [p for p in pages if p.meta.get('category') == slug]
    return render_template('category.html',
                           category=category,
                           cards=category_cards
                           )


@app.route('/articles')
def articles():
    return render_template('articles.html')
