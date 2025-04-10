from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from . import constants
from .enums import UserRole


class MyUser(AbstractUser):
    """Модель пользователя."""
    username = models.CharField(
        'Имя пользователя',
        max_length=constants.MAX_LENGTH_NAME,
        unique=True,
        blank=False,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+\Z$',
            message='Имя пользователя содержит недопустимый символ'
        )]
    )

    email = models.EmailField(
        'Электронная почта',
        max_length=constants.MAX_LENGTH_EMAIL,
        unique=True,
        blank=False
    )

    first_name = models.CharField(
        'Имя',
        max_length=constants.MAX_LENGTH_NAME,
        blank=True
    )

    last_name = models.CharField(
        'Фамилия',
        max_length=constants.MAX_LENGTH_NAME,
        blank=True
    )

    bio = models.TextField('Биография', blank=True)

    role = models.CharField(
        'Роль',
        max_length=constants.MAX_LENGTH_DEFAULT,
        choices=UserRole.choices(),
        default=UserRole.user.name,
    )

    confirmation_code = models.SlugField(null=True, blank=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        """Возвращает строковое представление пользователя (username)."""
        return self.username

    @property
    def is_admin(self):
        return self.role == UserRole.admin.name

    @property
    def is_moderator(self):
        return self.role == UserRole.moderator.name

    @property
    def is_user(self):
        return self.role == UserRole.user.name
