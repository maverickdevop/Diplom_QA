import jsonschema
import pytest
import requests
import os
import json
from jsonschema import validate
from config import *
from schema.get_schema import schema
from schema.search_schema import schema
from requests_toolbelt.multipart.encoder import MultipartEncoder


class TestDogAPI:

    def test_search_images(self):
        """ В данном тесте проверяем:
                1. Статус код
                2. Делаем проверку по всем необязательным параметрам
                3. Провалидируем JSON схему """
        search_url = URL + "v1/images/search"

        # Необязательные параметры
        data = {
            'size': 'med',
            'mime_types': 'jpg',
            'format': 'json',
            'order': 'RANDOM',
            'has_breeds': True,
            'limit': 10,
            'page': 0,
        }
        response = requests.get(search_url, params=data)

        # Тест статус кода
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"

        # Валидация по JSON-схеме
        try:
            validate(instance=response.json(), schema=schema)
        except jsonschema.exceptions.ValidationError as e:
            pytest.fail(f"Response schema validation error: {e}")

    @pytest.mark.parametrize("mime_type", ["jpg", "png"])
    def test_image_format_validation(self, mime_type):
        """ В данном тесте проверяем:
        1. Статус код
        2. Проверяем какой тип изображения jpg/png
        3. Данным методом можно проверить любой тип поля в ответе JSON
        4. Для проверок можно изпользовать параметризацию параметра GET-запроса"""

        # Параметры запроса
        search_url = URL + "v1/images/search"
        data = {'mime_types': mime_type}

        # Отправляем GET-запрос
        response = requests.get(search_url, params=data)

        # Проверка статус кода
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"

        # Проверка типа изображения
        images = response.json()
        for image in images:
            url = image.get('url', '')
            assert url.lower().endswith(f'.{mime_type}'), f"Invalid image format for URL: {url}"

    def test_get_my_images(self, headers_get):
        """ В данном тесте проверяем:
        1. Статус код
        2. Валидируем JSON схему """
        search_url = URL + "v1/images"

        # Необязательные параметры
        data = {
            'limit': 10,
            'page': 0,
            'order': 'DESC'
        }
        response = requests.get(search_url, params=data, headers=headers_get)

        # Тест статус кода
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"

        # Валидация по JSON-схеме
        try:
            validate(instance=response.json(), schema=schema)
        except jsonschema.exceptions.ValidationError as e:
            pytest.fail(f"Response schema validation error: {e}")

    def test_get_my_images_without_token(self):
        """ В данном тесте проверяем:
        1. Статус код должен быть 401, так как нет x-api-key """
        search_url = URL + "v1/images"
        response = requests.get(search_url)

        # Тест статус кода
        assert response.status_code == 400, f"Expected status code 400, but got {response.status_code}"

    @pytest.mark.parametrize("limit", [3, 5, 10])  # Примеры разных значений лимита
    def test_get_breeds_list_with_limit(self, headers_get, limit):
        """ Тест проверки корректности передачи лимитов и соответствия количества объектов в JSON-ответе"""
        search_url = URL + "v1/breeds"

        # Параметры запроса
        data = {'limit': limit, 'page': 0}

        response = requests.get(search_url, params=data, headers=headers_get)

        # Тест статус кода
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"

        # Валидация лимитов в JSON ответе
        assert len(response.json()) == limit, f"Expected {limit} objects in the response, but got {len(response.json())}"

    def test_get_image_by_id(self, headers_get):
        """ В данном тесте проверяем:
        1. Статус код
        2. Проверка наличия в ответе картинки с image_id """

        search_url = URL + f"v1/images/{IMAGE_ID}"
        response = requests.get(search_url, headers=headers_get)

        # Тест статус кода
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"

        # Тест проверки ID в JSON ответе
        response_json = response.json()
        assert response_json.get('id') == IMAGE_ID, f"Expected id {IMAGE_ID} not found in JSON response!"

    def test_create_image(self, headers_post):
        upload_url = URL + "v1/images/upload"
        img_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'img/pome.png'))

        # Создаем объект MultipartEncoder
        multipart_data = MultipartEncoder(
            fields={'file': ('pome.png', open(img_path, 'rb'))}
        )

        # Отправляем POST-запрос с использованием MultipartEncoder
        response = requests.post(
            upload_url,
            headers={**headers_post, 'Content-Type': multipart_data.content_type},
            data=multipart_data
        )

        # Проверка статус кода
        assert response.status_code == 201, f"Expected status code 201, but got {response.status_code}"

    def test_create_image_invalid_format(self, headers_post):
        """ В данном тесте проверяем:
                1. Статус код
                2. Загрузку невалидного формата файла """
        upload_url = URL + "v1/images/upload"
        img_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'img/invalid_format.docx'))

        # Создаем объект FormData
        files = {'file': (open(img_path, 'rb'))}

        # Отправляем POST-запрос с использованием FormData
        response = requests.post(upload_url, headers=headers_post, files=files)

        # Проверка статус кода
        assert response.status_code == 400, f"Expected status code 400, but got {response.status_code}"

    def test_create_image_with_existed_id(self, headers_post):
        """ В данном тесте проверяем:
        1. Статус код
        2. Создать изображение с image_id и породой """
        upload_url = URL + f"v1/images/{IMAGE_ID}"
        data = {
            'breed_id': 10
        }
        # Отправляем POST-запрос
        response = requests.post(upload_url, headers=headers_post, data=data)

        # Проверка статус кода
        assert response.status_code == 201, f"Expected status code 201, but got {response.status_code}"

    def test_create_image_with_other_user_id(self, headers_get):
        """ В данном тесте проверяем:
        1. Статус код 400
        2. Создать изображение с image_id и породой
        3. Убедиться, что создать пару порода + изображение чужого юзера нельзя """
        upload_url = URL + f"v1/images/{OTHER_IMAGE_ID}/breeds"
        payload = json.dumps({
            "breed_id": 10
        })
        # Отправляем POST-запрос
        response = requests.post(upload_url, headers=headers_get, data=payload)
        print(response.text)

        # Проверка статус кода
        assert response.status_code == 401, f"Expected status code 401, but got {response.status_code}"

    def test_delete_image_by_id(self, headers_get):
        """ В данном тесте проверяем:
                1. Статус код
                2. Удалить изобрадение по image_id из своих файлов """

        search_url = URL + f"v1/images/shceRnA48"
        response = requests.delete(search_url, headers=headers_get)

        # Тест статус кода
        assert response.status_code == 204, f"Expected status code 200, but got {response.status_code}"
