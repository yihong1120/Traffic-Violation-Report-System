import unittest
from unittest.mock import MagicMock, patch

from django.test import RequestFactory
from TrafficViolationReport.accounts.views import (create_user,
                                                   create_user_profile,
                                                   register,
                                                   send_verification_email,
                                                   validate_form, verify)


class TestValidateForm(unittest.TestCase):
    def setUp(self):
        self.mock_user = MagicMock()
        self.mock_user.username = 'test_user'
        self.mock_user.email = 'test_user@example.com'
        self.mock_request = RequestFactory()
        self.mock_request.user = self.mock_user

    @patch('TrafficViolationReport.accounts.views.UserProfile.objects.create')
    def test_validate_form(self):
        mock_form = MagicMock()
        mock_form.is_valid = MagicMock(return_value=True)
        self.mock_request.method = 'POST'
        validate_form(self.mock_request, mock_form)
        mock_form.is_valid.assert_called_once()

class TestCreateUser(unittest.TestCase):
    def setUp(self):
        self.mock_user = MagicMock()
        self.mock_user.username = 'test_user'
        self.mock_user.email = 'test_user@example.com'
        self.mock_request = RequestFactory()
        self.mock_request.user = self.mock_user

    def test_create_user(self):
        mock_form = MagicMock()
        with patch('TrafficViolationReport.accounts.views.validate_form', return_value=mock_form) as mock_validate_form:
            create_user(self.mock_request, mock_form)
            mock_validate_form.assert_called_once_with(self.mock_request, mock_form)

class TestCreateUserProfile(unittest.TestCase):
    def setUp(self):
        self.mock_user = MagicMock()
        self.mock_user.username = 'test_user'
        self.mock_user.email = 'test_user@example.com'

    def test_create_user_profile(self, mock_create):
        create_user_profile(self.mock_user)
        mock_create.assert_called_once_with(user=self.mock_user, email_verified_code=unittest.mock.ANY)

# Continue with other test classes...
