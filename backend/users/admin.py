from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserAdmin(UserAdmin):
    search_fields = ('email', 'username')


admin.site.register(User, CustomUserAdmin)
admin.site.unregister(Group)
