from djoser.views import UserViewSet as BaseUserViewSet

from .pagination import UserPageLimitPagination


class UserViewSet(BaseUserViewSet):
    pagination_class = UserPageLimitPagination
