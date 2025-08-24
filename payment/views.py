from traceback import print_tb
from django.http import HttpResponseRedirect
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from payment.fitlers import PaymentHistoryFilter
from payment.paginations import PaymentHistoryPagination
from payment.permissions import IsOwnerOrAdmin
from .models import PaymentHistory
from .serializers import (
    PaymentAdminHistorySerializer,
    PaymentHistorySerializer,
    PaymentInitSerializer,
)
import uuid
import time
from drf_yasg.utils import swagger_auto_schema
from django.conf import settings as main_settings
from sslcommerz_lib import SSLCOMMERZ
from decouple import config


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
        if self.action == "initiate":
            return PaymentInitSerializer
        if self.request.user.is_staff:
            return PaymentAdminHistorySerializer
        return PaymentHistorySerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # custom actions
    @swagger_auto_schema(
        operation_summary="List my pets",
        operation_description=(
            "Retrieve a list of pets owned by the authenticated user.\n\n"
            "- Requires authentication.\n"
            "- Returns only the pets created by the logged-in user."
        ),
    )
    @action(detail=False, methods=["post"])
    def initiate(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        amount = serializer.validated_data["amount"]
        transaction_id = f"TXN{int(time.time())}{uuid.uuid4().hex[:6]}"

        post_body = {}
        post_body["total_amount"] = amount
        post_body["currency"] = "BDT"
        post_body["tran_id"] = transaction_id
        post_body["success_url"] = (
            f"{main_settings.BACKEND_URL}/api/v1/payments/success/"
        )
        post_body["fail_url"] = f"{main_settings.BACKEND_URL}/api/v1/payments/fail/"
        post_body["cancel_url"] = f"{main_settings.BACKEND_URL}/api/v1/payments/cancel/"
        post_body["emi_option"] = 0
        post_body["cus_name"] = f"{user.first_name} {user.last_name}"
        post_body["cus_email"] = user.email
        post_body["cus_phone"] = user.phone_number
        post_body["cus_add1"] = "Unknown"
        post_body["cus_city"] = "Unknown"
        post_body["ship_name"] = "None"
        post_body["ship_add1"] = "None"
        post_body["ship_city"] = "None"
        post_body["ship_postcode"] = "None"
        post_body["ship_country"] = "None"
        post_body["cus_country"] = "Bangladesh"
        post_body["shipping_method"] = "Unknown"
        post_body["num_of_item"] = 1
        post_body["product_name"] = "Fund Adding"
        post_body["product_category"] = "General"
        post_body["product_profile"] = "general"
        settings = {
            "store_id": config("SSLCOMMERZ_STORE_ID", cast=str),
            "store_pass": config("SSLCOMMERZ_STORE_PASS", cast=str),
            "issandbox": True,
        }
        sslcz = SSLCOMMERZ(settings)
        response = sslcz.createSession(post_body)  # API response
        print(response)
        st = response.get("status")
        if st == "FAILED":
            return Response(
                {"details": "Payment Initiate failed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        url = response["GatewayPageURL"]

        PaymentHistory.objects.create(
            amount=amount,
            transaction_id=transaction_id,
            user=user,
        )

        return Response({"url": url}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="List my pets",
        operation_description=(
            "Retrieve a list of pets owned by the authenticated user.\n\n"
            "- Requires authentication.\n"
            "- Returns only the pets created by the logged-in user."
        ),
    )
    @action(detail=False, methods=["post"])
    def success(self, request, pk=None):
        with transaction.atomic():
            tran_id = request.data.get("tran_id")
            card_issuer = request.data.get("card_issuer")
            amount = request.data.get("amount")
            if amount is not None:
                try:
                    amount = float(amount)
                except ValueError:
                    amount = 0

            payment_history = PaymentHistory.objects.filter(transaction_id=tran_id)
            if not payment_history.exists():
                return Response(
                    {"data": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST
                )

            payment_history.update(
                status=PaymentHistory.SUCCESS, payment_method=card_issuer
            )

            user = request.user
            user.balance += amount
            user.save(update_fields=["balance"])

        return HttpResponseRedirect(
            f"{main_settings.FRONTEND_URL}/dashboard/payments/create?msg='Payment success!'"
        )

    @swagger_auto_schema(
        operation_summary="List my pets",
        operation_description=(
            "Retrieve a list of pets owned by the authenticated user.\n\n"
            "- Requires authentication.\n"
            "- Returns only the pets created by the logged-in user."
        ),
    )
    @action(detail=False, methods=["post"])
    def fail(self, request, pk=None):

        with transaction.atomic():
            tran_id = request.data.get("tran_id")
            card_issuer = request.data.get("card_issuer")

            payment_history = PaymentHistory.objects.filter(transaction_id=tran_id)
            if not payment_history.exists():
                return Response(
                    {"data": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST
                )

            payment_history.update(
                status=PaymentHistory.FAILED, payment_method=card_issuer
            )

        return HttpResponseRedirect(
            f"{main_settings.FRONTEND_URL}/dashboard/payments/create?msg='Payment failed!'"
        )

    @swagger_auto_schema(
        operation_summary="List my pets",
        operation_description=(
            "Retrieve a list of pets owned by the authenticated user.\n\n"
            "- Requires authentication.\n"
            "- Returns only the pets created by the logged-in user."
        ),
    )
    @action(detail=False, methods=["post"])
    def cancel(self, request, pk=None):
        with transaction.atomic():
            tran_id = request.data.get("tran_id")

            payment_history = PaymentHistory.objects.filter(transaction_id=tran_id)
            if not payment_history.exists():
                return Response(
                    {"data": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST
                )

            payment_history.update(status=PaymentHistory.CANCELLED)

        return HttpResponseRedirect(
            f"{main_settings.FRONTEND_URL}/dashboard/payments/create?msg='Payment cancelled!'"
        )

    # custom actions end

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
