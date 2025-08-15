import uuid
from django.db import models
from django.contrib.auth import get_user_model
from cloudinary.models import CloudinaryField
from pet.models import Pet

User = get_user_model()


class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    comments = models.TextField()
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name="reviews")
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")

    image = CloudinaryField("image", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review by {self.reviewer}"
