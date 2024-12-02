from typing import Optional

from django.db.models import QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound

from .models import Handbook, HandbookVersion


class HandbookMixin:
    """
    Миксин для HandbookViewSet.
    """

    def get_handbook_or_404(
        self, pk: int, queryset: Optional[QuerySet[Handbook]]
    ) -> Handbook:
        """
        Получает справочник по его идентификатору или возвращает 404.

        :param queryset: Предзагруженный QuerySet справочников.
        :param pk: Идентификатор справочника.
        :return: Объект Handbook.
        :raises NotFound: Если справочник не найден.
        """
        queryset = queryset or self.get_queryset()  # type: ignore[assignment]
        try:
            return get_object_or_404(queryset, pk=pk)
        except Http404:
            raise NotFound({"error": "Handbook not found."})

    def get_version_or_404(
        self, handbook: Handbook, version_param: Optional[str]
    ) -> HandbookVersion:
        """
        Возвращает указанную версию справочника или текущую версию.

        :param handbook: Объект справочника.
        :param version_param: Версия справочника (если указана).
        :return: Объект HandbookVersion.
        :raises NotFound: Если указанная версия не найдена.
        """
        if version_param:
            try:
                return handbook.versions.get(version=version_param)
            except HandbookVersion.DoesNotExist:
                raise NotFound(
                    {"error": f"Version '{version_param}' not found for this handbook."}
                )
        else:
            version = handbook.get_latest_version()
            if not version:
                raise NotFound(
                    {"error": "No valid current version found for this handbook."}
                )
            return version
