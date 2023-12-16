import unittest
from unittest.mock import MagicMock, patch

from django.http import JsonResponse
from django.test import RequestFactory
from traffic_data.views import (search_traffic_violations_view,
                                traffic_violation_details_view,
                                traffic_violation_markers_view)


class TrafficDataViewTest(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.mock_search_traffic_violations = MagicMock()
        self.mock_get_traffic_violation_markers = MagicMock()
        self.mock_get_traffic_violation_details = MagicMock()

    @patch('traffic_data.views.search_traffic_violations', new_callable=MagicMock)
    def test_search_traffic_violations_view(self, mock_search_traffic_violations):
        mock_search_traffic_violations.return_value = self.mock_search_traffic_violations
        request = self.factory.get('/search_traffic_violations_view')
        response = search_traffic_violations_view(request)
        self.assertIsInstance(response, JsonResponse)

    @patch('traffic_data.views.get_traffic_violation_markers', new_callable=MagicMock)
    def test_traffic_violation_markers_view(self, mock_get_traffic_violation_markers):
        mock_get_traffic_violation_markers.return_value = self.mock_get_traffic_violation_markers
        request = self.factory.get('/traffic_violation_markers_view')
        response = traffic_violation_markers_view(request)
        self.assertIsInstance(response, JsonResponse)

    @patch('traffic_data.views.get_traffic_violation_details', new_callable=MagicMock)
    def test_traffic_violation_details_view(self, mock_get_traffic_violation_details):
        mock_get_traffic_violation_details.return_value = self.mock_get_traffic_violation_details
        request = self.factory.get('/traffic_violation_details_view')
        response = traffic_violation_details_view(request, 'test_id')
        self.assertIsInstance(response, JsonResponse)
