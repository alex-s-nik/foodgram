from djoser.serializers import UserCreateSerializer as BaseUserCreateSerilizer
from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework import serializers

from recipes.models import AmountIngredients, Ingredient, Recipe, Tag
from users.models import User

from .fields import Base64ImageField


class UserSerializer(BaseUserSerializer):
    """Сериалайзер Пользователя."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )
        model = User

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.subscribed.filter(id=obj.id).exists()


class UserCreateSerializer(BaseUserCreateSerilizer):
    """Сериалайзер для создания Пользователя."""
    class Meta:
        fields = ('email', 'username', 'first_name', 'last_name', 'password')
        model = User


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер для Тэга."""
    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class ShortIngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для короткого описания Ингридиента."""
    class Meta:
        fields = ('id', 'amount')
        model = Ingredient


class AmountIngredientsSerializer(serializers.ModelSerializer):
    """Сериалайзер для Ингридиентов с количеством."""
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient', queryset=Ingredient.objects.all()
    )
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit')

    class Meta:
        model = AmountIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для Ингридиентов."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class CreateIngredientsInRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для создания Ингридиентов"""
    recipe = serializers.PrimaryKeyRelatedField(read_only=True)
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient', queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = AmountIngredients
        fields = ('recipe', 'id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для Рецептов."""
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    author = UserSerializer(read_only=True)
    ingredients = IngredientSerializer(many=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField()

    class Meta:
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
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

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        request = self.context['request']
        validated_data['author'] = request.user
        recipe = Recipe.objects.create(**validated_data)

        recipe.tags.set(tags)

        create_ingredients = [
            AmountIngredients(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount'],
            )
            for ingredient in ingredients
        ]

        AmountIngredients.objects.bulk_create(create_ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)

        if tags is not None:
            instance.tags.set(tags)
        if ingredients is not None:
            instance.ingredients.clear()

            create_ingredients = [
                AmountIngredients(
                    recipe=instance,
                    ingredient=ingredient['ingredient'],
                    amount=ingredient['amount'],
                )
                for ingredient in ingredients
            ]
            AmountIngredients.objects.bulk_create(create_ingredients)

        return super().update(instance=instance, validated_data=validated_data)


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для короткого описания Рецепта.
    Отображается при добавлении Рецепта в Список покупок."""
    image = Base64ImageField()

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe


class UserSubscriptionsSerializer(UserSerializer):
    """Сериалайзер для тех, кто подписан на Пользователя."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_recipes(self, obj):
        recipes_limit = int(self.context.get('recipes_limit', None))
        return ShortRecipeSerializer(obj.recipes.all()[:recipes_limit], many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    class Meta:
        model = UserSerializer.Meta.model
        fields = UserSerializer.Meta.fields + (
            'recipes_count',
            'recipes',
        )
