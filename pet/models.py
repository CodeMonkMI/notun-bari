from pickle import TRUE
from pyexpat import model
import uuid
from django.conf import settings
from django.db import models
from category.models import Category
from django.contrib.auth import get_user_model

User = get_user_model()


class PetStatus(models.TextChoices):
    PENDING = "pending", "pending"
    APPROVED = "approved", "approved"
    ADOPTED = "adopted", "adopted"
    WITHDRAWN = "withdrawn", "withdrawn"
    SUSPENDED = "suspended", "suspended"


class PetVisibility(models.TextChoices):
    PUBLIC = "public", "public"
    PRIVATE = "private", "private"


class Pet(models.Model):

    PENDING = "pending"
    APPROVED = "approved"
    ADOPTED = "adopted"
    WITHDRAWN = "withdrawn"
    SUSPENDED = "suspended"

    StatusChoices = [
        (PENDING, "pending"),
        (APPROVED, "approved"),
        (ADOPTED, "adopted"),
        (WITHDRAWN, "withdrawn"),
        (SUSPENDED, "suspended"),
    ]

    PUBLIC = "public"
    PRIVATE = "private"

    VisibilityChoices = [
        (PUBLIC, "public"),
        (PRIVATE, "private"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)

    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, related_name="pets", null=True
    )

    status = models.CharField(max_length=20, choices=StatusChoices, default=PENDING)
    visibility = models.CharField(
        max_length=20, choices=VisibilityChoices, default=PRIVATE
    )

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owned_pets", null=True
    )
    adopted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="adopted_pets",
        null=True,
        blank=True,
    )

    fees = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.name}"


class Adoption(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pet = models.ForeignKey(
        Pet, on_delete=models.CASCADE, related_name="adoption_history"
    )
    adopted_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="adopted", null=True
    )

    date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Adoption of {self.pet.name} on {self.date.isoformat()}"
