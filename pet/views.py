from functools import partial
from rest_framework import viewsets, permissions, mixins, status
from rest_framework import serializers
from pet.fitlers import AdoptionHistoryFilter, PetFilter
from pet.paginations import AdoptionHistoryPagination, PetsPagination
from pet.models import Pet, Adoption
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from pet import serializers as pet_serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema


class PetViewSet(viewsets.ModelViewSet):
    swagger_tags = ["pets"]
    pagination_class = PetsPagination
    http_method_names = ["get", "post", "patch", "delete", "head", "options", "trace"]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PetFilter
    search_fields = ["name", "category__name", "fees"]
    ordering_fields = ["fees", "updated_at"]

    @swagger_auto_schema(
        operation_summary="List my pets",
        operation_description=(
            "Retrieve a list of pets owned by the authenticated user.\n\n"
            "- Requires authentication.\n"
            "- Returns only the pets created by the logged-in user."
        ),
    )
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

    @swagger_auto_schema(
        operation_summary="List adopted pets",
        operation_description=(
            "Retrieve a list of pets adopted by the authenticated user.\n\n"
            "- Requires authentication.\n"
            "- Returns only the pets where the current user is marked as the adopter.\n"
            "- Supports pagination and filtering."
        ),
    )
    @action(detail=False, methods=["get"])
    def adopted(self, request, pk=None):
        queryset = self.filter_queryset(
            Pet.objects.select_related("category", "owner").filter(
                adopted_by=request.user
            )
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Retrieve pet details",
        operation_description=(
            "Retrieve details of a specific pet by ID.\n\n"
            "- **Owner or Admin**: Can always access their pet listing.\n"
            "- **Other users**: Can view details only if the pet is approved and public.\n"
            "- Returns 404 if access is restricted."
        ),
    )
    def retrieve(self, request, *args, **kwargs):
        pet = self.get_object()
        user = request.user
        print(user.is_staff)
        if (pet.owner == user) or (user.is_authenticated and user.is_staff):
            serializers = self.get_serializer(pet)
            return Response(serializers.data, status=status.HTTP_200_OK)

        if pet.status == Pet.APPROVED:
            serializers = self.get_serializer(pet)
            return Response(serializers.data, status=status.HTTP_200_OK)

        return Response({"details": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    def get_permissions(self):
        if self.action in ["my_pet"]:
            return [permissions.IsAuthenticated()]

        if self.action in ["partial_update", "destroy"]:
            return [permissions.IsAdminUser()]

        return [permissions.IsAuthenticatedOrReadOnly()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_serializer_class(self):
        if self.action == "partial_update":
            return pet_serializers.PetUpdateSerializer

        if self.action in ["my_pet"]:
            return pet_serializers.MyPetSerializer

        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return pet_serializers.AdminPetSerializer

        return pet_serializers.PetSerializer

    def get_queryset(self):

        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return Pet.objects.select_related("category", "owner")
        if self.action in ["retrieve"]:
            return Pet.objects.select_related("category", "owner")

        return Pet.objects.select_related("category", "owner").filter(
            status=Pet.APPROVED,
            visibility=Pet.PUBLIC,
        )

    @swagger_auto_schema(
        operation_summary="List pets",
        operation_description=(
            "Retrieve a list of pets.\n\n"
            "- **Admins**: Can view all pets.\n"
            "- **Regular users**: Only see pets with approved status and public visibility.\n"
            "- Supports filtering, search, ordering, and pagination."
        ),
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a pet listing",
        operation_description=(
            "Create a new pet listing.\n\n"
            "- Requires authentication.\n"
            "- The logged-in user will automatically be set as the owner of the pet."
        ),
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update pet details (partial)",
        operation_description=(
            "Partially update details of an existing pet listing.\n\n"
            "- Only admins are allowed to update pet records."
        ),
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a pet listing",
        operation_description=(
            "Delete a pet listing by ID.\n\n"
            "- Only admins are allowed to delete pet records."
        ),
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class AdoptionHistoryViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    swagger_tags = ["adoptions"]
    serializer_class = pet_serializers.AdoptionHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "head", "options", "trace"]

    pagination_class = AdoptionHistoryPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = AdoptionHistoryFilter
    ordering_fields = ["date", "id"]

    def get_queryset(self):
        if not self.request.user.is_staff:
            return Adoption.objects.none()
        pet_pk = self.kwargs.get("pets_pk")
        return Adoption.objects.select_related("pet", "adopted_by").filter(
            pet_id=pet_pk,
        )

    def perform_create(self, serializer):
        user = self.request.user
        pet = serializer.context["pet_instance"]

        with transaction.atomic():
            user.balance -= pet.fees  # type: ignore
            user.save(update_fields=["balance"])  # type: ignore
            serializer.save(pet_id=pet.pk, adopted_by=self.request.user)

    @swagger_auto_schema(
        operation_summary="List adoption histories",
        operation_description=(
            "Retrieve a list of adoption records for a specific pet.\n\n"
            "- Only admins can view adoption histories.\n"
            "- Supports filtering, ordering, and pagination."
        ),
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve adoption history by ID",
        operation_description=(
            "Fetch details of a specific adoption record by ID.\n\n"
            "- Only admins can retrieve adoption records."
        ),
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create an adoption record",
        operation_description=(
            "Create a new adoption history entry for a pet.\n\n"
            "- Requires authentication.\n"
            "- Automatically deducts the adoption fees from the adopter's balance.\n"
            "- Links the adoption record with the pet and the adopting user."
        ),
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
