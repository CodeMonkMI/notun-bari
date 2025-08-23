import attr
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from .models import Pet, Adoption
from django.contrib.auth import get_user_model

User = get_user_model()


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
            "owner",
        ]

        read_only_fields = [
            "status",
            "owner",
        ]


class MyPetSerializer(PetSerializer):
    class Meta(PetSerializer.Meta):
        fields = [
            "id",
            "name",
            "category",
            "description",
            "category_name",
            "fees",
            "breed",
            "age",
            "status",
            "visibility",
        ]


class AdminPetSerializer(PetSerializer):
    class Meta(PetSerializer.Meta):
        fields = PetSerializer.Meta.fields + ["visibility"]


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
        if view.request.user.balance < pet.fees:
            raise ValidationError("Insufficient balance")

        self.context["pet_instance"] = pet
        return attrs


class AdoptedPetSerializer(serializers.ModelSerializer):

    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
    )

    class Meta:
        model = Pet
        fields = [
            "id",
            "name",
            "category_name",
            "fees",
            "breed",
            "age",
        ]


class AdoptedPetOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "first_name",
            "last_name",
        ]


class AdoptionSerializer(serializers.ModelSerializer):
    adopted_by = AdoptedPetOwnerSerializer(read_only=True)
    pet = AdoptedPetSerializer(read_only=True)

    class Meta:
        model = Adoption
        fields = [
            "id",
            "adopted_by",
            "date",
            "pet",
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
        if view.request.user.balance < pet.fees:
            raise ValidationError("Insufficient balance")

        self.context["pet_instance"] = pet
        return attrs


class AdoptionCreateSerializer(serializers.ModelSerializer):
    pet = serializers.PrimaryKeyRelatedField(
        queryset=Pet.objects.select_related("category", "owner").filter(
            status=Pet.APPROVED,
            visibility=Pet.PUBLIC,
        ),
        write_only=True,
    )

    class Meta:
        model = Adoption
        fields = [
            "pet",
        ]

    def validate(self, attrs):
        pet = attrs.get("pet")

        if pet.status == Pet.ADOPTED:
            raise ValidationError("This pet is already adopted!")

        request = self.context.get("request")
        if request and request.user.balance < pet.fees:
            raise ValidationError("Insufficient balance")

        attrs["adopted_by"] = request.user  # type: ignore
        return attrs


class AdoptionAdminCreateSerializer(AdoptionCreateSerializer):

    adopted_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(
            is_active=True,
        ),
        write_only=True,
    )

    class Meta(AdoptionCreateSerializer.Meta):

        fields = AdoptionCreateSerializer.Meta.fields + ["adopted_by"]

    def validate(self, attrs):
        pet = attrs.get("pet")
        adopted_by = attrs.get("adopted_by")

        if pet.status == Pet.ADOPTED:
            raise ValidationError("This pet is already adopted!")

        if adopted_by.balance < pet.fees:
            raise ValidationError("Insufficient balance")

        return attrs
