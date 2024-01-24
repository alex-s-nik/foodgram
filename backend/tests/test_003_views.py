import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from api.views import TagViewSet
from recipes.models import Tag
from recipes.factories import TagFactory
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

    ...


class TestIngredientViewSet:
    """Тестирование вьюсета Ингридиентов."""

    ...
