from django.forms import ValidationError
from rest_framework import viewsets, permissions, mixins
from rest_framework import serializers
from pet.fitlers import AdoptionHistoryFilter, PetFilter
from pet.paginations import AdoptionHistoryPagination, PetsPagination
from pet.models import Pet, Adoption
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from pet.serializers import (
    PetSerializer,
    AdoptionHistorySerializer,
    PetUpdateSerializer,
)


class PetViewSet(viewsets.ModelViewSet):
    queryset = (
        Pet.objects.select_related("category")
        .select_related("owner")
        .filter(status=Pet.APPROVED)
    )
    serializer_class = PetSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = PetsPagination
    http_method_names = ["get", "post", "patch", "delete", "head", "options", "trace"]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PetFilter
    search_fields = ["name", "category__name", "fees"]
    ordering_fields = ["fees", "updated_at"]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_serializer_class(self):
        if self.action == "partial_update":
            return PetUpdateSerializer
        return PetSerializer


class AdoptionHistoryViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = AdoptionHistorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    http_method_names = ["get", "post", "head", "options", "trace"]

    pagination_class = AdoptionHistoryPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = AdoptionHistoryFilter
    ordering_fields = ["date", "id"]

    def get_queryset(self):
        pet_pk = self.kwargs.get("pets_pk")
        return Adoption.objects.select_related("pet", "adopted_by").filter(
            pet_id=pet_pk,
        )

    def perform_create(self, serializer):
        pet_pk = self.kwargs.get("pets_pk")
        pet = Pet.objects.get(pk=pet_pk)
        if pet.status == Pet.ADOPTED:
            raise serializers.ValidationError("this pet is already adopted!")

        serializer.save(pet_id=pet_pk, adopted_by=self.request.user)
