from flask import Flask
from flask_flatpages import FlatPages

app = Flask(__name__)
app.config.from_pyfile('config.py')

# Настройка FlatPages для Markdown
pages = FlatPages(app)

from app import routes
