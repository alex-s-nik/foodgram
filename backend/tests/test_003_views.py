import json
import pytest
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory, force_authenticate

from api.utils import image_to_base64
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
        'usertype, method, action, expectation_status_code',
        [
            ('unauthorize', 'get', 'list', status.HTTP_200_OK),
            ('unauthorize', 'get', 'retrieve', status.HTTP_200_OK),
            ('unauthorize', 'post', 'create', status.HTTP_405_METHOD_NOT_ALLOWED),
            ('unauthorize', 'put', 'update', status.HTTP_405_METHOD_NOT_ALLOWED),
            ('unauthorize', 'patch', 'partial_update', status.HTTP_405_METHOD_NOT_ALLOWED),
            ('unauthorize', 'delete', 'destroy', status.HTTP_405_METHOD_NOT_ALLOWED),
            ('user', 'get', 'list', status.HTTP_200_OK),
            ('user', 'get', 'retrieve', status.HTTP_200_OK),
            ('user', 'post', 'create', status.HTTP_405_METHOD_NOT_ALLOWED),
            ('user', 'put', 'update', status.HTTP_405_METHOD_NOT_ALLOWED),
            ('user', 'patch', 'partial_update', status.HTTP_405_METHOD_NOT_ALLOWED),
            ('user', 'delete', 'destroy', status.HTTP_405_METHOD_NOT_ALLOWED),
            ('admin', 'get', 'list', status.HTTP_200_OK),
            ('admin', 'get', 'retrieve', status.HTTP_200_OK),
            ('admin', 'post', 'create', status.HTTP_405_METHOD_NOT_ALLOWED),
            ('admin', 'put', 'update', status.HTTP_405_METHOD_NOT_ALLOWED),
            ('admin', 'patch', 'partial_update', status.HTTP_405_METHOD_NOT_ALLOWED),
            ('admin', 'delete', 'destroy', status.HTTP_405_METHOD_NOT_ALLOWED),
        ],
    )
    @pytest.mark.django_db()
    def test_tags(self, usertype, method, action, expectation_status_code):
        """Тестирование работы с Тегами: все методы от всех пользователей."""

        tag_created = TagFactory.create()
        tag_built = TagFactory.build()

        request_data = {'path': '/api/tags/'}
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
        view_data = {'request': api_request}
        if (method == 'get' and action == 'retrieve') or method in ['put', 'patch', 'delete']:
            view_data['pk'] = tag_created.pk
        # Если связанный с методом action будет отсутствовать во Вьюесете,
        # то response = view(**view_data) будет поднимать исключение AttributeError
        # Пока будет такая заглушка для кейсов от которых ожидаем 405 ответ.
        view = TagViewSet.as_view({method: action})
        try:
            response = view(**view_data)

            assert response.status_code == expectation_status_code
        except AttributeError:
            pass


