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
    name = ...


class Ingridient(models.Model):
    '''Ингридиент в рецепте'''
    name = ...
    measurement_unit = ...
    amount = ...


class Recipe(models.Model):
    '''Рецепт блюда'''
    author = ...
    name = ...
    image = ...
    text = ...
    ingridients = ...
    tags = ...
    cooking_time = ...
