from django.contrib.auth import get_user_model
from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework import viewsets
from rest_framework.decorators import action

from recipes.models import Ingridient, Recipe, Tag

from .mixins import M2MCreateDelete
from .pagination import PageLimitPagination
from .serializers import (CreateRecipeSerializer, RecipeSerializer,
                          ShortIngridientSerializer, ShortRecipeSerializer,
                          TagSerializer, UserSerializer)

User = get_user_model()


class UserViewSet(BaseUserViewSet, M2MCreateDelete):
    pagination_class = PageLimitPagination

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, id=None):
        subscriber = request.user
        author = get_object_or_404(User, id=id)

        return self.m2m_create_delete(
            obj1_m2m_manager=author.subscribers,
            obj2=subscriber,
            request=request,
            serializer=UserSerializer,
            errors={
                'create_fail': 'Вы уже подписаны на этого пользователя',
                'delete_fail': 'Вы не подписаны на этого пользователя'
            }
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet, M2MCreateDelete):
    pagination_class = PageLimitPagination
    serializer_classes = {
        'list': RecipeSerializer,
        'retrieve': RecipeSerializer,
        'create': CreateRecipeSerializer,
        'update': CreateRecipeSerializer,

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

        return self.m2m_create_delete(
            obj1_m2m_manager=user.shopping_cart,
            obj2=recipe,
            request=request,
            serializer=ShortRecipeSerializer,
            errors={
                'create_fail': 'Рецепт уже был добавлен в корзину',
                'delete_fail': 'Этого рецепта нет в корзине'
            }
        )

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        user = request.user

        ingridients_queryset = user.shopping_cart.values(
            'ingridients__name',
            'ingridients__measurement_unit'
        ).annotate(
            Sum('ingridients_amount__amount')
        ).values(
            name=F('ingridients__name'),
            units=F('ingridients__measurement_unit'),
            total=F('ingridients_amount__amount__sum')
        ).order_by('name')

        text = '\n'.join(
            f'{ingt["name"]}: {ingt["total"]} {ingt["units"]}'
            for ingt in ingridients_queryset
        )
        filename = 'shopping_cart.txt'
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        return self.m2m_create_delete(
            obj1_m2m_manager=user.shopping_cart,
            obj2=recipe,
            request=request,
            serializer=ShortRecipeSerializer,
            errors={
                'create_fail': 'Рецепт уже был добавлен в избранное',
                'delete_fail': 'Этого рецепта нет в избранном'
            }
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)


class IngridientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingridient.objects.all()
    serializer_class = ShortIngridientSerializer
