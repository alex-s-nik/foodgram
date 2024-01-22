from contextlib import nullcontext as does_not_raise

import pytest

from faker import Faker
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model

User = get_user_model()


class TestUser:
    faked_data = Faker()

    @pytest.mark.django_db()
    def test_user_model(self):
        user_data = {
            'username': self.faked_data.user_name(),
            'first_name': self.faked_data.first_name(),
            'last_name': self.faked_data.last_name(),
            'email': self.faked_data.email(),
            'password': self.faked_data.password(),
        }
        users_before_create_user = User.objects.count()
        test_user = User.objects.create(**user_data)
        user_after_create_user = User.objects.count()

        assert user_after_create_user == users_before_create_user + 1

        assert test_user.username == user_data['username']
        assert test_user.first_name == user_data['first_name']
        assert test_user.last_name == user_data['last_name']
        assert test_user.email == user_data['email']


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
