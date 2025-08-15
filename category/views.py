from rest_framework import viewsets
from rest_framework.permissions import AllowAny  # adjust as needed

from category.models import Category
from category.paginations import CategoryPagination
from category.serializers import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):

    queryset = Category.objects.all().order_by("name")
    permission_classes = [AllowAny]
    serializer_class = CategorySerializer
    pagination_class = CategoryPagination
