import pytest


@pytest.fixture
def user_superuser(django_user_model):
    return django_user_model.objects.create_superuser(
        username='TestSuperuser', email='testsuperuser@foodgram.fake', password='1234567'
    )

@pytest.fixture
def token_superuser(user_superuser):
    from rest_framework.authtoken.models import Token
    token = Token.objects.create(user=user_superuser)

    return {
        'auth_token': str(token)
    }

@pytest.fixture
def first_user(django_user_model):
    return django_user_model.objects.create_user(
        username='TestUser', 
        password='1234567',
        first_name = 'Test',
        last_name = 'user',
        email = 'testuser@foodgram.fake'
    )

@pytest.fixture
def second_user(django_user_model):
        return django_user_model.objects.create_user(
        username='TestUser2', 
        password='1234567',
        first_name = 'Test2',
        last_name = 'user',
        email = 'testuser2@foodgram.fake'
    )

@pytest.fixture
def third_user(django_user_model):
    return django_user_model.objects.create_user(
        username='TestUser3', 
        password='1234567',
        first_name = 'Test3',
        last_name = 'user',
        email = 'testuser3@foodgram.fake'
    )

@pytest.fixture
def token_first_user(first_user):
    from rest_framework.authtoken.models import Token
    token, _ = Token.objects.get_or_create(user=first_user)
    return token

@pytest.fixture
def token_second_user(second_user):
    from rest_framework.authtoken.models import Token
    token, _ = Token.objects.get_or_create(user=second_user)
    return token

@pytest.fixture
def token_third_user(third_user):
    from rest_framework.authtoken.models import Token
    token, _ = Token.objects.get_or_create(user=third_user)
    return token


@pytest.fixture
def first_user_client(token_first_user):
    from rest_framework.test import APIClient

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token_first_user}')
    return client

@pytest.fixture
def second_user_client(token_second_user):
    from rest_framework.test import APIClient

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token_second_user}')
    return client

@pytest.fixture
def third_user_client(token_third_user):
    from rest_framework.test import APIClient

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token_third_user}')
    return client
