import os
from flask import Flask
from flask_flatpages import FlatPages
import markdown

app = Flask(__name__)

app.config.from_object('config.Config')

pages = FlatPages(app)

from app import routes

@app.template_filter('markdown')
def markdown_filter(text):
    return markdown.markdown(text)
