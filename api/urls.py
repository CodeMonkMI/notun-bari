from codecs import lookup
from django.urls import include, path, re_path
from rest_framework.routers import SimpleRouter
from category.views import CategoryViewSet
from rest_framework_nested.routers import NestedSimpleRouter
from pet.views import AdoptionHistoryViewSet, PetViewSet

router = SimpleRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("pets", PetViewSet, basename="pets")

pet_router = NestedSimpleRouter(router, "pets", lookup="pets")
pet_router.register("adoptions", AdoptionHistoryViewSet, basename="adoptions")


urlpatterns = [
    path(r"", include(router.urls)),
    path(r"", include(pet_router.urls)),
    re_path(r"^auth/", include("djoser.urls")),
    re_path(r"^auth/", include("djoser.urls.jwt")),
]
