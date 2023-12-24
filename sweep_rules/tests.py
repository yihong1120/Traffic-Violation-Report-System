import unittest
from unittest.mock import MagicMock

from django.test import RequestFactory
from sweep_rules.models import SweepRule
from sweep_rules.views import apply_sweep_rule


class SweepRulesTest(unittest.TestCase):
    def setUp(self):
        self.mock_user = MagicMock()
        self.mock_user.username = 'test_user'
        self.mock_request = RequestFactory()
        self.mock_request.user = self.mock_user
        self.mock_sweep_rule = MagicMock()

    def test_apply_sweep_rule(self):
        apply_sweep_rule(self.mock_request, self.mock_sweep_rule)
        self.mock_sweep_rule.apply.assert_called_once_with(self.mock_user)

    def tearDown(self):
        del self.mock_user
        del self.mock_request
        del self.mock_sweep_rule
