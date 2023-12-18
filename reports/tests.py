"""
This file contains unit tests for the Traffic Violation Report system,
specifically for the functions in the `utils` module.
"""
import unittest
from unittest.mock import MagicMock, patch

from utils.bigquery_utils import (get_media_records, get_user_records,
                                  update_media_files, update_traffic_violation)
from utils.mysql_utils import (get_media_records, get_user_records,
                               update_media_files, update_traffic_violation)
from utils.utils import MediaFile, ReportManager, TrafficViolation
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from unittest.mock import patch
from reports.views import edit_report, dashboard
from reports.forms import ReportForm
from reports.models import TrafficViolation, MediaFile


class TrafficViolationReportTest(unittest.TestCase):
    """
    This class contains unit tests for the Traffic Violation Report system.
    """
    def setUp(self):
        """
        This method sets up the test environment by initializing mock user, traffic violations, and media files.
        """
        """
        Part of the unittest.TestCase setup. Initializes mock user, traffic violations,
        and media files for the tests.
        """
        self.mock_user = MagicMock()
        self.mock_user.username = 'test_user'
        self.mock_traffic_violations = [MagicMock() for _ in range(3)]
        self.mock_media_files = [MagicMock() for _ in range(3)]

        for i, violation in enumerate(self.mock_traffic_violations):
            violation.traffic_violation_id = i
            violation.username = self.mock_user.username
            violation.media_files = [self.mock_media_files[i]]

    @patch('reports.models.MediaFile')
    @patch('reports.models.TrafficViolation')
    @patch('reports.forms.ReportForm')
    def test_dashboard_post(self, mock_ReportForm, mock_TrafficViolation, mock_MediaFile):
        """
        This method tests the POST request to the dashboard view.
        """
        mock_request = RequestFactory().post('/dashboard', data={})
        mock_request.user = self.mock_user
        mock_ReportForm.is_valid.return_value = True
        mock_ReportForm.return_value.cleaned_data = {
            'license_plate': 'ABC123',
            'date': '2021-04-01',
            'time': '14:30',
            'violation': 'Speeding',
            'status': 'Reported',
            'location': 'Test Location',
            'officer': 'Officer Name'
        }

        dashboard(mock_request)

        mock_TrafficViolation.assert_called_once_with(
            license_plate='ABC123',
            date='2021-04-01',
            time='14:30',
            violation='Speeding',
            status='Reported',
            location='Test Location',
            officer='Officer Name',
            username='test_user'
        )
        mock_TrafficViolation.return_value.save.assert_called_once()
        self.assertTrue(mock_MediaFile.objects.create.called)

    @patch('reports.views.ReportManager.get_record_form_and_media')
    @patch('utils.mysql_utils.get_user_records')
    def test_edit_report(self, mock_get_user_records, mock_get_record_form_and_media):
        """
        This method tests the GET request to the edit report view.
        """
        mock_request = RequestFactory().get('/edit_report')
        mock_request.user = self.mock_user
        mock_get_user_records.return_value = self.mock_traffic_violations
        mock_get_record_form_and_media.return_value = (MagicMock(), ReportForm(), [MagicMock()])

        response = edit_report(mock_request)

        self.assertEqual(response.context_data['user_records'], self.mock_traffic_violations)
        self.assertIsInstance(response.context_data['selected_record'], MagicMock)
        self.assertIsInstance(response.context_data['form'], ReportForm)

    def tearDown(self):
        """
        This method cleans up the test environment by deleting the mock user, traffic violations, and media files.
        """
        """
        Part of the unittest.TestCase teardown. Deletes the mock user, traffic violations,
        and media files after each test.
        """
        del self.mock_user
        del self.mock_traffic_violations
        del self.mock_media_files

    @patch('utils.bigquery_utils.get_user_records')
    @patch('utils.mysql_utils.get_user_records')
    def test_get_user_records(self, mock_mysql_get_user_records, mock_bigquery_get_user_records):
        """
        This method tests the `get_user_records` function.
        """
        mock_mysql_get_user_records.return_value = self.mock_traffic_violations
        mock_bigquery_get_user_records.return_value = self.mock_traffic_violations

        records = get_user_records(self.mock_user.username)
        self.assertEqual(records, self.mock_traffic_violations)

        mock_mysql_get_user_records.assert_called_once_with(self.mock_user.username)
        mock_bigquery_get_user_records.assert_called_once_with(self.mock_user.username)

    @patch('reports.views.dashboard')
    def test_dashboard_get(self, mock_dashboard):
        """
        This method tests the GET request to the dashboard view.
        """
        mock_request = RequestFactory().get('/dashboard')
        mock_request.user = self.mock_user

        response = dashboard(mock_request)

        self.assertIsInstance(response.context['form'], ReportForm)
    
    # Add more test cases as needed...
