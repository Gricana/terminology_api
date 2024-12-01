from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class HandbookConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "handbook"
    verbose_name = _("Handbook")
