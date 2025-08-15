from functools import partial
from rest_framework import viewsets, permissions, mixins, status
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
    PetStatusUpdateSerializer,
)
from rest_framework.decorators import action
from rest_framework.response import Response


class PetViewSet(viewsets.ModelViewSet):

    pagination_class = PetsPagination
    http_method_names = ["get", "post", "patch", "delete", "head", "options", "trace"]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PetFilter
    search_fields = ["name", "category__name", "fees"]
    ordering_fields = ["fees", "updated_at"]

    @action(detail=False, methods=["get"])
    def my_pet(self, request, pk=None):
        queryset = self.filter_queryset(
            Pet.objects.select_related("category", "owner").filter(owner=request.user)
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"])
    def update_status(self, request, pk=None):
        pet = self.get_object()
        serializer = PetStatusUpdateSerializer(pet, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def retrieve(self, request, *args, **kwargs):
        pet = self.get_object()

        if pet.owner == request.user:
            serializers = self.get_serializer(pet)
            return Response(serializers.data, status=status.HTTP_200_OK)

        if pet.status == Pet.APPROVED:
            serializers = self.get_serializer(pet)
            return Response(serializers.data, status=status.HTTP_200_OK)

        return Response({"details": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    def get_permissions(self):
        if self.action in ["my_pet"]:
            return [permissions.IsAuthenticated()]

        if self.action in ["update_status"]:
            return [permissions.IsAdminUser()]

        return [permissions.IsAuthenticatedOrReadOnly()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_serializer_class(self):
        if self.action == "partial_update":
            return PetUpdateSerializer
        if self.action in ["update_status"]:
            return PetStatusUpdateSerializer
        return PetSerializer

    def get_queryset(self):
        if self.action in ["retrieve"]:
            return Pet.objects.select_related("category", "owner")
        return Pet.objects.select_related("category", "owner").filter(
            status=Pet.APPROVED
        )


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
