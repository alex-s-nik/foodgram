from django.db import models


class Tag(models.Model):
    name = ...
    color = ...
    slug = ...


class MeasurementUnit(models.Model):
    name = ...


class Ingridient(models.Model):
    name = ...
    measurement_unit = ...
    amount = ...


class Recipe(models.Model):
    author = ...
    name = ...
    image = ...
    text = ...
    ingridients = ...
    tags = ...
    cooking_time = ...
