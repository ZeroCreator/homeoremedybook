from app import app as application  # Vercel ожидает переменную 'application'
import logging

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    application.run()
