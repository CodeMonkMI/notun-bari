from rest_framework import serializers
from rest_framework.serializers import ValidationError
from .models import Pet, Adoption
from django.contrib.auth import get_user_model


class PetOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            "first_name",
            "last_name",
        ]


class PetCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            "first_name",
            "last_name",
        ]


class PetSerializer(serializers.ModelSerializer):
    owner = PetOwnerSerializer(read_only=True)
    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
    )

    class Meta:
        model = Pet
        fields = [
            "id",
            "name",
            "category",
            "description",
            "category_name",
            "fees",
            "breed",
            "age",
            "visibility",
            "owner",
        ]

        read_only_fields = [
            "status",
            "owner",
        ]
        extra_kwargs = {
            "category": {
                "write_only": True,
            }
        }


class MyPetSerializer(PetSerializer):
    class Meta(PetSerializer.Meta):
        fields = PetSerializer.Meta.fields + ["status"]


class PetUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Pet
        fields = [
            "name",
            "category",
            "description",
            "fees",
            "visibility",
            "status",
        ]


class AdoptedBySerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            "first_name",
            "last_name",
            "username",
        ]


class AdoptionHistorySerializer(serializers.ModelSerializer):
    adopted_by = PetOwnerSerializer(read_only=True)

    class Meta:
        model = Adoption
        fields = [
            "id",
            "adopted_by",
            "date",
        ]

        read_only_fields = [
            "id",
            "adopted_by",
            "date",
        ]

    def validate(self, attrs):
        view = self.context.get("view")
        if not view:
            raise ValidationError("View context is missing.")

        pet_pk = view.kwargs.get("pets_pk")
        try:
            pet = Pet.objects.get(pk=pet_pk)
        except Pet.DoesNotExist:
            raise ValidationError("Pet not found.")

        if pet.status == Pet.ADOPTED:
            raise ValidationError("This pet is already adopted!")

        self.context["pet_instance"] = pet
        return attrs
