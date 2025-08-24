from rest_framework import serializers

from pet.models import Pet
from .models import PaymentHistory


class PetSerializer(serializers.ModelSerializer):
    category = serializers.CharField(
        source="category.name",
        read_only=True,
    )

    class Meta:
        ref_name = "payment_pet_serializer"
        model = Pet
        fields = [
            "name",
            "category",
        ]


class PaymentHistorySerializer(serializers.ModelSerializer):
    pet_details = PetSerializer(source="pet", read_only=True)
    pet = serializers.PrimaryKeyRelatedField(
        queryset=Pet.objects.filter(status=Pet.APPROVED),
        required=False,
        write_only=True,
    )

    class Meta:
        model = PaymentHistory
        fields = [
            "id",
            "transaction_id",
            "amount",
            "payment_method",
            "pet",
            "pet_details",
            "status",
            "payment_type",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class PaymentAdminHistorySerializer(PaymentHistorySerializer):
    class Meta(PaymentHistorySerializer.Meta):
        fields = PaymentHistorySerializer.Meta.fields + ["user"]


class PaymentInitSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentHistory
        fields = [
            "amount",
        ]
