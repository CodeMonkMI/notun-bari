from django_filters.rest_framework import FilterSet
from pet.models import Pet, Adoption
from django_filters import rest_framework as dj_filters


class PetFilter(FilterSet):
    class Meta:
        model = Pet
        fields = {
            "name": ["contains"],
            "category__name": ["exact", "contains"],
            "fees": ["lt", "gt"],
            "status": ["exact"],
        }


class AdoptionHistoryFilter(dj_filters.FilterSet):
    # Range filtering: /adoptions/?date_after=...&date_before=...
    date_after = dj_filters.IsoDateTimeFilter(field_name="date", lookup_expr="gte")
    date_before = dj_filters.IsoDateTimeFilter(field_name="date", lookup_expr="lte")

    adopted_by = dj_filters.CharFilter(field_name="adopted_by")

    class Meta:
        model = Adoption
        fields = ["adopted_by", "date_after", "date_before"]
