from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, permissions
from review.fitlers import ReviewFilter
from review.paginations import ReviewPagination
from .models import Review
from .serializers import ReviewSerializer, ReviewUpdateSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .permissions import IsOwnerOrAdmin


class ReviewViewSet(viewsets.ModelViewSet):
    swagger_tags = ["reviews"]
    queryset = (
        Review.objects.select_related("reviewer").prefetch_related("images").all()
    )

    pagination_class = ReviewPagination
    http_method_names = ["get", "post", "patch", "delete", "head", "options", "trace"]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ReviewFilter
    ordering_fields = ["fees", "updated_at"]

    def get_permissions(self):
        if self.action in ["create", "partial_update", "destroy"]:
            return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]
        return [permissions.IsAuthenticatedOrReadOnly()]

    def get_serializer_class(self):
        if self.action in ["partial_update"]:
            return ReviewUpdateSerializer
        return ReviewSerializer

    def get_queryset(self):
        pet_pk = self.kwargs.get("pets_pk")
        return Review.objects.select_related("reviewer").filter(
            pet_id=pet_pk,
        )

    def perform_create(self, serializer):
        pet_pk = self.kwargs.get("pets_pk")
        serializer.save(reviewer=self.request.user, pet_id=pet_pk)

    @swagger_auto_schema(
        operation_summary="List reviews",
        operation_description=(
            "Retrieve a list of reviews for a specific pet.\n\n"
            "- **Unauthenticated users**: Can view reviews (read-only).\n"
            "- **Authenticated users**: Can view all reviews.\n"
            "- Supports filtering, ordering, and pagination."
        ),
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a review",
        operation_description=(
            "Submit a new review for a pet.\n\n"
            "- Requires authentication.\n"
            "- The logged-in user will be automatically assigned as the reviewer.\n"
            "- The review will be linked to the pet identified by `pets_pk`."
        ),
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve a review by ID",
        operation_description=(
            "Fetch the details of a specific review by its ID.\n\n"
            "- Accessible to all (read-only).\n"
            "- Includes reviewer information and related images."
        ),
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update a review (partial)",
        operation_description=(
            "Partially update details of an existing review by ID.\n\n"
            "- Requires authentication.\n"
            "- Only the review owner or an admin can update the review."
        ),
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a review",
        operation_description=(
            "Delete a review by ID.\n\n"
            "- Requires authentication.\n"
            "- Only the review owner or an admin can delete the review."
        ),
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
