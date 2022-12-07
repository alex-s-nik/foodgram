from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from recipes.models import Ingridient, Recipe, Tag

from .pagination import PageLimitPagination
from .serializers import IngridientSerializer, RecipeSerializer, RecipeShoppingCartSerializer, TagSerializer


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
                    queryset = queryset.filter(
                        favorite_users__id=self.request.user
                    )
                else:
                    queryset = queryset.exclude(
                        favorite_users__id=self.request.user
                    )

        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )
        if (is_in_shopping_cart is not None
                and is_in_shopping_cart in ('0', '1')):
            if not self.request.user.is_anonymous:
                if is_in_shopping_cart == '0':
                    queryset = queryset.filter(
                        cart_users__id=self.request.user
                    )
                else:
                    queryset = queryset.exclude(
                        cart_users__id=self.request.user
                    )

        author_id = self.request.query_params.get('author')
        if author_id is not None:
            queryset = queryset.filter(author__id=author_id)

        tags = self.request.query_params.get('tags')
        if tags is not None:
            queryset = queryset.filter(tags__in=tags)

        return queryset

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            if user.shopping_cart.filter(id=recipe.id).exists():
                raise ValidationError({'errors': 'Рецепт уже был добавлен в корзину'})
            user.shopping_cart.add(recipe)
            context = self.get_serializer_context()
            serializer = RecipeShoppingCartSerializer

            response = Response(
                serializer(instance=recipe, context=context).data,
                status=status.HTTP_201_CREATED
            )
        else:
            raise ValidationError({'errors': f'Метод {request.method} не поддерживается'})

        return response



class IngridientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingridient.objects.all()
    serializer_class = IngridientSerializer
