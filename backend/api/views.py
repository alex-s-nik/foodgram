from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework import viewsets

from .pagination import PageLimitPagination
from .serializers import IngridientSerializer, RecipeSerializer, TagSerializer

from recipes.models import Ingridient, Recipe, Tag


class UserViewSet(BaseUserViewSet):
    pagination_class = PageLimitPagination


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = PageLimitPagination
    serializer_classes = {
        'list': RecipeSerializer,
        'retrieve': RecipeSerializer,
        'create': ...,
        'update': ...,
        'delete': ...
    }

    def get_serializer_class(self):
        try:
            return self.serializer_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()

    def get_queryset(self):
        queryset = Recipe.objects.all()

        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited is not None and is_favorited in ('0', '1'):
            if not self.request.user.is_anonymous:
                if is_favorited == '0':
                    queryset = queryset.filter(favorite_users__id=self.request.user)
                else:
                    queryset = queryset.exclude(favorite_users__id=self.request.user)

        is_in_shopping_cart = self.request.query_params.get('is_in_shopping_cart')
        if is_in_shopping_cart is not None and is_in_shopping_cart in ('0', '1'):
            if not self.request.user.is_anonymous:
                if is_in_shopping_cart == '0':
                    queryset = queryset.filter(cart_users__id=self.request.user)
                else:
                    queryset = queryset.exclude(cart_users__id=self.request.user)

        author_id = self.request.query_params.get('author')
        if author_id is not None: 
            queryset = queryset.filter(author__id=author_id)

        tags = self.request.query_params.get('tags')
        if tags is not None:
            queryset = queryset.filter(tags__in=tags)

        return queryset


class IngridientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingridient.objects.all()
    serializer_class = IngridientSerializer
