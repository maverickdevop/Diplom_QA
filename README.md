# Проект курса GeekBrains. Исследование и разработка стратегии тестирования RESTful API с использованием проекта The Dog API (developers.thedogapi.com)
 
Ссылка на курс: [Клик](https://stepik.org/course/575).

Проект, разработанный в рамках дипломного проекта "Исследование и разработка стратегии тестирования RESTful API с использованием проекта The Dog API (developers.thedogapi.com)".

## Инструменты

- Python 3.10 / Python 3.11
- Requests
- PyTest
- JSONSchema

## Структура проекта

Проект организован следующим образом:

- theDogAPI/test_images.py - Основной файл с тестами. Здесь находятся ваши тестовые сценарии.
- theDogAPI/config.py - Файл с конфигурациями, содержит эндпонт, токен и прочие используемые в тестах данные.
- theDogAPI/conftest.py - Файл с тестовыми фикстурами. Здесь содержатся методы для формирования request headers для HTTP запросов.
- theDogAPI/schema - Папка с файлми схемы. Нужна для валидации JSON схемы.
- theDogAPI/img - Папка с изображениями разных форматов. Необходима для путей формирования загрузок на сервер.


## Установка и настройка

1. Создайте виртуальное окружение:
   ```shell
   python -m venv venv

2. Установите зависимости из файла requirements.txt:
   ```shell
   pip install -r requirements.txt

3. Для запуска тестов используйте команду:
   ```shell
   pytest test_images.py 
