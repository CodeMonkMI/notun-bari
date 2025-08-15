# admin.py
from django.contrib import admin
from .models import Pet, Adoption


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "status",
        "visibility",
        "owner",
    )
    list_filter = ("status", "visibility", "category", "created_at")
    search_fields = (
        "name",
        "owner__username",
        "adopted_by__username",
        "category__name",
    )
    ordering = ("-created_at",)
    readonly_fields = ("id", "created_at", "updated_at")
    autocomplete_fields = ("category", "owner", "adopted_by")


@admin.register(Adoption)
class AdoptionAdmin(admin.ModelAdmin):
    list_display = ("id", "pet", "adopted_by", "date")
    list_filter = ("date",)
    search_fields = ("pet__name", "adopted_by__username")
    ordering = ("-date",)
    readonly_fields = ("id",)
    autocomplete_fields = ("pet", "adopted_by")
