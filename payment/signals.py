from django.dispatch import receiver
from django.db.models.signals import post_save
from payment.models import PaymentHistory
from pet.models import Adoption, Pet
from django.contrib.auth import get_user_model

from user.models import CustomUser

User = get_user_model()


@receiver(post_save, sender=PaymentHistory)
def update_user_balance(sender, instance, created, **kwargs):
    if created:
        payment_type = instance.payment_type
        user = instance.user
        if instance.status != PaymentHistory.SUCCESS:
            return
        if payment_type == PaymentHistory.INCOME:
            user.balance += float(instance.amount)
        else:
            user.balance -= float(instance.amount)

        user.save(update_fields=["balance"])
