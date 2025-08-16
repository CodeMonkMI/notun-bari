from urllib import request
from rest_framework import serializers
from pet.models import Pet
from .models import Review
from django.contrib.auth import get_user_model

User = get_user_model()


class ReviewerSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(method_name="get_full_name")

    class Meta:
        model = get_user_model()
        fields = ["name", "username"]

    def get_full_name(self, user):
        return f"{user.first_name} {user.last_name}"


class ReviewSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    reviewer = ReviewerSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ["id", "comments", "reviewer", "image", "created_at"]
        read_only_fields = ["id", "reviewer", "created_at"]

    def validate(self, attrs):
        view = self.context.get("view")
        if not view:
            raise serializers.ValidationError("View context is missing.")

        pet_pk = view.kwargs.get("pets_pk")
        pet = Pet.objects.get(pk=pet_pk)
        if not pet.adopted_by == view.request.user:
            raise serializers.ValidationError(
                "You can only provide review for those pet you adopted!"
            )

        if Review.objects.filter(pet_id=pet_pk, reviewer=view.request.user).exists():
            raise serializers.ValidationError(
                "You have already provided a review for this pet"
            )

        return attrs


class ReviewUpdateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)

    class Meta:
        model = Review
        fields = [
            "comments",
            "image",
        ]
