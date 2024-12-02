from typing import Optional

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .filters import HandbookElementFilter, HandbookFilter
from .mixins import HandbookMixin
from .models import Handbook, HandbookElement
from .schema import (
    check_element_schema,
    get_handbook_elements_schema,
    list_handbooks_schema,
)
from .serializers import HandbookElementSerializer, HandbookSerializer


class HandbookViewSet(HandbookMixin, viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для работы со справочниками.
    Позволяет получать список справочников,
    а также работать с элементами справочников по версиям.
    """

    serializer_class = HandbookSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = HandbookFilter

    def get_queryset(self) -> QuerySet[Handbook]:
        """
        Возвращает QuerySet справочников с оптимизацией связанных данных.

        :return: QuerySet справочников и связанные с ними версии.
        """
        return Handbook.objects.all().prefetch_related("versions").distinct()

    @swagger_auto_schema(**list_handbooks_schema)
    def list(self, request, *args, **kwargs) -> Response:
        """
        Возвращает список справочников с поддержкой фильтрации.
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response({"refbooks": serializer.data})
        except DjangoValidationError as e:
            raise ValidationError({"error": e.message})

    @swagger_auto_schema(auto_schema=None)
    def retrieve(self, request, *args, **kwargs):
        """
        Метод извлечения конкретного справочника.
        Удалён из схемы Swagger.
        """
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(**get_handbook_elements_schema)
    @action(detail=True, methods=["get"], url_path="elements")
    def elements(self, request, pk=None) -> Response:
        """
        Возвращает элементы справочника по указанной или текущей версии.

        :param pk: Идентификатор справочника.
        :return: Ответ в JSON с элементами справочника.
        """
        elements = self.get_elements_by_version(request, pk)
        serializer = HandbookElementSerializer(elements, many=True)
        return Response({"elements": serializer.data})

    @swagger_auto_schema(**check_element_schema)
    @action(detail=True, methods=["get"], url_path="check_element")
    def check_element(self, request, pk=None) -> Response:
        """
        Проверяет наличие элемента с указанным кодом и значением в указанной версии.

        :param pk: Идентификатор справочника.
        :return: Ответ в JSON с ключом "exists", указывающим на наличие элемента.
        """
        elements = self.get_elements_by_version(request, pk)
        filterset = HandbookElementFilter(request.GET, queryset=elements)

        if not filterset.is_valid():
            return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)

        exists = filterset.qs.exists()
        return Response({"exists": exists}, status=status.HTTP_200_OK)

    def get_elements_by_version(
        self, request, pk: Optional[int]
    ) -> QuerySet[HandbookElement]:
        """
        Получает элементы справочника для указанной или текущей версии.

        :param pk: Идентификатор справочника.
        :return: QuerySet элементов справочника.
        """
        version_param = request.query_params.get("version")
        handbook = self.get_handbook_or_404(pk)
        version = self.get_version_or_404(handbook, version_param)
        return version.elements.all()
