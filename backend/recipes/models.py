from django.db import models


class Tag(models.Model):
    '''Тег для рецепта'''
    name = models.CharField(
        verbose_name='Название тега',
        max_length=32
    )
    color = models.CharField(
        verbose_name='Цвет ярлычка с тегом',
        max_length=7
    )
    slug = models.SlugField(
        verbose_name='Slug',
        unique=True
    )


class MeasurementUnit(models.Model):
    '''Единица измерения ингридиента'''
    name = models.CharField(
        verbose_name='Название единицы измерения',
        max_length=32,
        unique=True
    )


class Ingridient(models.Model):
    '''Ингридиент в рецепте'''
    name = models.CharField(
        verbose_name='Название ингридиента',
        max_length=64
    )
    measurement_unit = models.ForeignKey(
        to=MeasurementUnit,
        on_delete=models.CASCADE,
        related_name='ingridients',
        verbose_name='Единица измерения'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество'
    )


class Recipe(models.Model):
    '''Рецепт блюда'''
    author = ...
    name = ...
    image = ...
    text = ...
    ingridients = ...
    tags = ...
    cooking_time = ...
