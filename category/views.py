from rest_framework import viewsets
from rest_framework.permissions import AllowAny  # adjust as needed
from drf_yasg.utils import swagger_auto_schema
from category.models import Category
from category.paginations import CategoryPagination
from category.serializers import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    swagger_tags = ["categories"]
    queryset = Category.objects.all().order_by("name")
    permission_classes = [AllowAny]
    serializer_class = CategorySerializer
    pagination_class = CategoryPagination

    @swagger_auto_schema(
        operation_summary="List categories",
        operation_description=(
            "Retrieve a paginated list of all categories.\n\n"
            "- Publicly accessible (no authentication required).\n"
            "- Results are ordered alphabetically by name."
        ),
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a category",
        operation_description=(
            "Create a new category with the provided information.\n\n"
            "- Publicly accessible (no authentication required).\n"
            "- Useful for adding new category entries."
        ),
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve category details",
        operation_description=(
            "Fetch details of a single category by ID.\n\n"
            "- Publicly accessible (no authentication required)."
        ),
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update category (partial)",
        operation_description=(
            "Partially update the details of a category by ID.\n\n"
            "- Publicly accessible (no authentication required).\n"
            "- Only provided fields will be updated."
        ),
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a category",
        operation_description=(
            "Delete a category by ID.\n\n"
            "- Publicly accessible (no authentication required)."
        ),
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
