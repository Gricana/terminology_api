from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.utils.dateparse import parse_date
from django.utils.translation import gettext_lazy as _
from django_filters import Filter
from django_filters import rest_framework as filters

from .models import Handbook, HandbookElement


class DateFilter(Filter):
    """
    Фильтр для обработки даты с пользовательской ошибкой при неверном формате.

    Если дата имеет неверный формат, генерируется ошибка с пояснением.
    """

    def filter(self, qs, value) -> QuerySet[Handbook]:
        """
        Фильтрует переданный QuerySet по дате.
        Если дата имеет неверный формат,
        выбрасывается исключение ValidationError с пользовательским сообщением.

        :param qs: QuerySet для фильтрации
        :param value: строковое значение даты
        :return: отфильтрованный QuerySet
        :raises ValidationError: если формат даты некорректен
        """
        if value in [None, ""]:
            return qs
        try:
            parsed_date = parse_date(value)
            if not parsed_date:
                raise ValidationError(
                    _("Invalid date format. Use 'YYYY-MM-DD'."), code="invalid_date"
                )
            return super().filter(qs, parsed_date)
        except ValidationError as e:
            self.field.error_messages.update({"invalid": e})
            raise e


class HandbookFilter(filters.FilterSet):
    """
    Фильтр для модели Handbook.
    """

    date = DateFilter(
        field_name="versions__start_date", lookup_expr="lte", label="Date (YYYY-MM-DD)"
    )

    class Meta:
        model = Handbook
        fields = ["date"]


class HandbookElementFilter(filters.FilterSet):
    """
    Фильтр для модели HandbookElement,
    который позволяет фильтровать элементы справочников
    по коду, значению и версии.
    """

    code = filters.CharFilter(lookup_expr="iexact", required=True)
    value = filters.CharFilter(lookup_expr="icontains", required=True)
    version = filters.CharFilter(
        field_name="version__version", lookup_expr="exact", required=False
    )

    class Meta:
        model = HandbookElement
        fields = ["code", "value", "version"]
