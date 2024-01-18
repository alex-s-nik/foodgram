import base64

from faker import Faker
import pytest

from api.serializers import AmountIngredientsSerializer, IngredientSerializer, RecipeSerializer, TagSerializer
from recipes.factories import IngredientFactory, RecipeFactory, TagFactory


class TestSerializers:
    """Тестирование сериалайзеров."""

    faked_data = Faker()

    def test_user_serializer(self):
        """Сериалайзер Пользователя."""
        ...

    def test_user_create_serializer(self):
        """Сериалайзер создания Пользователя."""
        ...

    @pytest.mark.django_db()
    def test_tag_serializer(self):
        """Сериалайзер Тэга."""
        # здесь не берем фикстуру simple_tag в виду того, что
        # объект уже будет в БД, и, при валидации сериалайзера
        # с полями как у существующего объекта , сериалайзер не пройдет
        # валидацию по причине уникальности полей создаваемого сериалайзером
        # объекта
        tag = TagFactory.build()
        tag_data = {'name': tag.name, 'color': tag.color, 'slug': tag.slug}

        tag_serializer = TagSerializer(tag)
        tag_serializer_data = tag_serializer.data
        del tag_serializer_data['id']

        assert tag_data == tag_serializer_data

        tag_serializer_from_data = TagSerializer(data=tag_data)
        assert tag_serializer_from_data.is_valid()
        assert tag_serializer_from_data.validated_data == tag_data

    @pytest.mark.django_db()
    def test_ingredient_serializer(self, simple_ingredient):
        """Сериалайзер Ингридиента."""
        ingredient_data = {'name': simple_ingredient.name, 'measurement_unit': simple_ingredient.measurement_unit}

        ingredient_serializer = IngredientSerializer(simple_ingredient)
        ingredient_serializer_data = ingredient_serializer.data
        del ingredient_serializer_data['id']

        assert ingredient_data == ingredient_serializer_data

        ingredient_serializer_from_data = IngredientSerializer(data=ingredient_data)
        assert ingredient_serializer_from_data.is_valid()
        assert ingredient_serializer_from_data.validated_data == ingredient_data

    def test_amount_ingredient_serializer(self):
        """Сериалайзер Количества ингридиента."""
        ...

    @pytest.mark.django_db()
    def test_recipe_serializer(self, simple_recipe):
        """Сериалайзер Рецепта."""
        recipe = simple_recipe

        recipe_data = {
            'id': recipe.id,
            'tags': [TagSerializer(tag).data for tag in recipe.tags.all()],
            'author': {
                'id': recipe.author.id,
                'email': recipe.author.email,
                'username': recipe.author.username,
                'first_name': recipe.author.first_name,
                'last_name': recipe.author.last_name,
                'is_subscribed': False,
            },
            'ingredients': [
                AmountIngredientsSerializer(ingredient).data for ingredient in recipe.ingredients_amount.all()
            ],
            'is_favorited': False,
            'is_in_shopping_cart': False,
            'name': recipe.name,
            'image': recipe.image.url,
            'text': recipe.text,
            'cooking_time': recipe.cooking_time,
        }
        recipe_serializer = RecipeSerializer(recipe)
        recipe_serializer_data = recipe_serializer.data

        assert recipe_serializer_data == recipe_data

        recipe_ingredients = IngredientFactory.create_batch(10)  # take randint ingredients
        recipe_tags = TagFactory.create_batch(3)  # take randint ingredients
        recipe_image_width = 100
        recipe_image_height = 100
        recipe_image_format = 'PNG'
        recipe_image = self.faked_data.image(
            size=(recipe_image_width, recipe_image_height), image_format=recipe_image_format
        )
        recipe_image_decoded_to_b64 = base64.b64encode(recipe_image).decode('utf-8')
        recipe_image_decoded_str = f'data:image/{recipe_image_format};base64,{recipe_image_decoded_to_b64}'
        recipe_name = self.faked_data.word()
        recipe_text = self.faked_data.text()
        recipe_cooking_time = self.faked_data.random_int(1, 180)

        recipe_data_for_create = {
            'ingredients': recipe_ingredients,
            'tags': recipe_tags,
            'image': recipe_image_decoded_str,
            'name': recipe_name,
            'text': recipe_text,
            'cooking_time': recipe_cooking_time,
        }

        recipe_serializer_from_data = RecipeSerializer(data=recipe_data_for_create)
        assert recipe_serializer_from_data.is_valid()
        assert recipe_serializer_from_data.validated_data == recipe_data_for_create
