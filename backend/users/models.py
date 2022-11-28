from django.contrib.auth.models import AbstractUser
from django.db import models
from recipes.models import Recipe


class User(AbstractUser):
    '''Пользователь системы'''
    favorites = models.ManyToManyField(
        to=Recipe,
        related_name='users',
        verbose_name='Избранное'
    )
    shopping_cart = models.ManyToManyField(
        to=Recipe,
        related_name='users',
        verbose_name='Список покупок'
    )
    
    @property
    def is_admin(self):
        return self.is_superuser


class Follow(models.Model):
    '''Подписка на пользователя'''
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.CheckConstraint(
                name='impossible_follow_self',
                check=~models.Q(user=models.F('author')),
            ),
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='selffollow'
            )
        ]
