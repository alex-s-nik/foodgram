from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Пользователь системы."""

    # переопределение полей email, first_name и last_name для того, чтобы они стало обязательным
    # параметры полей те же, что и в AbstractUser, кроме blank=True
    email = models.EmailField(_("email address"))
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)

    favorites = models.ManyToManyField(
        to='recipes.Recipe', related_name='favorite_users', verbose_name='Избранное'
    )
    shopping_cart = models.ManyToManyField(
        to='recipes.Recipe', related_name='cart_users', verbose_name='Список покупок'
    )
    subscribers = models.ManyToManyField(
        to='self',
        related_name='subscribed',
        through='Subscriber',
        symmetrical=False,
        verbose_name='Подписчики',
    )

    REQUIRED_FIELDS = [
        'email',
        'first_name',
        'last_name'
    ]

    USERNAME_FIELD = 'username'

    @property
    def is_admin(self):
        return self.is_superuser

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Subscriber(models.Model):
    """Класс для создания M2M-отношения подписки пользователей."""

    author = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name='followers'
    )
    follower = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name='authors'
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                name='impossible_follow_self',
                check=~models.Q(author=models.F('follower')),
            ),
            models.UniqueConstraint(
                name='unique_follow',
                fields=(
                    'author',
                    'follower',
                ),
            ),
        ]
