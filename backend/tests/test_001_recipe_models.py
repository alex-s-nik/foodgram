import pytest

import factory
from faker import Faker

from django.db.utils import IntegrityError

from recipes.models import Ingredient, Recipe, Tag
from recipes.factories import IngredientFactory, RecipeFactory, TagFactory
from users.factories import UserFactory


class TestTag:
    """Тестирование модели Тэг."""

    faked_data = Faker()
    tag_name = faked_data.word()
    tag_color = faked_data.color()
    tag_slug = faked_data.slug()

    @pytest.mark.django_db()
    def test_tag_model(self):
        """Создание экземпляра."""

        tags_count_before_start_test = Tag.objects.count()
        test_tag = TagFactory.create(name=self.tag_name, color=self.tag_color, slug=self.tag_slug)
        tags_count_after_test_completed = Tag.objects.count()

        assert tags_count_before_start_test == tags_count_after_test_completed - 1

        assert test_tag.name == self.tag_name
        assert test_tag.color == self.tag_color
        assert test_tag.slug == self.tag_slug

    @pytest.mark.parametrize(
        'name, color, slug',
        [
            pytest.param(
                tag_name,
                factory.Faker('color'),
                factory.Faker('slug'),
                id='non-unique-name',
                marks=[pytest.mark.skip()],
            ),
            pytest.param(
                factory.Faker('word'),
                tag_color,
                factory.Faker('slug'),
                id='non-unique-color',
                marks=[pytest.mark.skip()],
            ),
            pytest.param(
                factory.Faker('word'),
                factory.Faker('color'),
                tag_slug,
                id='non-unique-slug',
                marks=[pytest.mark.skip()],
            ),
        ],
    )
    @pytest.mark.django_db()
    def test_unique_fields(self, name, color, slug):
        """Тестирование уникальности полей."""
        Tag.objects.create(name=self.tag_name, color=self.tag_color, slug=self.tag_slug)
        with pytest.raises(IntegrityError):
            Tag.objects.create(name=name, color=color, slug=slug)


class TestIngredient:
    """Тестирование модели Ингдидиент."""

    faked_data = Faker()

    ingredient_name = faked_data.word()
    ingredient_measurement_unit = faked_data.text(max_nb_chars=7)

    @pytest.mark.django_db()
    def test_ingredient_model(self):
        """Создание экземпляра."""
        ingredient_count_before_start_test = Ingredient.objects.count()
        test_ingredient = IngredientFactory.create(
            name=self.ingredient_name, measurement_unit=self.ingredient_measurement_unit
        )
        ingredient_count_after_test_completed = Ingredient.objects.count()

        assert ingredient_count_before_start_test == ingredient_count_after_test_completed - 1

        assert test_ingredient.name == self.ingredient_name
        assert test_ingredient.measurement_unit == self.ingredient_measurement_unit


class TestRecipe:
    """Тестирование модели Рецепт."""

    RECIPE_COUNT_TAGS = 4

    faked_data = Faker()

    recipe_name = faked_data.word()
    recipe_text = faked_data.text()
    recipe_cooking_time = faked_data.random_int(min=1, max=180)

    @pytest.mark.django_db()
    def test_recipe_model(self, batch_of_tags, one_user):
        """Создание экземпляра."""
        recipes_before_start_test = Recipe.objects.count()
        test_recipe = RecipeFactory.create(
            author=one_user,
            name=self.recipe_name,
            text=self.recipe_text,
            cooking_time=self.recipe_cooking_time,
            tags=batch_of_tags(self.RECIPE_COUNT_TAGS),
        )

        recipe_count_after_test_completed = Recipe.objects.count()

        assert recipes_before_start_test == recipe_count_after_test_completed - 1

        assert test_recipe.name == self.recipe_name
        assert test_recipe.text == self.recipe_text
        assert test_recipe.cooking_time == self.recipe_cooking_time
        assert test_recipe.author == one_user
        assert test_recipe.tags.count() == self.RECIPE_COUNT_TAGS
