import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from pet.models import Pet


User = get_user_model()


class PaymentHistory(models.Model):
    FAILED = "failed"
    SUCCESS = "success"
    BLOCKED = "blocked"

    STATUS_CHOICES = [
        (FAILED, "failed"),
        (SUCCESS, "success"),
        (BLOCKED, "blocked"),
    ]

    EXPENSE = "expense"
    INCOME = "income"
    PAYMENT_TYPE_CHOICES = [
        (EXPENSE, "expense"),
        (INCOME, "income"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)

    pet = models.ForeignKey(
        Pet,
        on_delete=models.SET_NULL,
        related_name="payment_histories",
        blank=True,
        null=True,
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="payment_histories"
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=SUCCESS)
    payment_type = models.CharField(
        max_length=20, choices=PAYMENT_TYPE_CHOICES, default=INCOME
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.transaction_id} ({self.status})"
