from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from payment.fitlers import PaymentHistoryFilter
from payment.paginations import PaymentHistoryPagination
from payment.permissions import IsOwnerOrAdmin
from .models import PaymentHistory
from .serializers import PaymentAdminHistorySerializer, PaymentHistorySerializer


class PaymentHistoryViewSet(viewsets.ModelViewSet):
    swagger_tags = ["payments"]
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    http_method_names = ["get", "post", "head", "options"]
    pagination_class = PaymentHistoryPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PaymentHistoryFilter
    search_fields = ["pet__name"]
    ordering_fields = ["amount", "created_at"]

    def get_queryset(self):
        if self.request.user.is_staff:
            return PaymentHistory.objects.select_related("pet", "user").all()
        return PaymentHistory.objects.select_related("pet", "user").filter(
            user=self.request.user
        )

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return PaymentAdminHistorySerializer
        return PaymentHistorySerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
