from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    '''Пользователь системы'''
    favorites = models.ManyToManyField(
        to='recipes.Recipe',
        related_name='favorite_users',
        verbose_name='Избранное'
    )
    shopping_cart = models.ManyToManyField(
        to='recipes.Recipe',
        related_name='cart_users',
        verbose_name='Список покупок'
    )
    subscribers = models.ManyToManyField(
        to='self',
        related_name='subscribed',
        through='Subscriber',
        symmetrical=False,
        verbose_name='Подписчики'
    )

    @property
    def is_admin(self):
        return self.is_superuser


class Subscriber(models.Model):
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='describers'
    )
    describer = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='authors'
    )
    class Meta:
        constraints = [
            models.CheckConstraint(
                name='impossible_follow_self',
                check=models.Q(author=models.F('describer'))
            )
        ]

