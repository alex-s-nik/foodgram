import pytest

from users.factories import UserFactory


@pytest.fixture
def user_superuser(django_user_model):
    """Создание Суперпользователя."""
    return django_user_model.objects.create_superuser(
        username='TestSuperuser',
        email='testsuperuser@foodgram.fake',
        password='1234567',
    )


@pytest.fixture
def token_superuser(user_superuser):
    """Получение Токена для Суперпользователя."""
    from rest_framework.authtoken.models import Token

    token = Token.objects.create(user=user_superuser)

    return {'auth_token': str(token)}


@pytest.fixture
def first_user(django_user_model):
    """Создание Пользователя."""
    return django_user_model.objects.create_user(
        username='TestUser',
        password='1234567',
        first_name='Test',
        last_name='user',
        email='testuser@foodgram.fake',
    )


@pytest.fixture
def second_user(django_user_model):
    """Создание еще одного Пользователя."""
    return django_user_model.objects.create_user(
        username='TestUser2',
        password='1234567',
        first_name='Test2',
        last_name='user',
        email='testuser2@foodgram.fake',
    )


@pytest.fixture
def third_user(django_user_model):
    """Создание третьего Пользователя."""
    return django_user_model.objects.create_user(
        username='TestUser3',
        password='1234567',
        first_name='Test3',
        last_name='user',
        email='testuser3@foodgram.fake',
    )


@pytest.fixture
def token_first_user(first_user):
    """Получение Токена для Пользователя."""
    from rest_framework.authtoken.models import Token

    token, _ = Token.objects.get_or_create(user=first_user)
    return token


@pytest.fixture
def token_second_user(second_user):
    """Получение Токена для еще одного Пользователя."""
    from rest_framework.authtoken.models import Token

    token, _ = Token.objects.get_or_create(user=second_user)
    return token


@pytest.fixture
def token_third_user(third_user):
    """Получение Токена для третьего Пользователя."""
    from rest_framework.authtoken.models import Token

    token, _ = Token.objects.get_or_create(user=third_user)
    return token


@pytest.fixture
def first_user_client(token_first_user):
    """Получение клиента для Пользователя."""
    from rest_framework.test import APIClient

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token_first_user}')
    return client


@pytest.fixture
def second_user_client(token_second_user):
    """Получение клиента для еще одного Пользователя."""
    from rest_framework.test import APIClient

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token_second_user}')
    return client


@pytest.fixture
def third_user_client(token_third_user):
    """Получение клиента для третего Пользователя."""
    from rest_framework.test import APIClient

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token_third_user}')
    return client


@pytest.fixture
def batch_of_users():
    """Создание нескольких Пользователей.
    По умолчанию 10.
    """

    def _wrapper(count: int = 10):
        return UserFactory.create_batch(count)

    return _wrapper


@pytest.fixture
def one_user(batch_of_users):
    """Создание одного Пользователя."""
    return UserFactory.create()
