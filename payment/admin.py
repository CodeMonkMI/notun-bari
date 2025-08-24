from django.contrib import admin
from .models import PaymentHistory


@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "transaction_id",
        "user",
        "pet",
        "amount",
        "payment_method",
        "status",
        "payment_type",
        "created_at",
    )
    list_filter = ("status", "payment_type", "payment_method", "created_at")
    search_fields = ("transaction_id", "user__username", "pet__name")
    ordering = ("-created_at",)
    readonly_fields = ("id", "transaction_id", "created_at", "updated_at")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "transaction_id",
                    "user",
                    "pet",
                    "amount",
                    "payment_method",
                    "status",
                    "payment_type",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
            },
        ),
    )
