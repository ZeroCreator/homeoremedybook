from app import app as application
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

application.template_folder = os.path.join(os.path.dirname(__file__), 'app/templates')
application.static_folder = os.path.join(os.path.dirname(__file__), 'app/static')


if __name__ == "__main__":
    application.run()
