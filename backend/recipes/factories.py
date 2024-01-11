import factory


from users.factories import UserFactory
from .models import Ingredient, Recipe, Tag


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


class RecipeFactory(factory.django.DjangoModelFactory):
    """Фабрика Рецептов."""

    class Meta:
        model = Recipe

    MIN_COOKING_TIME = 10
    MAX_COOKING_TIME = 180

    author = factory.SubFactory(UserFactory)
    name = factory.Faker('word')
    image = factory.Faker('image', size=(1, 1))
    text = factory.Faker('text')
    cooking_time = factory.Faker('random_int', min=MIN_COOKING_TIME, max=MAX_COOKING_TIME)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        self.tags.add(*extracted)

    @factory.post_generation
    def ingredients(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        self.ingredients.add(*extracted)


class AmountIngredientsFactory(factory.django.DjangoModelFactory):
    """Фабрика Количества Ингридиентов."""

    MIN_AMOUNT = 1
    MAX_AMOUNT = 1000

    recipe = factory.SubFactory(RecipeFactory)
    ingredient = factory.SubFactory(IngredientFactory)
    amount = factory.Faker('random_int', min=MIN_AMOUNT, max=MAX_AMOUNT)
