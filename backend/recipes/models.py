from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Тег для рецепта"""

    name = models.CharField(verbose_name='Название', max_length=32, unique=True)
    color = models.CharField(verbose_name='Цвет ярлычка', max_length=7, unique=True)
    slug = models.SlugField(verbose_name='Slug', unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f'{self.name}'


class Ingredient(models.Model):
    """Ингридиент в рецепте"""

    name = models.CharField(verbose_name='Название', max_length=64)
    measurement_unit = models.CharField(max_length=32, verbose_name='Единица измерения')

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'


class AmountIngredients(models.Model):
    """Количество ингридиентов"""

    recipe = models.ForeignKey(
        to='Recipe',
        on_delete=models.CASCADE,
        related_name='ingredients_amount',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        to=Ingredient,
        on_delete=models.CASCADE,
        related_name='recipes_amount',
        verbose_name='Ингридиент',
    )
    amount = models.PositiveSmallIntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Количество ингридиентов'
        verbose_name_plural = 'Количество ингридиентов'

    def __str__(self):
        return f'{self.recipe.name}: {self.ingredient.name}' f' - {self.amount}, {self.ingredient.measurement_unit}'


class Recipe(models.Model):
    """Рецепт блюда"""

    author = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='recipes', verbose_name='Автор')
    name = models.CharField(max_length=200, verbose_name='Название')
    image = models.ImageField(upload_to='recipes/', verbose_name='Фото')
    text = models.TextField(max_length=1024, verbose_name='Описание')
    ingredients = models.ManyToManyField(
        to=Ingredient,
        related_name='recipes',
        verbose_name='Ингридиенты',
        through=AmountIngredients,
    )
    tags = models.ManyToManyField(to=Tag, related_name='recipes', verbose_name='Теги')
    cooking_time = models.PositiveSmallIntegerField(verbose_name='Время приготовления, мин')
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации рецепта')

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
