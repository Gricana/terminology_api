from typing import Dict

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Handbook API",
        default_version='v1',
        description="API для работы со справочниками.",
        contact=openapi.Contact(email="contact@example.com"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny, ],
)
# Схема для получения списка справочников
list_handbooks_schema: Dict = {
    'operation_description': "Возвращает список всех справочников, "
                             "с возможностью фильтрации "
                             "по дате начала действия версии.",
    'operation_id': "list_handbooks",
    'responses': {
        200: openapi.Response(
            description="Список справочников",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'refbooks': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(
                                    type=openapi.TYPE_INTEGER),
                                'code': openapi.Schema(
                                    type=openapi.TYPE_STRING),
                                'name': openapi.Schema(
                                    type=openapi.TYPE_STRING)
                            }
                        )
                    )
                }
            ),
            examples={
                "application/json": {
                    "refbooks": [
                        {"id": 1, "code": "Код справочника 1",
                         "name": "Наименование справочника 1"},
                        {"id": 2, "code": "Код справочника 2",
                         "name": "Наименование справочника 2"}
                    ]
                }
            }
        ),
        400: openapi.Response(
            description="Неверный формат даты",
            examples={
                'application/json': {
                    'error': 'Invalid date format. Use YYYY-MM-DD.'}
            }
        )
    },
    'manual_parameters': [
        openapi.Parameter('date', openapi.IN_QUERY,
                          description="Дата фильтрации справочников",
                          type=openapi.TYPE_STRING)
    ]
}

# Схема для получения элементов справочника
get_handbook_elements_schema: Dict = {
    'operation_description': "Возвращает элементы справочника по "
                             "указанной версии или текущей версии.",
    'operation_id': "get_handbook_elements",
    'responses': {
        200: openapi.Response(
            description="Список элементов справочника",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'elements': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'code': openapi.Schema(
                                    type=openapi.TYPE_STRING),
                                'value': openapi.Schema(
                                    type=openapi.TYPE_STRING)
                            }
                        )
                    )
                }
            ),
            examples={
                "application/json": {
                    "elements": [
                        {"code": "element_1", "value": "Значение 1"},
                        {"code": "element_2", "value": "Значение 2"}
                    ]
                }
            }
        ),
        404: openapi.Response(
            description="Элемент или версия не найдены",
            examples={
                "application/json": [
                    {"error": "Handbook not found."},
                    {"error": "Version {version} not found for this handbook."}
                ]
            }
        )
    },
    'manual_parameters': [
        openapi.Parameter('id', openapi.IN_PATH,
                          description="Идентификатор справочника",
                          type=openapi.TYPE_STRING),
        openapi.Parameter('version', openapi.IN_QUERY,
                          description="Версия справочника для получения элементов",
                          type=openapi.TYPE_STRING)
    ]
}

# Схема для проверки существования элемента
check_element_schema: Dict = {
    'operation_description': "Проверяет наличие элемента "
                             "с указанным кодом и значением в указанной версии.",
    'operation_id': "check_element_exists",
    'responses': {
        200: openapi.Response(
            description="Элемент существует",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'exists': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                }
            ),
            examples={"application/json": {"exists": True}}
        ),
        400: openapi.Response(
            description="Неверно указаны параметры",
            examples={
                "application/json": {
                    "error": "Parameters 'code' and 'value' are required."}
            }
        ),
        404: openapi.Response(
            description="Элемент или версия не найдены",
            examples={
                "application/json": [
                    {"error": "Handbook not found."},
                    {"error": "Version {version} not found for this handbook."}
                ]
            }
        )
    },
    'manual_parameters': [
        openapi.Parameter('id', openapi.IN_PATH,
                          description="Идентификатор справочника",
                          type=openapi.TYPE_STRING),
        openapi.Parameter('code', openapi.IN_QUERY,
                          description="Код элемента справочника",
                          type=openapi.TYPE_STRING),
        openapi.Parameter('value', openapi.IN_QUERY,
                          description="Значение элемента",
                          type=openapi.TYPE_STRING),
        openapi.Parameter('version', openapi.IN_QUERY,
                          description="Версия справочника",
                          type=openapi.TYPE_STRING)
    ]
}
