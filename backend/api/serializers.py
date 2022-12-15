import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
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
            'last_name': {'required': True, 'allow_blank': False},
            'email': {'required': True, 'allow_blank': False}
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
    id = serializers.PrimaryKeyRelatedField(
        source='ingridient',
        queryset=Ingridient.objects.all()
    )
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    def get_name(self, obj):
        return obj.ingridient.name

    def get_measurement_unit(self, obj):
        return obj.ingridient.measurement_unit

    class Meta:
        model = AmountIngridients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngridientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingridient
        fields = '__all__'


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
            obj.ingridients_amount.all(),
            many=True
        ).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe


class CreateIngridientsInRecipeSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(read_only=True)
    id = serializers.PrimaryKeyRelatedField(
        source='ingridient',
        queryset=Ingridient.objects.all()
    )
    amount = serializers.IntegerField(
        write_only=True
    )

    class Meta:
        model = AmountIngridients
        fields = ('recipe', 'id', 'amount')


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class CreateRecipeSerializer(serializers.ModelSerializer):
    ingridients = CreateIngridientsInRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    image = Base64ImageField()
    author = UserSerializer(required=False)

    def create(self, validated_data):
        ingridients = validated_data.pop('ingridients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        recipe.tags.set(tags)

        create_ingridients = [
            AmountIngridients(
                recipe=recipe,
                ingridient=ingridient['ingridient'],
                amount=ingridient['amount']
            )
            for ingridient in ingridients
        ]

        AmountIngridients.objects.bulk_create(create_ingridients)
        return recipe

    def update(self, instance, validated_data):
        ingridients = validated_data.pop('ingridients', None)
        tags = validated_data.pop('tags', None)

        if tags is not None:
            instance.tags.set(tags)
        if ingridients is not None:
            instance.ingridients.clear()

            create_ingridients = [
                AmountIngridients(
                    recipe=instance,
                    ingridient=ingridient['ingridient'],
                    amount=ingridient['amount']
                )
                for ingridient in ingridients
            ]
            AmountIngridients.objects.bulk_create(create_ingridients)

        return super().update(instance=instance, validated_data=validated_data)

    def to_representation(self, instance):
        self.fields.pop('ingridients')
        self.fields['tags'] = TagSerializer(many=True)
        representation = super().to_representation(instance)
        representation['ingridients'] = AmountIngridientsSerializer(
            AmountIngridients.objects.filter(recipe=instance), many=True
        ).data
        return representation

    class Meta:
        fields = (
            'author',
            'ingridients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )
        model = Recipe
