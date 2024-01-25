import json
import pytest
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory, force_authenticate

from api.views import RecipeViewSet, TagViewSet
from recipes.models import Tag
from recipes.factories import IngredientFactory, RecipeFactory, TagFactory
from users.factories import UserFactory


class TestUserViewSet:
    """Тестирование вьюсета Пользователя."""

    ...


class TestTagViewSet:
    """Тестирование вьюсета Тегов."""

    @pytest.mark.parametrize(
        'usertype, method, type_, expectation_status_code',
        [
            ('unauthorize', 'get', 'list', status.HTTP_200_OK),
            ('unauthorize', 'get', 'retrieve', status.HTTP_200_OK),
            ('unauthorize', 'post', 'retrieve', status.HTTP_405_METHOD_NOT_ALLOWED),
            ('unauthorize', 'put', 'retrieve', status.HTTP_405_METHOD_NOT_ALLOWED),
            ('unauthorize', 'patch', 'retrieve', status.HTTP_405_METHOD_NOT_ALLOWED),
            ('unauthorize', 'delete', 'retrieve', status.HTTP_405_METHOD_NOT_ALLOWED),
            ('user', 'get', 'list', status.HTTP_200_OK),
            ('user', 'get', 'retrieve', status.HTTP_200_OK),
            ('user', 'post', 'retrieve', status.HTTP_405_METHOD_NOT_ALLOWED),
            ('user', 'put', 'retrieve', status.HTTP_405_METHOD_NOT_ALLOWED),
            ('user', 'patch', 'retrieve', status.HTTP_405_METHOD_NOT_ALLOWED),
            ('user', 'delete', 'retrieve', status.HTTP_405_METHOD_NOT_ALLOWED),
            ('admin', 'get', 'list', status.HTTP_200_OK),
            ('admin', 'get', 'retrieve', status.HTTP_200_OK),
            ('admin', 'post', 'retrieve', status.HTTP_405_METHOD_NOT_ALLOWED),
            ('admin', 'put', 'retrieve', status.HTTP_405_METHOD_NOT_ALLOWED),
            ('admin', 'patch', 'retrieve', status.HTTP_405_METHOD_NOT_ALLOWED),
            ('admin', 'delete', 'retrieve', status.HTTP_405_METHOD_NOT_ALLOWED),
        ],
    )
    @pytest.mark.django_db()
    def test_tags(self, usertype, method, type_, expectation_status_code):
        """Тестирование работы с Тегами: все методы от всех пользователей."""

        tag_created = TagFactory.create()
        tag_built = TagFactory.build()

        request_data = {'path': ''}
        if method in ['post', 'put', 'patch']:
            request_data['data'] = {
                'slug': tag_built.slug,
                'name': tag_built.name,
                'color': tag_built.color,
            }
        api_request = getattr(APIRequestFactory(), method)(**request_data)

        if usertype != 'unauthorize':
            user = UserFactory.create(is_superuser=(usertype == 'admin'))
            force_authenticate(request=api_request, user=user)
        view = TagViewSet.as_view({'get': type_})
        view_data = {'request': api_request}
        if type_ == 'retrieve' and method != 'post':
            view_data['pk'] = tag_created.pk
        response = view(**view_data)

        assert response.status_code == expectation_status_code


