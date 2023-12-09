import jsonschema
import pytest
import requests
import json
import os
from jsonschema import validate
from config import *
from schema.search_schema import schema


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
        4. Для проверок можно использовать параметризацию параметра GET-запроса"""

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

        response = requests.get(search_url, headers=headers_get)

        # Тест статус кода
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"

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
        assert len(response.json()) == limit, \
            f"Expected {limit} objects in the response, but got {len(response.json())}"

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

        # Добавим необязательные параметры
        payload = {'sub_id': 'pomeranian',
                   'breed_ids': '21'}
        # Загрузим изображение в запрос
        files = [('file', ('pome.png', open('img/pome.png', 'rb'), 'image/png'))]
        response = requests.request("POST", upload_url, headers=headers_post, data=payload, files=files)

        # Проверка статус кода
        assert response.status_code == 201, f"Expected status code 201, but got {response.status_code}"

    @pytest.mark.parametrize("breed_id", [BREED_ID, BREED_ID2])
    def test_breeds_filters(self, breed_id):
        """ В этом тесте проверим:
        1. Статус код
        2. Проверьте тип породы на основе ее идентификатора
        3. Этот метод можно использовать для проверки любого типа поля в ответе JSON
        4. Настройте параметр запроса GET для проверок """

        # Параметр запроса
        search_url = URL + f"v1/breeds/{breed_id}"
        response = requests.get(search_url)

        # Проверка статус0кода
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"

        # Проверьте поле "breed_id" в ответе
        assert response.json()['id'] == breed_id, f"Expected breed id {breed_id}, but got {response.json()['id']}"

    def test_create_image_with_breed(self, headers_post, headers_get):
        # Загрузим изображение в запрос
        upload_url = URL + "v1/images/upload"
        files = [('file', ('pome.png', open('img/pome.png', 'rb'), 'image/png'))]
        response = requests.request("POST", upload_url, headers=headers_post, files=files)

        # Вытащим image_id для создания пары с породой собаки
        response_json = response.json()
        image_id = response_json["id"]
        print("Созданный image_id изображения:", image_id)

        # Создадим последующий POST запрос с указанием image_id и breed_id
        upload_new_url = URL + f"v1/images/{image_id}/breeds"

        # Добавим обязательный параметр BREED_ID из конфига
        payload = json.dumps({
            "breed_id": BREED_ID
        })
        # Загрузим изображение в запрос
        response = requests.request("POST", upload_new_url, headers=headers_get, data=payload)

        # Проверка статус кода
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"

        # Проверить, что id установлено, как в body
        response_json = response.json()
        assert response_json.get('id') == BREED_ID, f"Expected breed_id {BREED_ID} not found in JSON response!"

        # Проверим, что наша порода с ID совпадает BREED_ID и image_id
        search_url = URL + f"v1/images/{image_id}"
        response = requests.get(search_url, headers=headers_get)
        json_response = response.json()
        assert json_response["breeds"][0]["id"] == int(BREED_ID) and json_response["id"] == image_id, (
            f"Value of 'id' in 'breeds' is not equal to {BREED_ID} "
            f"and id {image_id}")

    def test_create_image_invalid_format(self, headers_post):
        """ В данном тесте проверяем:
                1. Статус код
                2. Загрузку невалидного формата файла
                3. Загрузка с выбором пути папки с помощью библиотеки os """
        upload_url = URL + "v1/images/upload"

        # Пусть к папке с img
        img_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'img/invalid_format.docx'))

        # Создаем объект FormData
        files = {'file': (open(img_path, 'rb'))}

        # Отправляем POST-запрос с использованием FormData
        response = requests.post(upload_url, headers=headers_post, files=files)

        # Проверка статус кода
        assert response.status_code == 400, f"Expected status code 400, but got {response.status_code}"

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

        # Проверка статус кода
        assert response.status_code == 401, f"Expected status code 401, but got {response.status_code}"

    def test_delete_image_by_id(self, headers_get, headers_post):
        """ В данном тесте проверяем:
                1. Статус код
                2. Получить список своих фото
                3. Удалить изображение по image_id из своих файлов
                4. Проверить, что файл удален """

        # Создание нового изображения и получение его image_id
        upload_url = URL + "v1/images/upload"
        files = files = [('file', ('dobermann.jpg', open('img/dobermann.jpg', 'rb'), 'image/jpeg'))]
        response = requests.request("POST", upload_url, headers=headers_post, files=files)

        # Вытаскиваем image_id
        response_json = response.json()
        image_id = response_json["id"]
        print("Созданный image_id изображения:", image_id)

        # Проверяем, что image_id он есть в ответе GET
        search_url = URL + f"v1/images/{image_id}"
        response = requests.get(search_url, headers=headers_get)
        response_json = response.json()
        assert response_json.get('id') == image_id, f"Expected image_id {image_id} not found in JSON response!"

        # Теперь удалим изображение по image_id
        search_url = URL + f"v1/images/{image_id}"
        response = requests.delete(search_url, headers=headers_get)

        # Тест статус кода (Что изображение удалено)
        assert response.status_code == 204, f"Expected status code 200, but got {response.status_code}"

        # Проверим, что изображение удалено
        search_url = URL + f"v1/images/{image_id}"
        response = requests.get(search_url, headers=headers_get)
        print("Сообщение об успешном удалении:", response.text)

        # Тест статус кода (Ожидаем 400, так как изображение удалено)
        assert response.status_code == 400, f"Expected status code 400, but got {response.status_code}"