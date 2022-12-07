from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerilizer
from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework import serializers

from recipes.models import Ingridient, Recipe, Tag

User = get_user_model()


class UserSerializer(BaseUserSerializer):
    is_described = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_described'
        )
        model = User

    def get_is_described(self, obj):
        request = self.context['request']
        user = request.user
        if user.is_anonymous:
            return False
        return user.subscribers.filter(id=obj.id).exists()


class UserCreateSerializer(BaseUserCreateSerilizer):
    class Meta:
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        model = User


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class IngridientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = Ingridient


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingridients = IngridientSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id',
            'tags',
            'author',
            'ingridients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        model = Recipe

    def get_is_favorited(self, obj):
        request = self.context['request']
        if request.user.is_anonymous:
            return False
        return obj.favorite_users.filter(username=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context['request']
        if request.user.is_anonymous:
            return False
        return obj.cart_users.filter(username=request.user).exists()


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe
