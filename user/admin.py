from django.contrib import admin
from user.models import CustomUser

# Register your models here.


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = [
        "first_name",
        "last_name",
        "username",
        "email",
        "phone_number",
        "balance",
        "is_active",
    ]
    search_fields = ("username", "email", "first_name", "last_name")

    fieldsets = (
        (
            None,
            {
                "fields": ("username", "password"),
            },
        ),
        (
            "Personal Info:",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "balance",
                    "phone_number",
                )
            },
        ),
        (
            "Permissions:",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Important Dates:",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                )
            },
        ),
    )
