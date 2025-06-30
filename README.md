# Homeo Remedy Book

Приложение для справочного материала по гомеопатии

Установить все зависимости:

```bash
$ pip install -r requirements.txt
```

Запустите приложение:

```bash
$ python wsgi.py
```

Откройте в браузере:

http://localhost:5000


### Проект развернут на render.com и на vercel.com и доступен по ссылкам:
https://homeoremedybook.onrender.com/
https://homeoremedybook.vercel.app/


# Удалить старые кэшированные файлы
find . -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete