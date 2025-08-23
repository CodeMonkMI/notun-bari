from django.contrib.auth import get_user_model
from djoser import serializers as sr
from rest_framework import serializers
from pet import serializers as pet_serializers
from pet.models import Adoption, Pet

User = get_user_model()


class UserCreateSerializer(sr.UserCreateSerializer):
    class Meta(sr.UserCreateSerializer.Meta):
        ref_name = "Customuser"
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
        ref_name = "Customuser"
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "username",
            "is_active",
            "is_staff",
            "last_login",
            "date_joined",
        ]


class CurrentUserSerializer(UserSerializer):

    class Meta(UserSerializer.Meta):

        model = User
        fields = UserSerializer.Meta.fields + ["balance"]
        read_only_fields = ["balance"]
