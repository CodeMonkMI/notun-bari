from rest_framework.pagination import PageNumberPagination


class PetsPagination(PageNumberPagination):
    page_size = 10


class AdoptionHistoryPagination(PageNumberPagination):
    page_size = 10
