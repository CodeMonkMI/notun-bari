from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from payment.fitlers import PaymentHistoryFilter
from payment.paginations import PaymentHistoryPagination
from payment.permissions import IsOwnerOrAdmin
from .models import PaymentHistory
from .serializers import PaymentAdminHistorySerializer, PaymentHistorySerializer
from drf_yasg.utils import swagger_auto_schema


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

    @swagger_auto_schema(
        operation_summary="List payment histories",
        operation_description=(
            "Retrieve a list of payment history records.\n\n"
            "- **Admins/Librarians**: Can view all records.\n"
            "- **Regular Users**: Can only view their own payment history."
        ),
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a payment history record",
        operation_description=(
            "Add a new payment history entry. "
            "The authenticated user will automatically be assigned as the owner. "
            "Accessible by all authenticated users."
        ),
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve payment history by ID",
        operation_description=(
            "Fetch details of a specific payment history record by ID.\n\n"
            "- **Admins**: Can view any record.\n"
            "- **Regular Users**: Can only access their own records."
        ),
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
