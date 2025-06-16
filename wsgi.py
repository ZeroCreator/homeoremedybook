from app import app as application
import os

application.template_folder = os.path.join(os.path.dirname(__file__), 'app/templates')
application.static_folder = os.path.join(os.path.dirname(__file__), 'app/static')

if __name__ == "__main__":
    application.run()
