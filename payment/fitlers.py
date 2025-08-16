from django_filters.rest_framework import FilterSet
from payment.models import PaymentHistory
from pet.models import Pet, Adoption
from django_filters import rest_framework as dj_filters


class PaymentHistoryFilter(FilterSet):
    class Meta:
        model = PaymentHistory
        fields = {
            "transaction_id": ["exact"],
            "payment_method": ["exact", "contains"],
            "status": ["exact", "contains"],
            "pet__name": ["exact", "contains"],
        }
