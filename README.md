# Terminology API

Terminology API — это сервис для управления справочниками и их версиями. Проект предоставляет интерфейс для работы со справочниками, их элементами и версиями через Django Admin и REST API.

## Функциональность

- Управление справочниками, их версиями и элементами.
- Поддержка локализации для мультиязычной работы.
- Административный интерфейс на базе Django Admin.

---

## Установка и настройка

1. Клонирование репозитория

```bash
git clone https://github.com/Gricana/terminology_api.git
cd terminology_api
```
2. Установите зависимости
```bash 
poetry install
```
4. Активируйте виртуальное окружение
```bash
poetry shell
```
5. Примените миграции базы данных
```bash 
poetry run python manage.py makemigrations handbook
poetry run python manage.py migrate
```
6. Создайте суперпользователя
```bash 
poetry run python manage.py createsuperuser
```
7. Запуск проекта
```bash 
poetry run python manage.py runserver
```
Перейдите в браузере по адресу: http://127.0.0.1:8000/admin/.

### Команды для работы с локализацией

1. Установка пакета для предоставления механизма перевода строк текста
```bash
sudo apt install gettext
```

2. Компиляция переводов:
```bash 
poetry run django-admin compilemessages
```
### Тестирование

Запуск тестов:
```bash 
poetry run python manage.py test
```
### Дополнительно
Локализация: Поддерживает смену языка интерфейса через настройку 
LANGUAGE_CODE в файле [settings.py](https://github.com/Gricana/terminology_api/blob/cd7f0486f9bda27f86acb9a14dcf4242d34220d8/terminology_api/settings.py#L121).

Доступные маршруты API:

- [api/docs/](http://localhost:8000/api/docs/) - документация Swagger API