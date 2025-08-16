from rest_framework import viewsets, permissions
from review.fitlers import ReviewFilter
from review.paginations import ReviewPagination
from .models import Review
from .serializers import ReviewSerializer, ReviewUpdateSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .permissions import IsOwnerOrAdmin


class ReviewViewSet(viewsets.ModelViewSet):
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
