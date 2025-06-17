import os
from flask import Flask
from flask_flatpages import FlatPages
import markdown

app = Flask(__name__,
            static_folder='static',
            template_folder='templates')

app.config.from_object('config.Config')

# Явно указываем пути
app.static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
app.template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

pages = FlatPages(app)

from app import routes

@app.template_filter('markdown')
def markdown_filter(text):
    return markdown.markdown(text)
