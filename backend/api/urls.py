from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import UserViewSet, TagViewSet

router = SimpleRouter()

router.register(
    'tags',
    TagViewSet,
    basename='tags',
)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('users/', UserViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('users/<int:id>/', UserViewSet.as_view({'get': 'retrieve'})),
    path('users/me/', UserViewSet.as_view({'get': 'me'})),
    path('users/set_password/', UserViewSet.as_view({'post': 'set_password'})),
    path('', include(router.urls)),
]
