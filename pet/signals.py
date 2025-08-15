from django.dispatch import receiver
from django.db.models.signals import post_save
from pet.models import Adoption, Pet


@receiver(post_save, sender=Adoption)
def assign_default_role(sender, instance, created, **kwargs):
    if created:
        Pet.objects.filter(pk=instance.pet_id).update(status=Pet.ADOPTED)
