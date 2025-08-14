from django.db import models
from uuid import uuid4
from django.contrib.auth.models import AbstractUser


# Create your models here.


class CustomUser(AbstractUser):

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    balance = models.FloatField(max_length=50, default=0.0)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"
