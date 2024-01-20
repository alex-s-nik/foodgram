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
        if 'request' not in self.context:
            return False
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


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для Ингридиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class AmountIngredientsSerializer(serializers.ModelSerializer):
    """Сериалайзер для Ингридиентов в Рецепте."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = AmountIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


'''class RecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для Рецептов."""

    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = AmountIngredientsSerializer(
        source='ingredients_amount',
        many=True,
        read_only=True,
    )
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
        if 'request' not in self.context:
            return False
        request = self.context['request']
        if request.user.is_anonymous:
            return False
        return obj.favorite_users.filter(username=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        if 'request' not in self.context:
            return False
        request = self.context['request']
        if request.user.is_anonymous:
            return False
        return obj.cart_users.filter(username=request.user).exists()

    def validate(self, data):
        ingredients = self.initial_data['ingredients']
        if not ingredients:
            raise serializers.ValidationError('Количество ингридиентов должно быть больше 0.')
        data['ingredients'] = ingredients
        return data

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
                ingredient=Ingredient.objects.get(pk=ingredient['id']),
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

        return super().update(instance=instance, validated_data=validated_data)'''


class RecipeResponseSerializer(serializers.ModelSerializer):
    """Сериалайзер Рецепта для GET-ответов."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
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

    def get_ingredients(self, obj):
        return AmountIngredientsSerializer(obj.ingredients_amount.all(), many=True).data

    def get_is_favorited(self, obj):
        return False

    def get_is_in_shopping_cart(self, obj):
        return False


class RecipeSerializer(serializers.ModelSerializer):
    """Основной сериалайзер для Рецепта."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name', 'text', 'cooking_time')

    def to_representation(self, instance):
        return RecipeResponseSerializer(context=self.context).to_representation(instance)

    def validate(self, data):
        ingredients = self.initial_data['ingredients']
        ingredients_list = []
        if not ingredients:
            raise serializers.ValidationError('Количество ингридиентов должно быть больше 0.')
        for ingredient in ingredients:
            if not Ingredient.objects.filter(pk=ingredient['id']).exists():
                raise serializers.ValidationError(f'Ингридиента с id = {ingredient["id"]} не существует.')
            ingredients_list.append(
                {'ingredient': Ingredient.objects.get(pk=ingredient['id']), 'amount': ingredient['amount']}
            )
        data['ingredients'] = ingredients_list

        tag_ids = self.initial_data['tags']
        tags_list = []

        for tag_id in tag_ids:
            try:
                tag_id = int(tag_id)
            except ValueError:
                raise serializers.ValidationError('Id тэга должен быть целым числом.')
            if not Tag.objects.filter(pk=tag_id).exists():
                raise serializers.ValidationError(f'Тэга с id = {tag_id} не существует.')
            tags_list.append(Tag.objects.get(pk=tag_id))
        data['tags'] = tags_list

        return data

    def create(self, validated_data):
        request = self.context['request']
        validated_data['author'] = request.user

        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        new_recipe = Recipe.objects.create(**validated_data)

        for tag in tags:
            new_recipe.tags.add(tag)

        ingredients_with_amount_for_new_recipe = [
            AmountIngredients(
                recipe=new_recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount'],
            )
            for ingredient in ingredients
        ]
        AmountIngredients.objects.bulk_create(ingredients_with_amount_for_new_recipe)

        return new_recipe


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
