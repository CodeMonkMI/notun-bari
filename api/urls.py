from django.urls import include, path, re_path
from rest_framework.routers import SimpleRouter
from category.views import CategoryViewSet

router = SimpleRouter()
router.register("categories", CategoryViewSet, basename="category")


urlpatterns = [
    path(r"", include(router.urls)),
    re_path(r"^auth/", include("djoser.urls")),
    re_path(r"^auth/", include("djoser.urls.jwt")),
]
