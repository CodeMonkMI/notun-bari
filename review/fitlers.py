from django_filters.rest_framework import FilterSet
from .models import Review
from django_filters import rest_framework as dj_filters


class ReviewFilter(FilterSet):
    class Meta:
        model = Review
        fields = {
            "reviewer__username": ["exact", "contains"],
            "pet__name": ["exact", "contains"],
        }
