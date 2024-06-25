# Django testing
Коллекция тестов для проектов.

**YaNews**: новостной сайт, где пользователи могут оставлять комментарии к новостям.

Протестирован с использованием `pytest`.

[Тесты находятся в директории `ya_news/news/pytest_tests/`](ya_news/news/pytest_tests/)

**YaNote:** электронная записная книжка.

Протестирован с использованием `unittest`.

[Тесты находятся в директории `ya_note/notes/tests/`](ya_note/notes/tests/)
## Технологии
- [Python 3.9.10](https://docs.python.org/3.9/index.html)
- [Django 3.2.15](https://docs.djangoproject.com/en/3.2/)
- [Pytest-django 4.5.2](https://pypi.org/project/pytest-django/4.5.2/)
- [Unittest](https://docs.python.org/3.9/library/unittest.html)

### Запуск тестов
Клонируйте проект и перейдите в его директорию:
```bash
git clone git@github.com:Wiz410/django_testing.git
cd django_testing
```

Cоздайте и активируйте виртуальное окружение:
- Для Windows
```bash
python -m venv venv
source venv/Scripts/activate
```

- Для Linux и macOS
```bash
python3 -m venv venv
source venv/bin/activate
```

Установите зависимости из файла `requirements.txt`:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Тест для YaNews:**

Перейдите в директорию проекта и запустите тесты:
```bash
cd ya_news
pytest
```

**Тест для YaNote:**

Перейдите в директорию проекта и запустите тесты:
```bash
cd ya_note
python manage.py test -v 2
```

#### Авторы
- [Danila Polunin](https://github.com/Wiz410)
