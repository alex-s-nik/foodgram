import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

class Test01Tokens:
    token_login_url = '/api/auth/token/login/'
    token_logout_url = '/api/auth/token/logout/'

    @pytest.mark.django_db(transaction=True)
    def test_01_get_token(self, client, first_user):
        data = {
            'email': first_user.email,
            'password': '1234567'
        }

        request_type = 'POST'

        response = client.post(self.token_login_url, data=data)

        assert response.status_code != 404, (
            f'Страница `{self.token_login_url}` не найдена, проверьте этот адрес в *urls.py*'
        )


        code = 200
        assert response.status_code == code, (
            f'Проверьте, что при {request_type} запросе `{self.token_login_url}` без параметров '
            f'возвращается статус {code}'
        )

        assert 'auth_token' in response.json(), (
            f'Проверьте, что при {request_type} запросе `{self.token_login_url}` без параметров '
            f'возвращается токен'
        )

    @pytest.mark.django_db(transaction=True)
    def test_01_del_token(self, client, first_user_client):

        request_type = 'POST'

        response = first_user_client.post(self.token_logout_url)

        assert response.status_code != 404, (
            f'Страница `{self.token_logout_url}` не найдена, проверьте этот адрес в *urls.py*'
        )

        success_code = 204
        assert response.status_code == success_code, (
            f'Проверьте, что при {request_type} запросе `{self.token_logout_url}` с токеном '
            f'возвращается статус {success_code}'
        )


        response = client.post(self.token_logout_url)

        fault_code = 401
        assert response.status_code == fault_code, (
            f'Проверьте, что при {request_type} запросе `{self.token_logout_url}` без токена '
            f'возвращается статус {fault_code}'
        )
