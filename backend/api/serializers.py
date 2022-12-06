from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from djoser.serializers import (
    UserSerializer as BaseUserSerializer,
    UserCreateSerializer as BaseUserCreateSerilizer
)
from rest_framework import serializers

from recipes.models import Recipe, Tag
from users.models import Follow

User = get_user_model()


class UserSerializer(BaseUserSerializer):
    is_described = serializers.SerializerMethodField()

    class Meta:
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_described')
        model = User
    
    def get_is_described(self, obj):
        request = self.context['request']
        if request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=obj).exists()


class UserCreateSerializer(BaseUserCreateSerilizer):
    class Meta:
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'password')
        model = User


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
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
        print(request.user.is_anonymous)
        if request.user.is_anonymous:
            return False
        return obj.favorite_users.filter(author=request.user).exist()

    def get_is_in_shopping_cart(self, obj):
        request = self.context['request']
        if request.user.is_anonymous:
            return False
        return obj.cart_users.filter(author=request.user).exist()


class RecipeListSerializer(RecipeSerializer):
    pass
