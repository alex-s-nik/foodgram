import random

import factory


from users.factories import UserFactory
from .models import AmountIngredients, Ingredient, Recipe, Tag


class TagFactory(factory.django.DjangoModelFactory):
    """Фабрика Тегов."""

    class Meta:
        model = Tag

    name = factory.Faker('word')
    color = factory.Faker('color')
    slug = factory.Faker('slug')


class IngredientFactory(factory.django.DjangoModelFactory):
    """Фабрика Ингридиентов."""

    class Meta:
        model = Ingredient

    name = factory.Faker('word')
    measurement_unit = factory.Faker('text', max_nb_chars=7)


# константы для RecipeFactory
MIN_COOKING_TIME = 10
MAX_COOKING_TIME = 180


class RecipeFactory(factory.django.DjangoModelFactory):
    """Фабрика Рецептов."""

    class Meta:
        model = Recipe

    author = factory.SubFactory(UserFactory)
    name = factory.Faker('word')
    image = factory.django.ImageField()
    text = factory.Faker('text')
    cooking_time = factory.Faker('random_int', min=MIN_COOKING_TIME, max=MAX_COOKING_TIME)

    ingredients = factory.RelatedFactoryList(
        'recipes.factories.AmountIngredientsFactory',
        factory_related_name='recipe',
        size=random.randint(1, 20),
    )

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for tag in extracted:
                self.tags.add(tag)
        else:
            for tag in TagFactory.create_batch(4):
                self.tags.add(tag)


# константы для AmountIngredientsFactory
MIN_AMOUNT = 1
MAX_AMOUNT = 1000


class AmountIngredientsFactory(factory.django.DjangoModelFactory):
    """Фабрика Количества Ингридиентов."""

    class Meta:
        model = AmountIngredients

    recipe = factory.SubFactory(RecipeFactory)
    ingredient = factory.SubFactory(IngredientFactory)
    amount = factory.Faker('random_int', min=MIN_AMOUNT, max=MAX_AMOUNT)
