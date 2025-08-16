from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "pet",
        "reviewer",
        "short_comment",
        "created_at",
        "updated_at",
    )
    list_filter = ("created_at", "updated_at", "pet")
    search_fields = ("comments", "reviewer__username", "pet__name")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")

    # Custom method to shorten long comments
    def short_comment(self, obj):
        return obj.comments[:50] + "..." if len(obj.comments) > 50 else obj.comments

    short_comment.short_description = "Comment"
