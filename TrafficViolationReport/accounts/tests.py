from unittest.mock import MagicMock, patch

from django.test import RequestFactory, TestCase
from TrafficViolationReport.accounts.views import (create_user,
                                                   create_user_profile,
                                                   register,
                                                   send_verification_email)


class AccountsViewsTest(TestCase):
    def setUp(self):
        self.mock_user = MagicMock()
        self.mock_user.username = 'test_user'
        self.mock_user.email = 'test_user@example.com'
        self.mock_request = RequestFactory()
        self.mock_request.user = self.mock_user

    def mock_form_and_request(self, mock_request):
        mock_form = MagicMock()
        mock_form.is_valid = MagicMock(return_value=True)
        mock_request.method = 'POST'
        mock_request.POST = {}
        return mock_form

    def patch_form_and_call_register(self, mock_request, mock_form):
        with patch('TrafficViolationReport.accounts.views.CustomUserCreationForm', return_value=mock_form):
            register(mock_request)

    @patch('TrafficViolationReport.accounts.views.send_mail')
    @patch('TrafficViolationReport.accounts.views.create_user')
    @patch('TrafficViolationReport.accounts.views.create_user_profile')
    @patch('TrafficViolationReport.accounts.views.send_verification_email')
    def test_register(self, mock_send_verification_email, mock_create_user_profile, mock_create_user):
        mock_form = self.mock_form_and_request(self.mock_request)
        self.patch_form_and_call_register(self.mock_request, mock_form)
        mock_create_user.assert_called_once_with(self.mock_request, mock_form)
        mock_create_user_profile.assert_called_once_with(self.mock_user)
