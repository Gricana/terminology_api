from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.utils.translation import gettext_lazy as _

from .models import Handbook, HandbookElement, HandbookVersion


class HandbookVersionInline(admin.TabularInline):
    """
    Встраиваемая модель для версии справочника в админке.
    Используется для отображения и редактирования версий справочников
    прямо из интерфейса справочников.
    """

    model = HandbookVersion
    extra = 1
    fields = ["version", "start_date"]


@admin.register(Handbook)
class HandbookAdmin(admin.ModelAdmin):
    """
    Админ-класс для модели Handbook (Справочник).
    Управляет отображением справочников в админке.
    """

    list_display = ["get_id", "code", "name", "current_version", "current_version_date"]
    search_fields = ["code", "name"]
    list_display_links = ["code"]
    inlines = [HandbookVersionInline]

    @admin.display(description=_("ID"))
    def get_id(self, obj: Handbook) -> int:
        """
        Получить ID справочника.
        """
        return obj.id

    @admin.display(description=_("Current Version"))
    def current_version(self, obj: Handbook) -> str:
        """
        Получить текущую версию справочника.
        """
        return obj.get_current_version()

    @admin.display(description=_("Current Version Date"))
    def current_version_date(self, obj: Handbook) -> str:
        """
        Получить дату начала текущей версии справочника.
        """
        return obj.get_current_version_date()


class HandbookElementInline(admin.TabularInline):
    """
    Встраиваемая модель для элементов справочника в админке.
    Используется для отображения и редактирования элементов справочников.
    """

    model = HandbookElement
    extra = 1
    fields = ["code", "value"]


@admin.register(HandbookVersion)
class HandbookVersionAdmin(admin.ModelAdmin):
    """
    Админ-класс для модели HandbookVersion (Версия справочника).
    Управляет отображением версий справочников в админке.
    """

    list_display = ["handbook_code", "handbook_name", "version", "start_date"]
    search_fields = ["handbook__code", "handbook__name", "version"]
    inlines = [HandbookElementInline]

    @admin.display(description=_("Handbook code"))
    def handbook_code(self, obj: HandbookVersion) -> str:
        """
        Получить код справочника для данной версии.
        """
        return obj.handbook.code

    @admin.display(description=_("Handbook name"))
    def handbook_name(self, obj: HandbookVersion) -> str:
        """
        Получить название справочника для данной версии.
        """
        return obj.handbook.name


@admin.register(HandbookElement)
class HandbookElementAdmin(admin.ModelAdmin):
    """
    Админ-класс для модели HandbookElement (Элемент справочника).
    Управляет отображением элементов справочников в админке.
    """

    list_display = ["version", "code", "value"]


# Убираем модели User и Group из админки.
admin.site.unregister(User)
admin.site.unregister(Group)

admin.site.site_header = _("Terminology service")
