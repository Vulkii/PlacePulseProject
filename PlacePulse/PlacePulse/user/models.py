from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db import models


from PlacePulse.constants import (
    MAX_ROLE_LENGHT, MAX_USERNAME_LENGHT, MAX_EMAIL_LENGTH
)


class User(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    ROLES = [
        (ADMIN, 'Administrator'),
        (MODERATOR, 'Moderator'),
        (USER, 'User'),
    ]
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=MAX_EMAIL_LENGTH,
        unique=True,
    )

    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=MAX_USERNAME_LENGHT,
        validators=[UnicodeUsernameValidator()],
        unique=True,
        error_messages={
            'unique': 'Пользователь с таким именем уже существует.',
        },
    )
    role = models.CharField(
        verbose_name='Роль',
        max_length=MAX_ROLE_LENGHT,
        choices=ROLES,
        default=USER
    )
    bio = models.TextField(
        verbose_name='О себе',
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def clean(self) -> None:
        if self.username == "me":
            raise ValidationError(f'Использование имени '
                                  f'"{self.username}" недопустимо')
        return super().clean()

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.ADMIN
