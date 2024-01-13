import pytest

from api.serializers import IngredientSerializer, TagSerializer
from recipes.factories import TagFactory


class TestSerializers:
    """Тестирование сериалайзеров."""

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

    def test_recipe_serializer(self):
        """Сериалайзер Рецепта."""
