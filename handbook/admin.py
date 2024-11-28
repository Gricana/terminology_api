from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.utils.translation import gettext_lazy as _

from .models import Handbook, HandbookVersion, HandbookElement


class HandbookVersionInline(admin.TabularInline):
    """
    Встраиваемая модель для версии справочника в админке.
    Используется для отображения и редактирования версий справочников
    прямо из интерфейса справочников.
    """
    model = HandbookVersion
    extra = 1
    fields = ['version', 'start_date']


@admin.register(Handbook)
class HandbookAdmin(admin.ModelAdmin):
    """
    Админ-класс для модели Handbook (Справочник).
    Управляет отображением справочников в админке.
    """
    list_display = ['get_id', 'code', 'name',
                    'current_version', 'current_version_date']
    search_fields = ['code', 'name']
    inlines = [HandbookVersionInline]

    def get_id(self, obj: Handbook) -> int:
        """
        Получить ID справочника.
        """
        return obj.id

    get_id.short_description = _('ID')

    def current_version(self, obj: Handbook) -> str:
        """
        Получить текущую версию справочника.
        """
        return obj.get_current_version()

    current_version.short_description = _('Current Version')

    def current_version_date(self, obj: Handbook) -> str:
        """
        Получить дату начала текущей версии справочника.
        """
        return obj.get_current_version_date()

    current_version_date.short_description = _('Current Version Date')


class HandbookElementInline(admin.TabularInline):
    """
    Встраиваемая модель для элементов справочника в админке.
    Используется для отображения и редактирования элементов справочников.
    """
    model = HandbookElement
    extra = 1
    fields = ['code', 'value']


@admin.register(HandbookVersion)
class HandbookVersionAdmin(admin.ModelAdmin):
    """
    Админ-класс для модели HandbookVersion (Версия справочника).
    Управляет отображением версий справочников в админке.
    """
    list_display = ['get_handbook__code', 'get_handbook__name', 'version',
                    'start_date']
    search_fields = ['handbook__code', 'handbook__name', 'version']
    inlines = [HandbookElementInline]

    def get_handbook__code(self, obj: HandbookVersion) -> str:
        """
        Получить код справочника для данной версии.
        """
        return obj.handbook.code

    get_handbook__code.short_description = _("Handbook code")

    def get_handbook__name(self, obj: HandbookVersion) -> str:
        """
        Получить название справочника для данной версии.
        """
        return obj.handbook.name

    get_handbook__name.short_description = _("Handbook name")


@admin.register(HandbookElement)
class HandbookElementAdmin(admin.ModelAdmin):
    """
    Админ-класс для модели HandbookElement (Элемент справочника).
    Управляет отображением элементов справочников в админке.
    """
    list_display = ['version', 'code', 'value']


# Убираем модели User и Group из админки.
admin.site.unregister(User)
admin.site.unregister(Group)

admin.site.site_header = _('Terminology service')
