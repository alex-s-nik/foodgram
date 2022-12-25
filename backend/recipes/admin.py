from django.contrib import admin

from .models import AmountIngredients, Ingredient, Recipe, Tag


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'count_field',)
    search_fields = ('name',)
    filter_horizontal = ('tags',)
    list_filter = ('tags', 'author',)

    @admin.display(description='Добавлены в избранное')
    def count_field(self, obj):
        return obj.favorite_users.count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)


admin.site.register(AmountIngredients)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
