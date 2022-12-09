from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    '''Тег для рецепта'''
    name = models.CharField(
        verbose_name='Название',
        max_length=32
    )
    color = models.CharField(
        verbose_name='Цвет ярлычка',
        max_length=7
    )
    slug = models.SlugField(
        verbose_name='Slug',
        unique=True
    )


class MeasurementUnit(models.Model):
    '''Единица измерения ингридиента'''
    name = models.CharField(
        verbose_name='Название',
        max_length=32,
        unique=True
    )


class Ingridient(models.Model):
    '''Ингридиент в рецепте'''
    name = models.CharField(
        verbose_name='Название',
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
    author = models.ForeignKey(
        to='users.User',
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    image = models.ImageField(
        upload_to='img/',
        verbose_name='Фото'
    )
    text = models.TextField(
        max_length=1024,
        verbose_name='Описание'
    )
    ingridients = models.ManyToManyField(
        to=Ingridient,
        related_name='recipes',
        verbose_name='Ингридиенты'
    )
    tags = models.ManyToManyField(
        to=Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления, мин'
    )
