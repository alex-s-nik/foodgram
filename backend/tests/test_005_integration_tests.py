class TestAllUsers:
    """Что могут делать все пользователи."""

    def test_view_recipes_on_main_page(self):
        """Просматривать рецепты на главной."""
        ...

    def test_visit_page_with_recipe(self):
        """Просматривать отдельные страницы рецептов."""
        ...

    def test_visit_to_other_userpage(self):
        """Просматривать страницы пользователей."""
        ...

    def test_filter_recipes_by_tags(self):
        """Фильтровать рецепты по тегам."""
        ...


class TestUnauthorizedUsers:
    "Что могут делать неавторизованные пользователи."

    def test_create_account(self):
        "Создать аккаунт."
        ...


class TestAuthorizedUsersAndAdmins:
    """Что могут делать авторизованные пользователи и администраторы."""

    def test_login(self):
        """Входить в систему под своим логином и паролем."""
        ...

    def test_logout(self):
        """Выходить из системы (разлогиниваться)."""
        ...

    def test_change_password(self):
        """Менять свой пароль."""
        ...

    def test_actions_with_own_recipes(self):
        """Создавать/редактировать/удалять собственные рецепты."""
        ...

    def test_favorite_list(self):
        """Работать с персональным списком избранного: добавлять в него рецепты или удалять их, просматривать свою страницу избранных рецептов."""
        ...

    def test_shopping_cart(self):
        """Работать с персональным списком покупок: добавлять/удалять любые рецепты, выгружать файл с количеством необходимых ингредиентов для рецептов из списка покупок."""
        ...

    def test_subcribing(self):
        """Подписываться на публикации авторов рецептов и отменять подписку, просматривать свою страницу подписок."""
        ...


class TestAdminUsers:
    """Что может делать администратор."""

    def test_change_password_of_other_user(self):
        """Изменять пароль любого пользователя."""

    def test_actions_with_users_Accounts(self):
        """Создавать/блокировать/удалять аккаунты пользователей."""

    def test_actions_with_foreign_recipes(self):
        """Редактировать/удалять любые рецепты."""

    def test_actions_with_ingredients(self):
        """Добавлять/удалять/редактировать ингредиенты."""

    def test_actions_with_tags(self):
        """Добавлять/удалять/редактировать теги."""
        ...
