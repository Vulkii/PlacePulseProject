from rest_framework import serializers, exceptions
from django.core.validators import RegexValidator
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model

from reviews.models import Review

from PlacePulse.constants import MAX_USERNAME_LENGHT, MAX_EMAIL_LENGTH

User = get_user_model()


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True,
    )

    class Meta:
        model = Review
        fields = ('__all__')
        read_only_fields = ('author',)


class UserSignUpSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        max_length=MAX_USERNAME_LENGHT,
        validators=[RegexValidator(regex=r'^[\w.@+-]+\Z')]
    )
    email = serializers.EmailField(
        required=True,
        max_length=MAX_EMAIL_LENGTH,
    )

    def validate_email(self, data):
        if data is None or data == '':
            raise serializers.ValidationError('Вы не указали email')
        return data

    def validate_username(self, data):
        if data == 'me':
            raise ValidationError('Нельзя использовать "me" в '
                                  'качестве имени пользователя')
        return data

    def create(self, validated_data):
        return User.objects.create(**validated_data)


class UserTokenSerializer(serializers.Serializer):
    confirmation_code = serializers.CharField(required=True)
    username = serializers.CharField(required=True,
                                     max_length=MAX_USERNAME_LENGHT)

    class Meta:
        model = User
        fields = (
            'username',
            'confirmation_code'
        )

    def validate_username(self, value):
        if not User.objects.filter(username=value).exists():
            raise exceptions.NotFound('Указанное имя не найдено')
        return value


class UserSerializer(serializers.ModelSerializer):
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
