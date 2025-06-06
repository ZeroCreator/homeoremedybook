import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Config:
    SECRET_KEY = 'secret'
    FLATPAGES_ROOT = os.path.join(BASE_DIR, 'homeoremedybook', 'app', 'content')
    FLATPAGES_EXTENSION = '.md'
    FLATPAGES_MARKDOWN_EXTENSIONS = ['fenced_code', 'tables']
    ACUTE_CASES_FOLDER = os.path.join(BASE_DIR, 'homeoremedybook', 'app', 'content', 'acute_cases')
    UPLOAD_FOLDER = 'static/images'

    @staticmethod
    def init_app(app):
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
