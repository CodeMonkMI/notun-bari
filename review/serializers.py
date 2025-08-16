from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = Review
        fields = ["id", "comments", "reviewer", "image", "created_at", "updated_at"]
        read_only_fields = ["id", "reviewer", "created_at", "updated_at"]

    def validate(self, attrs):
        view = self.context.get("view")
        if not view:
            raise serializers.ValidationError("View context is missing.")

        pet_pk = view.kwargs.get("pets_pk")

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
