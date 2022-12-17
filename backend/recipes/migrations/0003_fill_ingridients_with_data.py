# Generated by Django 4.1.3 on 2022-12-15 19:18

import json
from django.conf import settings
from django.db import migrations

def load_initial_ingredient_data(apps, schema_editor):

    data_file = (
        settings.BASE_DIR.parent / settings.RECIPES['ingredients_data_file']
    )

    Ingrigient = apps.get_model('recipes', 'Ingredient')

    with open(data_file, encoding='utf-8') as ingredients_file:
        ingredients_list = json.load(ingredients_file)

        ingredients = [
            Ingrigient(
                name=ingredient['name'],
                measurement_unit = ingredient['measurement_unit']
            )
            for ingredient in ingredients_list
        ]

        Ingrigient.objects.bulk_create(ingredients)


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.RunPython(load_initial_ingredient_data)
    ]
