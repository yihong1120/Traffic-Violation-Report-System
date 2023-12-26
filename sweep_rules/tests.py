import unittest
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import RequestFactory
from reports.models import TrafficViolation
from sweep_rules.models import SweepRule
from sweep_rules.views import (apply_sweep_rule, create_sweep_rule,
                               delete_sweep_rule)


class SweepRulesTest(unittest.TestCase):
    def setUp(self):
        self.mock_user = MagicMock(spec=User)
        self.mock_sweep_rule = MagicMock(spec=SweepRule)
        self.mock_traffic_violation = MagicMock(spec=TrafficViolation)
        self.mock_request = RequestFactory()

    @patch('sweep_rules.views.create_sweep_rule')
    def test_create_sweep_rule(self, mock_create_sweep_rule):
        self.mock_request.user = self.mock_user
        create_sweep_rule(self.mock_request)
        mock_create_sweep_rule.assert_called_once()

    @patch('sweep_rules.views.apply_sweep_rule')
    def test_apply_sweep_rule(self, mock_apply_sweep_rule):
        self.mock_request.user = self.mock_user
        apply_sweep_rule(self.mock_request, self.mock_sweep_rule.id)
        mock_apply_sweep_rule.assert_called_once_with(self.mock_user, self.mock_sweep_rule.id)

    @patch('sweep_rules.views.delete_sweep_rule')
    def test_delete_sweep_rule(self, mock_delete_sweep_rule):
        self.mock_request.user = self.mock_user
        delete_sweep_rule(self.mock_request, self.mock_sweep_rule.id)
        mock_delete_sweep_rule.assert_called_once_with(self.mock_user, self.mock_sweep_rule.id)

    def tearDown(self):
        del self.mock_user
        del self.mock_sweep_rule
        del self.mock_traffic_violation
        del self.mock_request
