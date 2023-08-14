import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


class Test03Subscriptioins:
    subcribe_url = '/api/users/{id}/subscribe/'

    @pytest.mark.django_db(transaction=True)
    def test_03_subscribe_to_user(
        self, client, first_user_client, first_user, second_user
    ):
        # подписка неавторизованного пользователя

        url = self.subcribe_url.format(id=second_user.id)
        response = client.post(url)

        assert (
            response.status_code != 404
        ), f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'

        code = 401
        assert response.status_code == code, (
            f'Подписка неавторизованного пользователя должна быть невозможна и '
            f'возвращать статус {code}'
        )

        # подписка на самого себя
        response = first_user_client.post(self.subcribe_url.format(id=first_user.id))

        code = 400
        assert response.status_code == code, (
            f'Подписка на себя должна быть невозможна и ' f'возвращать статус {code}'
        )

        # подписка на несуществующего пользователя

        # поиск несуществующего id
        invalid_user_id = 1
        while User.objects.filter(id=invalid_user_id).exists():
            invalid_user_id += 1

        response = first_user_client.post(self.subcribe_url.format(id=invalid_user_id))

        code = 404
        assert response.status_code == code, (
            f'Подписка на несуществующего пользователя должна быть невозможна и '
            f'возвращать статус {code}'
        )

        # success case
        response = first_user_client.post(self.subcribe_url.format(id=second_user.id))

        code = 201
        assert response.status_code == code, (
            f'С валидными данными подписка должна осуществляться'
            f' и возвращать статус {code}'
        )

        # повторная подписка
        response = first_user_client.post(self.subcribe_url.format(id=second_user.id))

        code = 400
        assert response.status_code == code, (
            f'Повторная подписка на пользователя должна быть невозможна и '
            f'возвращать статус {code}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_03_unsubscribing(self, client, first_user_client, second_user):
        # отмена подписки неавторизованным пользователем
        url = self.subcribe_url.format(id=second_user.id)
        response = client.delete(url)

        assert (
            response.status_code != 404
        ), f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'

        code = 401
        assert response.status_code == code, (
            f'Отмена подписки неавторизованного пользователя должна быть невозможна и '
            f'возвращать статус {code}'
        )

        # отмена подписки на несуществующего пользователя
        invalid_user_id = 1
        while User.objects.filter(id=invalid_user_id).exists():
            invalid_user_id += 1

        response = first_user_client.delete(
            self.subcribe_url.format(id=invalid_user_id)
        )

        code = 404
        assert response.status_code == code, (
            f'Отмена подписки на несуществующего пользователя должна быть невозможна и '
            f'возвращать статус {code}'
        )

        # success case
        first_user_client.post(self.subcribe_url.format(id=second_user.id))
        response = first_user_client.delete(self.subcribe_url.format(id=second_user.id))

        code = 204
        assert response.status_code == code, (
            f'С валидными данными отмена подписки должна осуществляться'
            f' и возвращать статус {code}'
        )

        # отмена подписки на пользователя, на которого нет подписки
        response = first_user_client.delete(self.subcribe_url.format(id=second_user.id))

        code = 400
        assert response.status_code == code, (
            f'Отмена подписки на пользователя, на которого подписки нет, '
            f'должна быть невозможна и возвращать статус {code}'
        )
