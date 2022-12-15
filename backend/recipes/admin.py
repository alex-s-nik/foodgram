from django.contrib import admin

from .models import AmountIngridients, Ingridient, Recipe, Tag

class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'count_field',)
    list_filter = ('author', 'name', 'tags',)

    @admin.display(description='Добавлены в избранное')
    def count_field(self, obj):
        return obj.favorite_users.count()


admin.site.register(AmountIngridients)
admin.site.register(Ingridient)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
