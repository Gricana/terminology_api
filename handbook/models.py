from datetime import date
from typing import Optional

from django.db import models
from django.utils.translation import gettext_lazy as _


class Handbook(models.Model):
    """
    Модель для справочника (Handbook).
    Хранит информацию о справочниках, такую как код, наименование и описание.
    """

    code = models.CharField(verbose_name=_("Code"), max_length=100, unique=True)
    name = models.CharField(verbose_name=_("Name"), max_length=300)
    description = models.TextField(verbose_name=_("Description"), blank=True)

    class Meta:
        verbose_name = _("Handbook")
        verbose_name_plural = _("Handbooks")

    def get_latest_version(self) -> Optional["HandbookVersion"]:
        """
        Получить последнюю версию справочника, которая действительна на сегодняшний день.
        Кэширует результат, чтобы избежать повторных запросов.
        """
        if not hasattr(self, "_cached_latest_version"):
            if hasattr(self, "prefetched_versions"):
                self._cached_latest_version = self.prefetched_versions[0]
            else:
                self._cached_latest_version = self.versions.filter(
                    start_date__lte=date.today()
                ).first()
        return self._cached_latest_version

    def get_current_version(self) -> Optional[str]:
        """
        Получить текущую версию справочника.
        """
        latest_version = self.get_latest_version()
        return latest_version.version if latest_version else None

    def get_current_version_date(self) -> Optional[str]:
        """
        Получить дату начала действия текущей версии справочника.
        """
        latest_version = self.get_latest_version()
        return latest_version.start_date if latest_version else None

    def __str__(self) -> str:
        """
        Возвращает строковое представление справочника (код - наименование).
        """
        return f"{self.code} - {self.name}"


class HandbookVersion(models.Model):
    """
    Модель для версии справочника (HandbookVersion).
    Хранит информацию о версии справочника, включая дату начала действия.
    """

    handbook = models.ForeignKey(
        Handbook,
        on_delete=models.CASCADE,
        related_name="versions",
        verbose_name=_("Handbook"),
    )
    version = models.CharField(verbose_name=_("Handbook Version"), max_length=50)
    start_date = models.DateField(verbose_name=_("Start date"))

    class Meta:
        ordering = ("-start_date",)
        unique_together = ("handbook", "version")
        constraints = [
            models.UniqueConstraint(
                fields=["handbook", "start_date"], name="unique_version_start_date"
            )
        ]
        verbose_name = _("Handbook Version")
        verbose_name_plural = _("Handbook Versions")

    def __str__(self) -> str:
        """
        Возвращает строковое представление версии справочника.
        """
        return f"{self.handbook.name} - v{self.version}"


class HandbookElement(models.Model):
    """
    Модель для элемента справочника (HandbookElement).
    Хранит информацию об элементах справочника для каждой версии,
    включая код и значение.
    """

    version = models.ForeignKey(
        HandbookVersion,
        on_delete=models.CASCADE,
        related_name="elements",
        verbose_name=_("Handbook Version"),
    )
    code = models.CharField(verbose_name=_("Element code"), max_length=100)
    value = models.CharField(verbose_name=_("Element value"), max_length=300)

    class Meta:
        unique_together = ("version", "code")
        verbose_name = _("Handbook Element")
        verbose_name_plural = _("Handbook Elements")

    def __str__(self) -> str:
        """
        Возвращает строковое представление элемента справочника.
        """
        return f"{self.code} - {self.value}"
