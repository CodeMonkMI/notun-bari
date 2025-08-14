from django.contrib.auth import get_user_model
from djoser import serializers as sr

User = get_user_model()


class UserCreateSerializer(sr.UserCreateSerializer):
    class Meta(sr.UserCreateSerializer.Meta):
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "username",
            "password",
        ]


class UserSerializer(sr.UserSerializer):
    class Meta(sr.UserSerializer.Meta):
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "username",
            "balance",
        ]
