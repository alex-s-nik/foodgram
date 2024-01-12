from django.contrib.auth import get_user_model

import factory
from faker import Faker

User = get_user_model()

faked_data = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('user_name')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    password = factory.django.Password(faked_data.password())
