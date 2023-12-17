import unittest
from unittest.mock import MagicMock, patch

from django.db.models import QuerySet
from utils.mysql_utils import search_traffic_violations
from .utils import process_input


class MySqlUtilsTest(unittest.TestCase):
    def setUp(self):
        self.mock_traffic_violations = [MagicMock() for _ in range(3)]
        self.mock_query_set = MagicMock(spec=QuerySet)
        self.mock_query_set.filter.return_value = self.mock_traffic_violations

    @patch('utils.mysql_utils.TrafficViolation.objects.all', new_callable=MagicMock)
    def test_search_traffic_violations(self, mock_all):
        mock_all.return_value = self.mock_query_set
        result = search_traffic_violations('keyword', '1day')
        self.assertEqual(result, self.mock_traffic_violations)

        result = search_traffic_violations('keyword', 'custom', '2021-01-01', '2021-12-31')
        self.assertEqual(result, self.mock_traffic_violations)

        result = search_traffic_violations('', 'all')
        self.assertEqual(result, self.mock_traffic_violations)

        result = search_traffic_violations('keyword', '1day', '2021-01-01', '2021-12-31')
        self.assertEqual(result, self.mock_traffic_violations)


class TestProcessInput(unittest.TestCase):

    def test_process_input_with_address(self):
        address_input = '1600 Amphitheatre Parkway, Mountain View, CA'
        expected_output = (37.4224764, -122.0842499)
        output = process_input(address_input)
        self.assertEqual(output, expected_output)

    def test_process_input_with_coordinates(self):
        coordinates_input = '37.4224764,-122.0842499'
        expected_output = '1600 Amphitheatre Parkway, Mountain View, CA'
        output = process_input(coordinates_input)
        self.assertEqual(output, expected_output)

    def test_process_input_with_invalid_input(self):
        invalid_input = 'not a valid input'
        expected_output = 'not a valid input'
        output = process_input(invalid_input)
        self.assertEqual(output, expected_output)