class TestRecipeViewSet:
    """Тестирование вьюсета Рецептов."""

    @pytest.mark.parametrize(
        'usertype, who_created, method, type_, expectation_status_code',
        [
            ('unauthorize', 'not_self', 'get', 'list', status.HTTP_200_OK),
            ('unauthorize', 'not_self', 'get', 'retrieve', status.HTTP_200_OK),
            ('unauthorize', 'not_self', 'post', 'retrieve', status.HTTP_401_UNAUTHORIZED),
            ('unauthorize', 'not_self', 'put', 'retrieve', status.HTTP_401_UNAUTHORIZED),
            ('unauthorize', 'not_self', 'patch', 'retrieve', status.HTTP_401_UNAUTHORIZED),
            ('unauthorize', 'not_self', 'delete', 'retrieve', status.HTTP_401_UNAUTHORIZED),
            ('user', 'self', 'get', 'list', status.HTTP_200_OK),
            ('user', 'self', 'get', 'retrieve', status.HTTP_200_OK),
            ('user', 'self', 'post', 'retrieve', status.HTTP_201_CREATED),
            ('user', 'self', 'put', 'retrieve', status.HTTP_200_OK),
            ('user', 'self', 'patch', 'retrieve', status.HTTP_200_OK),
            ('user', 'self', 'delete', 'retrieve', status.HTTP_204_NO_CONTENT),
            ('user', 'not_self', 'get', 'list', status.HTTP_200_OK),
            ('user', 'not_self', 'get', 'retrieve', status.HTTP_200_OK),
            ('user', 'not_self', 'put', 'retrieve', status.HTTP_401_UNAUTHORIZED),
            ('user', 'not_self', 'patch', 'retrieve', status.HTTP_401_UNAUTHORIZED),
            ('user', 'not_self', 'delete', 'retrieve', status.HTTP_401_UNAUTHORIZED),
            ('admin', 'self', 'get', 'list', status.HTTP_200_OK),
            ('admin', 'self', 'get', 'retrieve', status.HTTP_200_OK),
            ('admin', 'self', 'post', 'retrieve', status.HTTP_201_CREATED),
            ('admin', 'self', 'put', 'retrieve', status.HTTP_200_OK),
            ('admin', 'self', 'patch', 'retrieve', status.HTTP_200_OK),
            ('admin', 'self', 'delete', 'retrieve', status.HTTP_204_NO_CONTENT),
            ('admin', 'not_self', 'get', 'list', status.HTTP_200_OK),
            ('admin', 'not_self', 'get', 'retrieve', status.HTTP_200_OK),
            ('admin', 'not_self', 'put', 'retrieve', status.HTTP_200_OK),
            ('admin', 'not_self', 'patch', 'retrieve', status.HTTP_200_OK),
            ('admin', 'not_self', 'delete', 'retrieve', status.HTTP_204_NO_CONTENT),
        ],
    )
    @pytest.mark.django_db()
    def test_recipe(self, usertype, who_created, method, type_, expectation_status_code):
        recipe_built = RecipeFactory.build()
        recipe_created = RecipeFactory.create()

        request_data = {'path': ''}
        if method in ['post', 'put', 'patch']:
            request_data['data'] = {
                'name': recipe_built.name,
                'image': recipe_built.image,
                'text': recipe_built.text,
                'cooking_time': recipe_built.cooking_time,
            }
        api_request = getattr(APIRequestFactory(), method)(**request_data)
        if usertype != 'unauthorize':
            user = UserFactory.create(is_superuser=(usertype == 'admin'))
            force_authenticate(request=api_request, user=user)
        view = RecipeViewSet.as_view({'get': type_})
        view_data = {'request': api_request}
        if type_ == 'retrieve' and method != 'post':
            view_data['pk'] = recipe_created.pk
        response = view(**view_data)

        assert response.status_code == expectation_status_code

    @pytest.mark.django_db()
    def test_create_recipe(self):
        recipe_built = RecipeFactory.build()
        ingredients = [{'id': ingredient.id, 'amount': 20} for ingredient in IngredientFactory.create_batch(3)]
        print(ingredients)
        print(f'{recipe_built.name=}')
        '''{
            'name': recipe_built.name,
            'image': recipe_built.image,
            'text': recipe_built.text,
            'cooking_time': recipe_built.cooking_time,
            'ingredients': ingredients,
        },'''
        factory = APIRequestFactory()
        data = {
            "name": "asdfas",
            "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
            "text": "gdfgsdf",
            "cooking_time": 15,
            "ingredients": [{"id": 1, "amount": 20}, {"id": 2, "amount": 20}],
            "tags": [],
        }

        '''api_request = factory.post(
            '/',
            data=data
            # content_type='application/json',
        )'''
        # request = Request(api_request)
        json_data = json.dumps(data)  # data must be converted to string for POST requests
        request = factory.post('', data=json_data, content_type='application/json')

        print(f'{request.POST=}')
        print(f'{request.__dir__()=}')
        print(f'{request.META=}')
        user = UserFactory.create()
        force_authenticate(request=request, user=user)
        view = RecipeViewSet.as_view({'post': 'create'})
        response = view(request=request)
        response.render()
        print(response.data)
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.django_db()
    def test_create_recipe1(self):
        recipe_built = RecipeFactory.build()
        ingredients = [{'id': ingredient.id, 'amount': 20} for ingredient in IngredientFactory.create_batch(3)]

        factory = APIRequestFactory()
        data = {
            "name": recipe_built.name,
            "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
            "text": recipe_built.text,
            "cooking_time": recipe_built.cooking_time,
            "ingredients": ingredients,
            "tags": [],
        }

        json_data = json.dumps(data)
        request = factory.post('', data=json_data, content_type='application/json')

        print(f'{request.POST=}')
        print(f'{request.__dir__()=}')
        print(f'{request.META=}')
        user = UserFactory.create()
        force_authenticate(request=request, user=user)
        view = RecipeViewSet.as_view({'post': 'create'})
        response = view(request=request)
        print(response.data)
        assert response.status_code == status.HTTP_201_CREATED


class TestIngredientViewSet:
    """Тестирование вьюсета Ингридиентов."""

    ...
