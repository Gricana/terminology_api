from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


class HandbookViewSetTests(TestCase):
    """
    Тест-кейсы для работы со справочниками и их версиями.
    """
    fixtures = ['test_data.json']

    def setUp(self) -> None:
        """
        Подготавливает клиент API для выполнения запросов.
        """
        self.client = APIClient()

    def test_list_handbooks(self) -> None:
        """
        Тестирует запрос на получение списка всех справочников.
        Ожидается, что вернется 2 справочника, и один из них будет с кодом 'ICD10'.
        """
        url = reverse('refbook-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refbooks', response.data)
        self.assertEqual(len(response.data['refbooks']), 2)
        self.assertEqual(response.data['refbooks'][0]['code'], 'ICD10')

    def test_filter_handbooks_by_date(self) -> None:
        """
        Тестирует фильтрацию справочников по дате.
        Ожидается, что вернется 1 справочник для даты '2021-06-01'.
        """
        url = reverse('refbook-list')
        params = {'date': '2021-06-01'}
        response = self.client.get(url, data=params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refbooks', response.data)
        self.assertEqual(len(response.data['refbooks']), 1)

    def test_filter_handbooks_by_invalid_date_format(self) -> None:
        """
        Тестирует фильтрацию по дате с некорректным форматом даты.
        Ожидается ошибка с кодом 400 и сообщением о неверном формате даты.
        """
        url = reverse('refbook-list')
        params = {'date': '2022.31.12'}
        response = self.client.get(url, data=params)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'],
                         'Invalid date format. Use YYYY-MM-DD.')

    def test_filter_handbooks_by_date_with_no_results(self) -> None:
        """
        Тестирует фильтрацию по дате, когда для указанной даты нет справочников.
        Ожидается, что вернется пустой список справочников для даты '2020-01-01'.
        """
        url = reverse('refbook-list')
        params = {'date': '2020-01-01'}
        response = self.client.get(url, data=params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refbooks', response.data)
        self.assertEqual(len(response.data['refbooks']), 0)

    def test_get_handbook_elements_for_current_version(self) -> None:
        """
        Тестирует получение элементов справочника для текущей версии.
        Ожидается, что вернется 3 элемента, первый из которых будет иметь код 'A00'.
        """
        url = reverse('refbook-elements', args=[1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('elements', response.data)
        self.assertEqual(len(response.data['elements']), 3)
        self.assertEqual(response.data['elements'][0]['code'], 'A00')

    def test_get_handbook_elements_for_specific_version(self) -> None:
        """
        Тестирует получение элементов справочника для конкретной версии.
        Ожидается, что вернется 3 элемента для версии '2022'.
        """
        url = reverse('refbook-elements', args=[1])
        params = {'version': '2022'}
        response = self.client.get(url, data=params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('elements', response.data)
        self.assertEqual(len(response.data['elements']), 3)
        self.assertEqual(response.data['elements'][0]['value'], 'Холера')

    def test_check_element_exists(self) -> None:
        """
        Тестирует проверку наличия элемента в справочнике по коду и значению.
        Ожидается, что элемент с кодом 'A00' и значением 'Холера (обновлено)'
        существует в версии '2023'.
        """
        url = reverse('refbook-check-element', args=[1])
        params = {
            'code': 'A00',
            'value': 'Холера (обновлено)',
            'version': '2023'
        }
        response = self.client.get(url, data=params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('exists', response.data)
        self.assertTrue(response.data['exists'])

    def test_check_element_not_exists(self) -> None:
        """
        Тестирует проверку отсутствия элемента в справочнике.
        Ожидается, что элемент с кодом 'A00' и значением 'Холера'
        не существует в версии '2023'.
        """
        url = reverse('refbook-check-element', args=[2])
        params = {
            'code': 'A00',
            'value': 'Холера',
            'version': '2023'
        }
        response = self.client.get(url, data=params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('exists', response.data)
        self.assertFalse(response.data['exists'])

    def test_invalid_handbook_id(self) -> None:
        """
        Тестирует запрос с некорректным ID справочника.
        Ожидается ошибка 404, если справочник с ID 999 не существует.
        """
        url = reverse('refbook-elements', args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], "Handbook not found.")

    def test_invalid_version(self) -> None:
        """
        Тестирует запрос на несуществующую версию справочника.
        Ожидается ошибка 404, если версия '2025' не существует.
        """
        url = reverse('refbook-elements', args=[1])
        params = {'version': '2025'}
        response = self.client.get(url, data=params)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'],
                         f"Version '{params['version']}' not found for this handbook.")

    def test_missing_code_or_value_in_check_element(self) -> None:
        """
        Тестирует запрос без обязательных параметров 'code' или 'value' в проверке элемента.
        Ожидается ошибка 400 с сообщением о недостающих параметрах.
        """
        url = reverse('refbook-check-element', args=[1])
        params = {'code': 'A00'}
        response = self.client.get(url, data=params)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'],
                         "Parameters 'code' and 'value' are required.")
