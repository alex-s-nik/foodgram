import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


class Test00UserRegistration:
    user_registration_url = '/api/users/'

    @pytest.mark.django_db(transaction=True)
    def test_00_nodata_signup(self, client):
        request_type = 'POST'
        response = client.post(self.user_registration_url)

        assert (
            response.status_code != 404
        ), f'Страница `{self.user_registration_url}` не найдена, проверьте этот адрес в *urls.py*'
        code = 400
        assert response.status_code == code, (
            f'Проверьте, что при {request_type} запросе `{self.user_registration_url}` без параметров '
            f'не создается пользователь и возвращается статус {code}'
        )
        response_json = response.json()
        empty_fields = ['email', 'username', 'first_name', 'last_name', 'password']
        for field in empty_fields:
            assert field in response_json.keys() and isinstance(
                response_json[field], list
            ), (
                f'Проверьте, что при {request_type} запросе `{self.user_registration_url}` без параметров '
                f'в ответе есть сообщение о том, какие поля заполнены неправильно'
            )

    @pytest.mark.django_db(transaction=True)
    def test_00_not_all_data_signup(self, client):
        request_data = {
            'username': 'testusername',
            'email': 'test@email.fake',
            'first_name': 'Тестовоеимя',
            'last_name': 'Тестоваяфамилия',
            'password': 'Qwerty123',
        }

        request_type = 'POST'
        response = client.post(self.user_registration_url)

        assert (
            response.status_code != 404
        ), f'Страница `{self.user_registration_url}` не найдена, проверьте этот адрес в *urls.py*'

        code = 400

        for field in request_data:
            temp_data = request_data.copy()
            del temp_data[field]

            response = client.post(self.user_registration_url, data=temp_data)

            assert response.status_code == code, (
                f'Проверьте, что при {request_type} запросе `{self.user_registration_url}` без {field} '
                f'нельзя создать пользователя и возвращается статус {code}'
            )

    @pytest.mark.django_db(transaction=True)
    def test_00_user_signup(self, client):
        valid_data = {
            'username': 'testusername6',
            'email': 'test6@email.fake',
            'first_name': 'Тестовоеимя6',
            'last_name': 'Тестоваяфамилия6',
            'password': 'Qwerty1236',
        }

        request_type = 'POST'

        response = client.post(self.user_registration_url, data=valid_data)

        assert (
            response.status_code != 404
        ), f'Страница `{self.user_registration_url}` не найдена, проверьте этот адрес в *urls.py*'

        code = 201
        print(response.json())
        assert response.status_code == code, (
            f'Проверьте, что при {request_type} запросе `{self.user_registration_url}` с валидными данными '
            f'создается пользователь и возвращается статус {code}'
        )

        assert all(
            field in response.json() and valid_data[field] == response.json()[field]
            for field in valid_data
            if field != 'password'
        ), (
            f'Проверьте, что при {request_type} запросе `{self.user_registration_url}` с валидными данными '
            f'создается пользователь и возвращается корректные данные пользователя {code}'
        )

        new_user = User.objects.filter(email=valid_data['email'])
        assert new_user.exists(), (
            f'Проверьте, что при {request_type} запросе `{self.user_registration_url}` с валидными данными '
            f'создается пользователь и он доступен в БД'
        )

    @pytest.mark.django_db(transaction=True)
    def test_00_unique_email_and_username(self, client):
        username1 = 'testusername1'
        username2 = 'testusername2'
        email1 = 'test1@email.fake'
        email2 = 'test2@email.fake'

        valid_data = {
            'username': username1,
            'email': email1,
            'first_name': 'Тестовоеимя',
            'last_name': 'Тестоваяфамилия',
            'password': 'Qwerty123',
        }

        request_type = 'POST'

        response = client.post(self.user_registration_url, data=valid_data)

        valid_data['email'] = email2

        response = client.post(self.user_registration_url, data=valid_data)

        code = 400
        assert response.status_code == code, (
            f'Проверьте, что при {request_type} запросе `{self.user_registration_url}` нельзя создать '
            f'пользователя, username которого уже зарегистрирован и возвращается статус {code}'
        )

        valid_data['email'] = email1
        valid_data['username'] = username2
        response = client.post(self.user_registration_url, data=valid_data)

        assert response.status_code == code, (
            f'Проверьте, что при {request_type} запросе `{self.user_registration_url}` нельзя создать '
            f'пользователя, email которого уже зарегистрирован и возвращается статус {code}'
        )
