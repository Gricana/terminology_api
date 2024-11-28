from typing import Optional, List

from django.utils.dateparse import parse_date
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

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

    def get_queryset(self) -> List[Handbook]:
        """
        Возвращает список всех справочников.
        """
        return Handbook.objects.all()

    def filter_by_date(self, date_param: Optional[str]) -> List[Handbook]:
        """
        Фильтрует QuerySet по дате начала действия версий.

        :param date_param: дата для фильтрации в формате YYYY-MM-DD
        :return: отфильтрованный QuerySet
        :raises ValueError: если формат даты неверен
        """
        if not date_param:
            return self.queryset

        parsed_date = parse_date(date_param)
        if parsed_date:
            return self.queryset.filter(
                versions__start_date__lte=parsed_date
            ).distinct()

        raise ValueError("Invalid date format. Use YYYY-MM-DD.")

    @swagger_auto_schema(**list_handbooks_schema)
    def list(self, request, *args, **kwargs) -> Response:
        """
        Возвращает список справочников.
        Может фильтровать справочники по дате начала действия версии.
        """
        queryset = self.get_queryset()
        date_param = request.query_params.get('date')

        try:
            if date_param:
                queryset = self.filter_by_date(date_param)
        except ValueError as e:
            return Response({"error": str(e)},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(queryset, many=True)
        return Response({'refbooks': serializer.data})

    @swagger_auto_schema(auto_schema=None)
    def retrieve(self, request, *args, **kwargs):
        """
        Метод извлечния конкретного справочника удалён из схемы Swagger
        """
        super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(**get_handbook_elements_schema)
    @action(detail=True, methods=['get'], url_path='elements')
    def elements(self, request, pk=None) -> Response:
        """
        Возвращает элементы справочника по указанной или текущей версии.
        """
        handbook = self.get_handbook_or_404(pk)
        version = self.get_version_or_404(handbook,
                                          request.query_params.get('version'))
        elements = self.get_elements_for_version(version)

        serializer = HandbookElementSerializer(elements, many=True)
        return Response({"elements": serializer.data})

    def get_handbook_or_404(self, pk: int) -> Handbook:
        """
        Получает справочник по его идентификатору или возвращает 404.

        :param pk: Идентификатор справочника
        :return: объект справочника Handbook
        :raises NotFound: если справочник не найден
        """
        try:
            return Handbook.objects.get(pk=pk)
        except Handbook.DoesNotExist:
            raise NotFound({"error": "Handbook not found."})

    def get_version_or_404(self, handbook: Handbook,
                           version_param: Optional[str]) -> HandbookVersion:
        """
        Возвращает указанную версию справочника или текущую версию.

        :param handbook: справочник
        :param version_param: строковый параметр версии, если указан
        :return: объект версии справочника
        :raises NotFound: если версия не найдена
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

    def get_elements_for_version(self, version: HandbookVersion) \
            -> List[HandbookElement]:
        """
        Возвращает элементы для указанной версии справочника.

        :param version: версия справочника
        :return: список элементов справочника
        """
        return HandbookElement.objects.filter(version=version)

    @swagger_auto_schema(**check_element_schema)
    @action(detail=True, methods=['get'], url_path='check_element')
    def check_element(self, request, pk=None) -> Response:
        """
        Проверяет наличие элемента с указанным кодом и значением в указанной версии.

        :param request: запрос
        :param pk: идентификатор справочника
        :return: ответ с результатом проверки
        """
        code = request.query_params.get('code')
        value = request.query_params.get('value')
        version_param = request.query_params.get('version')

        if not code or not value:
            return Response(
                {"error": "Parameters 'code' and 'value' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        handbook = self.get_handbook_or_404(pk)
        version = self.get_version_or_404(handbook, version_param)
        exists = self.check_element_exists(version, code, value)

        return Response({"exists": exists}, status=status.HTTP_200_OK)

    def check_element_exists(self, version: HandbookVersion,
                             code: str, value: str) -> bool:
        """
        Проверяет, существует ли элемент с данным кодом и значением в данной версии.

        :param version: версия справочника
        :param code: код элемента
        :param value: значение элемента
        :return: True, если элемент существует, иначе False
        """
        return HandbookElement.objects.filter(version=version, code=code,
                                              value__icontains=value).exists()
