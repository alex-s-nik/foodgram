from contextlib import nullcontext as does_not_raise

import pytest

from faker import Faker
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model

User = get_user_model()


class TestUser:
    faked_data = Faker()

    @pytest.mark.django_db()
    @pytest.mark.parametrize(
        'credentials, expectation',
        [
            pytest.param(
                {
                    'username': faked_data.user_name(),
                    'first_name': faked_data.first_name(),
                    'last_name': faked_data.last_name(),
                    'email': faked_data.email(),
                    'password': faked_data.password(),
                },
                does_not_raise(),
                id='all required fields',
            ),
            pytest.param(
                {
                    'first_name': faked_data.first_name(),
                    'last_name': faked_data.last_name(),
                    'email': faked_data.email(),
                    'password': faked_data.password(),
                },
                pytest.raises(TypeError),
                id='without username',
                marks=[pytest.mark.skip()],
            ),
            pytest.param(
                {
                    'username': faked_data.user_name(),
                    'last_name': faked_data.last_name(),
                    'email': faked_data.email(),
                    'password': faked_data.password(),
                },
                pytest.raises(TypeError),
                id='without first_name',
                marks=[pytest.mark.skip()],
            ),
            pytest.param(
                {
                    'username': faked_data.user_name(),
                    'first_name': faked_data.first_name(),
                    'email': faked_data.email(),
                    'password': faked_data.password(),
                },
                pytest.raises(TypeError),
                id='without last_name',
                marks=[pytest.mark.skip()],
            ),
            pytest.param(
                {
                    'username': faked_data.user_name(),
                    'first_name': faked_data.first_name(),
                    'last_name': faked_data.last_name(),
                    'password': faked_data.password(),
                },
                pytest.raises(TypeError),
                id='without email',
                marks=[pytest.mark.skip()],
            ),
            pytest.param(
                {
                    'username': faked_data.user_name(),
                    'first_name': faked_data.first_name(),
                    'last_name': faked_data.last_name(),
                    'email': faked_data.email(),
                },
                pytest.raises(TypeError),
                id='without password',
                marks=[pytest.mark.skip()],
            ),
        ],
    )
    def test_required_fields_for_registration_user(self, credentials, expectation):
        with expectation:
            User.objects.create_user(**credentials)


class TestSubscribers:
    @pytest.mark.django_db()
    def test_subcribers(self, batch_of_users):
        author, follower = batch_of_users(2)
        author.subscribers.add(follower)
        assert len(author.subscribers.all()) == 1

    @pytest.mark.django_db()
    def test_self_subscribing(self, one_user):
        author = one_user

        with pytest.raises(IntegrityError):
            author.subscribers.add(author)
