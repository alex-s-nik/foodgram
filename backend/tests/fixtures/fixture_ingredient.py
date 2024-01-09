import pytest

from recipes.factories import IngredientFactory


@pytest.fixture(scope='class')
def simple_ingredient(django_db_blocker):
    with django_db_blocker.unblock():
        ingredient = IngredientFactory.create()
    return ingredient
