from django.contrib import admin

from .models import Ingridient, Recipe, Tag

admin.site.register(Ingridient)
admin.site.register(Recipe)
admin.site.register(Tag)
