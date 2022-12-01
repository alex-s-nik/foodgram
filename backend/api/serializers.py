from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework import serializers

from users.models import Follow

User = get_user_model()


class UserSerializer(BaseUserSerializer):
    is_described = serializers.SerializerMethodField()

    class Meta:
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_described')
        model = User
    
    def get_is_described(self, obj):
        request = self.context['request']
        return Follow.objects.filter(user=request.user, author=obj).exists()
