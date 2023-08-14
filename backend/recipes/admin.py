from django.contrib import admin

from .models import AmountIngredients, Ingredient, Recipe, Tag


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'count_field', 'recipe_tags')
    search_fields = (
        'name',
        'author__username',
        'tags__name',
    )
    list_filter = (
        'tags',
        'author',
    )

    @admin.display(description='Тэги')
    def recipe_tags(self, obj):
        return ', '.join(tag.name for tag in obj.tags.all())

    @admin.display(description='Добавлены в избранное')
    def count_field(self, obj):
        return obj.favorite_users.count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)


admin.site.register(AmountIngredients)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
