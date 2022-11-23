from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    '''Пользователь системы'''
    favorites = ...
    shopping_cart = ...


class Follow(models.Model):
    '''Подписка на пользователя'''
    user = ...
    author = ...
