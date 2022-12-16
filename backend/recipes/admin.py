from django.contrib import admin

from .models import AmountIngridients, Ingridient, Recipe, Tag


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'count_field',)
    list_filter = ('author', 'name', 'tags',)

    @admin.display(description='Добавлены в избранное')
    def count_field(self, obj):
        return obj.favorite_users.count()


class IngridientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)


admin.site.register(AmountIngridients)
admin.site.register(Ingridient, IngridientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
