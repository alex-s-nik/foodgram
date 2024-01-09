import pytest

from recipes.factories import TagFactory


@pytest.fixture(scope='class')
def simple_tag(django_db_blocker):
    with django_db_blocker.unblock():
        tag = TagFactory.create()
    return tag
