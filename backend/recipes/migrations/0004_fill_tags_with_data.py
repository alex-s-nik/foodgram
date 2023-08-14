# Generated by Django 4.1.3 on 2022-12-20 08:51

from django.db import migrations


def load_initial_tags_data(apps, schema_editor):
    tags = [
        {'name': 'Завтрак', 'color': '#cc0000', 'slug': 'breakfast'},
        {'name': 'Обед', 'color': '#00cc00', 'slug': 'lunch'},
        {'name': 'Ужин', 'color': '#0000cc', 'slug': 'dinner'},
    ]

    Tag = apps.get_model('recipes', 'Tag')

    Tag.objects.bulk_create([Tag(**tag) for tag in tags])


class Migration(migrations.Migration):
    dependencies = [
        ('recipes', '0003_fill_ingridients_with_data'),
    ]

    operations = [migrations.RunPython(load_initial_tags_data)]
