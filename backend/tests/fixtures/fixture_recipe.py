import pytest

from recipes.factories import RecipeFactory


@pytest.fixture
def simple_recipe():
    """Создание Рецепта без Тегов и Ингридиентов."""
    return RecipeFactory.create()
