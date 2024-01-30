import base64
import hashlib

from faker import Faker
import pytest

from api.serializers import (
    AmountIngredientsSerializer,
    IngredientSerializer,
    RecipeResponseSerializer,
    RecipeSerializer,
    TagSerializer,
    UserCreateSerializer,
)
from recipes.factories import IngredientFactory, TagFactory
from users.factories import UserFactory


class TestSerializers:
    """Тестирование сериалайзеров."""

    faked_data = Faker()

    def test_user_serializer(self):
        """Сериалайзер Пользователя."""
        ...

    @pytest.mark.parametrize(
        'credentials, expectation, error',
        [
            pytest.param(
                {
                    'username': faked_data.user_name(),
                    'first_name': faked_data.first_name(),
                    'last_name': faked_data.last_name(),
                    'email': faked_data.email(),
                    'password': faked_data.password(),
                },
                True,
                None,
                id='all required fields',
            ),
            pytest.param(
                {
                    'first_name': faked_data.first_name(),
                    'last_name': faked_data.last_name(),
                    'email': faked_data.email(),
                    'password': faked_data.password(),
                },
                False,
                'username',
                id='without username',
            ),
            pytest.param(
                {
                    'username': faked_data.user_name(),
                    'last_name': faked_data.last_name(),
                    'email': faked_data.email(),
                    'password': faked_data.password(),
                },
                False,
                'first_name',
                id='without first_name',
            ),
            pytest.param(
                {
                    'username': faked_data.user_name(),
                    'first_name': faked_data.first_name(),
                    'email': faked_data.email(),
                    'password': faked_data.password(),
                },
                False,
                'last_name',
                id='without last_name',
            ),
            pytest.param(
                {
                    'username': faked_data.user_name(),
                    'first_name': faked_data.first_name(),
                    'last_name': faked_data.last_name(),
                    'password': faked_data.password(),
                },
                False,
                'email',
                id='without email',
            ),
            pytest.param(
                {
                    'username': faked_data.user_name(),
                    'first_name': faked_data.first_name(),
                    'last_name': faked_data.last_name(),
                    'email': faked_data.email(),
                },
                False,
                'password',
                id='without password',
            ),
        ],
    )
    @pytest.mark.django_db()
    def test_required_fields_for_registration_user(self, credentials, expectation, error):
        user_serializer = UserCreateSerializer(data=credentials)
        assert user_serializer.is_valid() == expectation
        if not expectation:
            assert error in user_serializer.errors

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


class TestRecipeSerializer:
    """Тестирование сериалайзеров Рецепта."""

    faked_data = Faker()

    @pytest.mark.django_db()
    def test_recipe_respone_serializer(self, simple_recipe):
        """Сериалайзер Рецепта для GET-ответов."""
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

        recipe_serializer = RecipeResponseSerializer(recipe)
        recipe_serializer_data = recipe_serializer.data

        assert recipe_serializer_data == recipe_data

    @pytest.mark.parametrize('with_tags', [True, False])
    @pytest.mark.django_db()
    def test_recipe_serializer(self, with_tags):
        """Основной сериалайзер Рецепта."""
        ingredients_count = 10
        ingredients = IngredientFactory.create_batch(ingredients_count)
        recipe_ingredients = [
            {'id': ingredient.id, 'amount': self.faked_data.random_int(min=1, max=180)} for ingredient in ingredients
        ]
        recipe_tags = []
        if with_tags:
            tags_count = 4
            tags = TagFactory.create_batch(tags_count)
            recipe_tags = [tag.id for tag in tags]

        recipe_image_width = 200
        recipe_image_height = 200
        recipe_image_format = 'png'
        recipe_image = self.faked_data.image(
            size=(recipe_image_width, recipe_image_height), image_format=recipe_image_format
        )
        recipe_image_encoded = base64.b64encode(recipe_image).decode('utf-8')
        recipe_image_encoded_for_serializer = f'data:image/{recipe_image_format};base64,{recipe_image_encoded}'

        recipe_name = self.faked_data.word()
        recipe_text = self.faked_data.text()
        recipe_cooking_time = self.faked_data.random_int(min=1, max=180)

        recipe_author = UserFactory.create()

        recipe_data = {
            'ingredients': recipe_ingredients,
            'image': recipe_image_encoded_for_serializer,
            'name': recipe_name,
            'text': recipe_text,
            'cooking_time': recipe_cooking_time,
        }
        recipe_data['tags'] = recipe_tags

        class MockedRequest:
            def __init__(self):
                self.user = recipe_author

        recipe_serializer = RecipeSerializer(data=recipe_data, context={'request': MockedRequest()})

        assert recipe_serializer.is_valid()
        recipe = recipe_serializer.save()
        assert recipe.author == recipe_author
        assert recipe.name == recipe_name
        assert recipe.image.width == recipe_image_width
        assert recipe.image.height == recipe_image_height

        with open(recipe.image._file.name, 'rb') as f:
            recipe_obj_image_hash = hashlib.md5(f.read()).hexdigest()
        recipe_image_hash = hashlib.md5(recipe_image).hexdigest()

        assert recipe_obj_image_hash == recipe_image_hash
        assert recipe.text == recipe_text

        assert recipe.ingredients.count() == ingredients_count
        assert set(recipe.ingredients.all()) == set(ingredients)

        if with_tags:
            assert recipe.tags.count() == tags_count
            assert set(recipe.tags.all()) == set(tags)

        assert recipe.cooking_time == recipe_cooking_time
