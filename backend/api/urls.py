from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import IngridientViewSet, RecipeViewSet, TagViewSet, UserViewSet

router = SimpleRouter()

router.register(
    'users',
    UserViewSet,
    basename='users',
)

router.register(
    'tags',
    TagViewSet,
    basename='tags',
)

router.register(
    'recipes',
    RecipeViewSet,
    basename='recipes',
)

router.register(
    'ingridients',
    IngridientViewSet,
    basename='ingridients',
)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
