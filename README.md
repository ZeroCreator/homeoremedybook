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

Удалить старые кэшированные файлы:

```bash
find . -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete
```

### Проект развернут на `vercel.com` и доступен по ссылке:

https://homeoremedybook.vercel.app/
