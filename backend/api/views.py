from django.db.models import Case, F, Sum, Value, When
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import Ingredient, Recipe, Tag
from users.models import User

from .mixins import M2MAddRemoveHelper
from .pagination import PageLimitPagination
from .serializers import (CreateRecipeSerializer, IngredientSerializer,
                          RecipeSerializer, ShortRecipeSerializer,
                          TagSerializer, UserSerializer, UserSubscriptionsSerializer)


class UserViewSet(BaseUserViewSet, M2MAddRemoveHelper):
    pagination_class = PageLimitPagination

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, id=None):
        subscriber = request.user
        author = get_object_or_404(User, id=id)
        fail_messages = {
            'add_fail': 'Вы уже подписаны на этого пользователя',
            'remove_fail': 'Вы не подписаны на этого пользователя'
        }
        return self.m2m_add_remove(
            m2m_manager_of_changing_object=author.subscribers,
            object_for_action=subscriber,
            object_serializer=UserSerializer,
            request_method=request.method,
            fail_messages=fail_messages
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes = (IsAuthenticated,),
        serializer_class = UserSubscriptionsSerializer
    )
    def subscriptions(self, request):
        user = request.user
        serializer = self.get_serializer_class()
        recipes_limit = self.request.query_params.get('recipes_limit')
        queryset = user.subscribed.all()
        context = {
            'recires_limit': recipes_limit,
            'request': request
        }

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context=context)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True, context=context)
        return Response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet, M2MAddRemoveHelper):
    pagination_class = PageLimitPagination
    serializer_classes = {
        'list': RecipeSerializer,
        'retrieve': RecipeSerializer,
        'create': CreateRecipeSerializer,
        'partial_update': CreateRecipeSerializer,

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
                if is_favorited == '1':
                    queryset = queryset.filter(
                        favorite_users__id=self.request.user.id
                    )
                else:
                    queryset = queryset.exclude(
                        favorite_users__id=self.request.user.id
                    )

        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )
        if (is_in_shopping_cart is not None
                and is_in_shopping_cart in ('0', '1')):
            if not self.request.user.is_anonymous:
                if is_in_shopping_cart == '1':
                    queryset = queryset.filter(
                        cart_users__id=self.request.user.id
                    )
                else:
                    queryset = queryset.exclude(
                        cart_users__id=self.request.user.id
                    )

        author_id = self.request.query_params.get('author')
        if author_id is not None:
            queryset = queryset.filter(author__id=author_id)

        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        return queryset

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        fail_messages = {
            'add_fail': 'Рецепт уже был добавлен в корзину',
            'remove_fail': 'Этого рецепта нет в корзине'
        }
        return self.m2m_add_remove(
            m2m_manager_of_changing_object=user.shopping_cart,
            object_for_action=recipe,
            object_serializer=ShortRecipeSerializer,
            request_method=request.method,
            fail_messages=fail_messages
        )

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        user = request.user

        ingredients_queryset = user.shopping_cart.values(
            'ingredients__name',
            'ingredients__measurement_unit'
        ).annotate(
            Sum('ingredients_amount__amount')
        ).values(
            name=F('ingredients__name'),
            units=F('ingredients__measurement_unit'),
            total=F('ingredients_amount__amount__sum')
        ).order_by('name')

        text = '\n'.join(
            f'{ingt["name"]}: {ingt["total"]} {ingt["units"]}'
            for ingt in ingredients_queryset
        )
        filename = 'shopping_cart.txt'
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        fail_messages = {
            'add_fail': 'Рецепт уже был добавлен в избранное',
            'remove_fail': 'Этого рецепта нет в избранном'
        }
        return self.m2m_add_remove(
            m2m_manager_of_changing_object=user.favorites,
            object_for_action=recipe,
            object_serializer=ShortRecipeSerializer,
            request_method=request.method,
            fail_messages=fail_messages
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer

    def get_queryset(self):
        queryset = Ingredient.objects.all()

        searched_name = self.request.query_params.get('name')
        if searched_name:
            # Если есть совпадения, сначала выводим ингридиенты
            # с совпадениями в начале,
            # затем те, в которых есть совпадения вообще
            # Для этого создадим еще один столбец в таблице с признаком:
            # 2 - совпадение в начале имени,
            # 1 - совпадение вообще,
            # 0 - совпадений нет.
            # Затем отберем те записи, у которых этот признак 1 или 2
            # В окончательный запрос отправим записи в нужном порядке
            # и без столбца-признака
            queryset = queryset.annotate(
                search_sort_attribute=Case(
                    When(name__istartswith=searched_name, then=Value('2')),
                    When(name__icontains=searched_name, then=Value('1')),
                    default=Value('0')
                )
            ).filter(
                search_sort_attribute__in=('1', '2')
            ).order_by('-search_sort_attribute').values(
                'id', 'name', 'measurement_unit'
            )

        return queryset
