from rest_framework import viewsets, permissions
from .models import Review
from .serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = (
        Review.objects.select_related("reviewer").prefetch_related("images").all()
    )
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        pet_pk = self.kwargs.get("pets_pk")
        return Review.objects.select_related("reviewer").filter(
            pet_id=pet_pk,
        )

    def perform_create(self, serializer):
        pet_pk = self.kwargs.get("pets_pk")
        serializer.save(reviewer=self.request.user, pet_id=pet_pk)
