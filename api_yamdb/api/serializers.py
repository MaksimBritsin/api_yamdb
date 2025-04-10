import re

from api.const import USERNAME_REGEX
from django.contrib.auth import get_user_model
from rest_framework import serializers
from users import constants

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя."""

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )


class SignupSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя."""

    username = serializers.RegexField(
        required=True,
        max_length=constants.MAX_LENGTH_NAME,
        regex=USERNAME_REGEX,
    )
    email = serializers.EmailField(
        required=True, max_length=constants.MAX_LENGTH_EMAIL)

    class Meta:
        model = User
        fields = ('email', 'username')

    def create(self, validated_data):
        """Создаёт нового пользователя или возвращает существующего."""
        return User.objects.get_or_create(**validated_data)[0]

    def validate_username(self, value):
        """Проверяет username на запрещённые значения и символы."""
        if value.lower() == 'me':
            raise serializers.ValidationError(
                "Использовать 'me' в качестве username запрещено.")
        pattern = USERNAME_REGEX
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "Имя пользователя содержит недопустимые символы.")
        return value


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""

    username = serializers.CharField()
    confirmation_code = serializers.CharField()