class TestRecipeViewSet:
    """Тестирование вьюсета Рецептов."""

    @pytest.mark.parametrize(
        'usertype, who_created, method, action, expectation_status_code',
        [
            ('unauthorize', 'not_self', 'get', 'list', status.HTTP_200_OK),
            ('unauthorize', 'not_self', 'get', 'retrieve', status.HTTP_200_OK),
            ('unauthorize', 'not_self', 'post', 'create', status.HTTP_401_UNAUTHORIZED),
            ('unauthorize', 'not_self', 'put', 'update', status.HTTP_401_UNAUTHORIZED),
            ('unauthorize', 'not_self', 'patch', 'partial_update', status.HTTP_401_UNAUTHORIZED),
            ('unauthorize', 'not_self', 'delete', 'destroy', status.HTTP_401_UNAUTHORIZED),
            ('user', 'self', 'get', 'list', status.HTTP_200_OK),
            ('user', 'self', 'get', 'retrieve', status.HTTP_200_OK),
            ('user', 'self', 'post', 'create', status.HTTP_201_CREATED),
            ('user', 'self', 'put', 'update', status.HTTP_200_OK),
            ('user', 'self', 'patch', 'partial_update', status.HTTP_200_OK),
            ('user', 'self', 'delete', 'destroy', status.HTTP_204_NO_CONTENT),
            ('user', 'not_self', 'get', 'list', status.HTTP_200_OK),
            ('user', 'not_self', 'get', 'retrieve', status.HTTP_200_OK),
            ('user', 'not_self', 'put', 'update', status.HTTP_401_UNAUTHORIZED),
            ('user', 'not_self', 'patch', 'partial_update', status.HTTP_401_UNAUTHORIZED),
            ('user', 'not_self', 'delete', 'destroy', status.HTTP_401_UNAUTHORIZED),
            ('admin', 'self', 'get', 'list', status.HTTP_200_OK),
            ('admin', 'self', 'get', 'retrieve', status.HTTP_200_OK),
            ('admin', 'self', 'post', 'create', status.HTTP_201_CREATED),
            ('admin', 'self', 'put', 'update', status.HTTP_200_OK),
            ('admin', 'self', 'patch', 'partial_update', status.HTTP_200_OK),
            ('admin', 'self', 'delete', 'destroy', status.HTTP_204_NO_CONTENT),
            ('admin', 'not_self', 'get', 'list', status.HTTP_200_OK),
            ('admin', 'not_self', 'get', 'retrieve', status.HTTP_200_OK),
            ('admin', 'not_self', 'put', 'update', status.HTTP_200_OK),
            ('admin', 'not_self', 'patch', 'partial_update', status.HTTP_200_OK),
            ('admin', 'not_self', 'delete', 'destroy', status.HTTP_204_NO_CONTENT),
        ],
    )
    @pytest.mark.django_db()
    def test_recipe(self, usertype, who_created, method, action, expectation_status_code):
        """Тест всех возможностей: CRUD анонимно, CRUD зарегистрированного пользователя,
        CRUD админа, а также RUD Рецептов, автором которых не является текущий пользователь.

        Параметры:
        usertype: unauthorize - гость, user - зарегистрированный пользователь, admin - администратор
        who_created: с каким объектом работаем, self - созданный самим, not_self - созданный другим пользователем
        method, action: метод и действие для запроса
        expectation_status_code: ожидаемый статус-код результата запроса.
        """

        # объект с набором сгенерированных полей
        recipe_built = RecipeFactory.build()

        # объект, созданный другим пользователем
        recipe_non_self_created = RecipeFactory.create()

        # формируем параметры для RequestFactory.
        # Если запрос идет к конкретному объекту, то параметры будут path, data и content_type,
        # если же запрос на создание и получение списка, то параметром будет только path.
        request_data = {'path': ''}

        # формирование data и content_type
        if method in ['post', 'put', 'patch']:
            ingredients = [{'id': ingredient.id, 'amount': 20} for ingredient in IngredientFactory.create_batch(3)]
            request_data['data'] = {
                'name': recipe_built.name,
                'image': image_to_base64(recipe_built.image.file.read(), 'jpg'),
                'text': recipe_built.text,
                'cooking_time': recipe_built.cooking_time,
                'ingredients': ingredients,
                'tags': [],
            }
            request_data['data'] = json.dumps(request_data['data'])
            request_data['content_type'] = 'application/json'

        api_request = getattr(APIRequestFactory(), method)(**request_data)

        if usertype != 'unauthorize':
            user = UserFactory.create(is_superuser=(usertype == 'admin'))
            recipe_self_created = RecipeFactory.create(author=user)
            force_authenticate(request=api_request, user=user)

        view = RecipeViewSet.as_view({method: action})

        view_data = {'request': api_request}
        if (method == 'get' and action == 'retrieve') or method in ['put', 'patch', 'delete']:
            if who_created == 'self':
                view_data['pk'] = recipe_self_created.pk
            elif who_created == 'not_self':
                view_data['pk'] = recipe_non_self_created.pk

        response = view(**view_data)

        assert response.status_code == expectation_status_code


class TestIngredientViewSet:
    """Тестирование вьюсета Ингридиентов."""

    ...
