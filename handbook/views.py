from typing import Optional, List

from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response

from .filters import HandbookFilter, HandbookElementFilter
from .models import Handbook, HandbookElement, HandbookVersion
from .schema import *
from .serializers import HandbookSerializer, HandbookElementSerializer


class HandbookViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для работы со справочниками.
    Позволяет получать список справочников,
    а также работать с элементами справочников по версиям.
    """
    serializer_class = HandbookSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = HandbookFilter

    def get_queryset(self) -> List[Handbook]:
        """
        Возвращает базовый QuerySet справочников с оптимизацией связанных данных.
        """
        return Handbook.objects.all().prefetch_related('versions').distinct()

    @swagger_auto_schema(**list_handbooks_schema)
    def list(self, request, *args, **kwargs) -> Response:
        """
        Возвращает список справочников с поддержкой фильтрации и сортировки.
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response({'refbooks': serializer.data})
        except DjangoValidationError as e:
            raise ValidationError({"error": e.message})

    @swagger_auto_schema(auto_schema=None)
    def retrieve(self, request, *args, **kwargs):
        """
        Метод извлечения конкретного справочника удалён из схемы Swagger.
        """
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(**get_handbook_elements_schema)
    @action(detail=True, methods=['get'], url_path='elements')
    def elements(self, request, pk=None) -> Response:
        """
        Возвращает элементы справочника по указанной или текущей версии.
        """
        version_param = request.query_params.get('version')

        handbook = self.get_handbook_or_404(pk)
        version = self.get_version_or_404(handbook, version_param)

        elements = version.elements.all()

        serializer = HandbookElementSerializer(elements, many=True)
        return Response({"elements": serializer.data})

    @swagger_auto_schema(**check_element_schema)
    @action(detail=True, methods=['get'], url_path='check_element')
    def check_element(self, request, pk=None) -> Response:
        """
        Проверяет наличие элемента с указанным кодом и значением в указанной версии.
        """
        handbook = self.get_handbook_or_404(pk)
        version_param = request.query_params.get('version')
        version = self.get_version_or_404(handbook, version_param)

        queryset = HandbookElement.objects.filter(version=version)
        filterset = HandbookElementFilter(request.GET, queryset=queryset)

        if not filterset.is_valid():
            return Response(filterset.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        exists = filterset.qs.exists()
        return Response({"exists": exists}, status=status.HTTP_200_OK)

    def get_handbook_or_404(self, pk: int) -> Handbook:
        """
        Получает справочник по его идентификатору или возвращает 404.
        """
        try:
            return self.get_object()
        except Http404:
            raise NotFound({"error": "Handbook not found."})

    def get_version_or_404(self, handbook: Handbook,
                           version_param: Optional[str]) -> HandbookVersion:
        """
        Возвращает указанную версию справочника или текущую версию.
        """
        if version_param:
            try:
                return handbook.versions.get(version=version_param)
            except HandbookVersion.DoesNotExist:
                raise NotFound({
                    "error": f"Version '{version_param}' not found for this handbook."
                })
        else:
            version = handbook.get_latest_version()
            if not version:
                raise NotFound({
                    "error": "No valid current version found for this handbook."
                })
            return version
