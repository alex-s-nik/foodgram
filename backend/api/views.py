from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework import viewsets

from .pagination import UserPageLimitPagination
from .serializers import TagSerializer

from recipes.models import Tag


class UserViewSet(BaseUserViewSet):
    pagination_class = UserPageLimitPagination


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
