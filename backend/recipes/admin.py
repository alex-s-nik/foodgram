from django.contrib import admin

from .models import Ingridient, MeasurementUnit, Recipe, Tag

admin.site.register(Ingridient)
admin.site.register(MeasurementUnit)
admin.site.register(Recipe)
admin.site.register(Tag)
