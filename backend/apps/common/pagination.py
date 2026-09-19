from rest_framework.pagination import PageNumberPagination


class OrbitePagination(PageNumberPagination):
    """Consistent pagination format across /api/v1 endpoints."""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100