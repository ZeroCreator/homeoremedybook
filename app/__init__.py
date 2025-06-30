from flask import Flask
from flask_flatpages import FlatPages
import markdown
from config import Config

app = Flask(__name__,
            static_folder=str(Config.STATIC_DIR),
            static_url_path='/static',
            template_folder=str(Config.TEMPLATE_DIR))

# Применяем конфигурацию
app.config.from_object(Config)

pages = FlatPages(app)
app.config['FLATPAGES_ROOT'] = Config.FLATPAGES_ROOT

@app.template_filter('markdown')
def markdown_filter(text):
    return markdown.markdown(text)

from app import routes
