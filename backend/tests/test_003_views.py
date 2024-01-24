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
        'usertype, expectation',
        [
            pytest.param(
                'unauthorize',
                {'status_code': status.HTTP_200_OK},
                id="unauthorize-get-list",
            ),
            pytest.param(
                'user',
                {'status_code': status.HTTP_200_OK},
                id="user-get-list",
            ),
            pytest.param(
                'admin',
                {'status_code': status.HTTP_200_OK},
                id="admin-get-list",
            ),
        ],
    )
    @pytest.mark.django_db()
    def test_list_tags(self, usertype, expectation):
        """Тестирование получения списка всех Тегов.
        Доступно всем пользователям."""
        api_request = APIRequestFactory().get('')
        if usertype != 'unauthorize':
            user = UserFactory.create(is_superuser=(usertype == 'admin'))
            force_authenticate(request=api_request, user=user)
        list_view = TagViewSet.as_view({'get': 'list'})
        response = list_view(api_request)
        assert response.status_code == expectation['status_code']
        assert len(response.data) == Tag.objects.count()

    @pytest.mark.parametrize(
        'usertype, expectation',
        [
            pytest.param(
                'unauthorize',
                {'status_code': status.HTTP_200_OK},
                id="unauthorize-get-obj",
            ),
            pytest.param(
                'user',
                {'status_code': status.HTTP_200_OK},
                id="user-get-obj",
            ),
            pytest.param(
                'admin',
                {'status_code': status.HTTP_200_OK},
                id="admin-get-obj",
            ),
        ],
    )
    @pytest.mark.django_db()
    def test_obj_tags(self, usertype, expectation):
        """Тестирование получения конкретного Тега.
        Доступно всем пользователям."""
        test_tag = TagFactory.create()

        api_request = APIRequestFactory().get('')
        if usertype != 'unauthorize':
            user = UserFactory.create(is_superuser=(usertype == 'admin'))
            force_authenticate(request=api_request, user=user)
        obj_view = TagViewSet.as_view({'get': 'retrieve'})
        response = obj_view(api_request, pk=test_tag.pk)
        assert response.status_code == expectation['status_code']

    @pytest.mark.parametrize(
        'usertype, expectation',
        [
            pytest.param(
                'unauthorize',
                {'status_code': status.HTTP_405_METHOD_NOT_ALLOWED},
                id="unauthorize-create-obj",
            ),
            pytest.param(
                'user',
                {'status_code': status.HTTP_405_METHOD_NOT_ALLOWED},
                id="user-create-obj",
            ),
            pytest.param(
                'admin',
                {'status_code': status.HTTP_405_METHOD_NOT_ALLOWED},
                id="admin-create-obj",
            ),
        ],
    )
    @pytest.mark.django_db()
    def test_create_tag(self, usertype, expectation):
        """Тестирование создания конкретного Тега.
        Через API недоступно никаким категориям пользователей."""
        tag = TagFactory.build()

        api_request = APIRequestFactory().post(
            '',
            {
                'slug': tag.slug,
                'name': tag.name,
                'color': tag.color,
            },
        )
        if usertype != 'unauthorize':
            user = UserFactory.create(is_superuser=(usertype == 'admin'))
            force_authenticate(request=api_request, user=user)
        obj_view = TagViewSet.as_view({'get': 'retrieve'})
        response = obj_view(api_request)
        assert response.status_code == expectation['status_code']

    @pytest.mark.parametrize(
        'usertype, expectation',
        [
            pytest.param(
                'unauthorize',
                {'status_code': status.HTTP_405_METHOD_NOT_ALLOWED},
                id="unauthorize-put-obj",
            ),
            pytest.param(
                'user',
                {'status_code': status.HTTP_405_METHOD_NOT_ALLOWED},
                id="user-put-obj",
            ),
            pytest.param(
                'admin',
                {'status_code': status.HTTP_405_METHOD_NOT_ALLOWED},
                id="admin-put-obj",
            ),
        ],
    )
    @pytest.mark.django_db()
    def test_put_tag(self, usertype, expectation):
        """Тестирование замены конкретного Тега.
        Через API недоступно никаким категориям пользователей."""
        old_tag = TagFactory.create()
        new_tag = TagFactory.build()

        api_request = APIRequestFactory().put(
            '',
            {
                'slug': new_tag.slug,
                'name': new_tag.name,
                'color': new_tag.color,
            },
        )
        if usertype != 'unauthorize':
            user = UserFactory.create(is_superuser=(usertype == 'admin'))
            force_authenticate(request=api_request, user=user)
        obj_view = TagViewSet.as_view({'get': 'retrieve'})
        response = obj_view(api_request, pk=old_tag.pk)
        assert response.status_code == expectation['status_code']

    @pytest.mark.parametrize(
        'usertype, expectation',
        [
            pytest.param(
                'unauthorize',
                {'status_code': status.HTTP_405_METHOD_NOT_ALLOWED},
                id="unauthorize-patch-obj",
            ),
            pytest.param(
                'user',
                {'status_code': status.HTTP_405_METHOD_NOT_ALLOWED},
                id="user-patch-obj",
            ),
            pytest.param(
                'admin',
                {'status_code': status.HTTP_405_METHOD_NOT_ALLOWED},
                id="admin-patch-obj",
            ),
        ],
    )
    @pytest.mark.django_db()
    def test_patch_tag(self, usertype, expectation):
        """Тестирование обновления отдельных полей конкретного Тега.
        Через API недоступно никаким категориям пользователей."""
        old_tag = TagFactory.create()
        new_tag = TagFactory.build()

        api_request = APIRequestFactory().patch(
            '',
            {
                'slug': new_tag.slug,
                'name': new_tag.name,
                'color': new_tag.color,
            },
        )
        if usertype != 'unauthorize':
            user = UserFactory.create(is_superuser=(usertype == 'admin'))
            force_authenticate(request=api_request, user=user)
        obj_view = TagViewSet.as_view({'get': 'retrieve'})
        response = obj_view(api_request, pk=old_tag.pk)
        assert response.status_code == expectation['status_code']

    @pytest.mark.parametrize(
        'usertype, expectation',
        [
            pytest.param(
                'unauthorize',
                {'status_code': status.HTTP_405_METHOD_NOT_ALLOWED},
                id="unauthorize-patch-obj",
            ),
            pytest.param(
                'user',
                {'status_code': status.HTTP_405_METHOD_NOT_ALLOWED},
                id="user-patch-obj",
            ),
            pytest.param(
                'admin',
                {'status_code': status.HTTP_405_METHOD_NOT_ALLOWED},
                id="admin-patch-obj",
            ),
        ],
    )
    @pytest.mark.django_db()
    def test_delete_tag(self, usertype, expectation):
        """Тестирование удаления конкретного Тега.
        Через API недоступно никаким категориям пользователей."""
        test_tag = TagFactory.create()

        api_request = APIRequestFactory().delete('')
        if usertype != 'unauthorize':
            user = UserFactory.create(is_superuser=(usertype == 'admin'))
            force_authenticate(request=api_request, user=user)
        obj_view = TagViewSet.as_view({'get': 'retrieve'})
        response = obj_view(api_request, pk=test_tag.pk)
        assert response.status_code == expectation['status_code']


class TestRecipeViewSet:
    """Тестирование вьюсета Рецептов."""

    ...


class TestIngredientViewSet:
    """Тестирование вьюсета Ингридиентов."""

    ...
