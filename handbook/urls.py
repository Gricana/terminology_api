from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .schema import schema_view
from .views import HandbookViewSet

router = DefaultRouter()
router.register(r"refbooks", HandbookViewSet, basename="refbook")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "docs/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
]
