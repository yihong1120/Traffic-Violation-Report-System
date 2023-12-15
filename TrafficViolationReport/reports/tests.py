import unittest
from unittest.mock import MagicMock, patch

from utils.bigquery_utils import (get_media_records, get_user_records,
                                  update_media_files, update_traffic_violation)
from utils.mysql_utils import (get_media_records, get_user_records,
                               update_media_files, update_traffic_violation)
from utils.utils import MediaFile, ReportManager, TrafficViolation


class TrafficViolationReportTest(unittest.TestCase):
    def setUp(self):
        self.mock_user = MagicMock()
        self.mock_user.username = 'test_user'
        self.mock_traffic_violations = [MagicMock() for _ in range(3)]
        self.mock_media_files = [MagicMock() for _ in range(3)]

        for i, violation in enumerate(self.mock_traffic_violations):
            violation.traffic_violation_id = i
            violation.username = self.mock_user.username
            violation.media_files = [self.mock_media_files[i]]

    def tearDown(self):
        del self.mock_user
        del self.mock_traffic_violations
        del self.mock_media_files

    @patch('utils.bigquery_utils.get_user_records')
    @patch('utils.mysql_utils.get_user_records')
    def test_get_user_records(self, mock_mysql_get_user_records, mock_bigquery_get_user_records):
        mock_mysql_get_user_records.return_value = self.mock_traffic_violations
        mock_bigquery_get_user_records.return_value = self.mock_traffic_violations

        records = get_user_records(self.mock_user.username)
        self.assertEqual(records, self.mock_traffic_violations)

        mock_mysql_get_user_records.assert_called_once_with(self.mock_user.username)
        mock_bigquery_get_user_records.assert_called_once_with(self.mock_user.username)

    # Add more test cases as needed...
