import unittest
from unittest.mock import MagicMock

from sweep_rules.business_logic import function1, function2, function3


class SweepRulesBusinessLogicTest(unittest.TestCase):
    def setUp(self):
        self.mock_user = MagicMock()
        self.mock_traffic_violation = MagicMock()
        self.mock_sweep_rule = MagicMock()

    def test_function1(self):
        result = function1(self.mock_user, self.mock_traffic_violation, self.mock_sweep_rule)
        self.assertEqual(result, expected_result)
        self.mock_user.assert_called_once_with(expected_args)
        self.mock_traffic_violation.assert_called_once_with(expected_args)
        self.mock_sweep_rule.assert_called_once_with(expected_args)

    def test_function2(self):
        result = function2(self.mock_user, self.mock_traffic_violation, self.mock_sweep_rule)
        self.assertEqual(result, expected_result)
        self.mock_user.assert_called_once_with(expected_args)
        self.mock_traffic_violation.assert_called_once_with(expected_args)
        self.mock_sweep_rule.assert_called_once_with(expected_args)

    def test_function3(self):
        result = function3(self.mock_user, self.mock_traffic_violation, self.mock_sweep_rule)
        self.assertEqual(result, expected_result)
        self.mock_user.assert_called_once_with(expected_args)
        self.mock_traffic_violation.assert_called_once_with(expected_args)
        self.mock_sweep_rule.assert_called_once_with(expected_args)

    def tearDown(self):
        del self.mock_user
        del self.mock_traffic_violation
        del self.mock_sweep_rule
