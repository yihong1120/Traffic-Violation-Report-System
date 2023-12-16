import unittest
from unittest.mock import MagicMock, patch

from django.db.models import QuerySet
from utils.mysql_utils import search_traffic_violations


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
