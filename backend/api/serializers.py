from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerilizer
from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework import serializers

from recipes.models import AmountIngridients, Ingridient, Recipe, Tag

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
        extra_kwargs = {
            'first_name': {'required': True, 'allow_blank': False},
            'last_name': {'required': True,'allow_blank': False},
            'email': {'required': True,'allow_blank': False}
        }


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class ShortIngridientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'amount')
        model = Ingridient


class AmountIngridientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AmountIngridients
        fields = ('amount',)


class IngridientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingridient
        fields = '__all__'

    def serialize_ingridients_amount(self, ingridient_instance):
        ingridient_amount_instance = ingridient_instance.recipes.filter(
            recipe=self.context['recipe_instance']
        ).first()
        
        if ingridient_amount_instance:
            return AmountIngridientsSerializer(ingridient_amount_instance).data
    
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        return {**rep, **self.serialize_ingridients_amount(instance)}


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingridients = serializers.SerializerMethodField()
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
    
    def get_ingridients(self, obj):
        return AmountIngridientsSerializer(
            obj.ingridients.all(),
            many=True,
            context={'recipe_instance': obj}
        ).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe
