import pytest

from recipes.factories import TagFactory


@pytest.fixture
def batch_of_tags():
    """Создание нескольких Тегов.
    По умолчанию 5."""

    def _wrapper(count: int = 5):
        return TagFactory.create_batch(count)

    return _wrapper


@pytest.fixture
def simple_tag(batch_of_tags):
    """Создание одного Тега."""
    return TagFactory.create()
