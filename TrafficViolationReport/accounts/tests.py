from unittest.mock import MagicMock, patch

from django.test import RequestFactory, TestCase
from TrafficViolationReport.accounts.views import (handle_post_request, handle_get_request,
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
            if mock_request.method == 'POST':
                register_post_request(mock_request)
            else:
                register_get_request()

    @patch('TrafficViolationReport.accounts.views.send_mail')
    @patch('django.contrib.auth.get_user_model')
    @patch('TrafficViolationReport.accounts.views.send_verification_email')
    @patch('TrafficViolationReport.accounts.views.create_user_profile')
    @patch('TrafficViolationReport.accounts.views.validate_and_create_user')
    def test_register_email_already_exists(self, mock_validate_and_create_user, mock_create_user_profile, mock_send_verification_email, get_user_model):
        mock_form = self.mock_form_and_request(self.mock_request)
        mock_user_manager = MagicMock()
        mock_user_manager.filter.return_value.exists.return_value = True
        get_user_model.return_value.objects = mock_user_manager
        if self.mock_request.method == 'POST':
            self.patch_form_and_call_register(self.mock_request, mock_form)
        else:
            self.patch_form_and_call_register(self.mock_request, None)
        mock_create_user.assert_not_called()
        mock_create_user_profile.assert_not_called()
        mock_send_verification_email.assert_not_called()
    @patch('TrafficViolationReport.accounts.views.send_verification_email')
    @patch('TrafficViolationReport.accounts.views.create_user_profile')
    @patch('TrafficViolationReport.accounts.views.validate_and_create_user')
    def test_register_user_already_exists(self, mock_validate_and_create_user, mock_create_user_profile, mock_send_verification_email):
        mock_form = self.mock_form_and_request(self.mock_request)
        self.mock_user.exists.return_value = True
        self.patch_form_and_call_register(self.mock_request, mock_form)
        mock_create_user.assert_not_called()
        mock_create_user_profile.assert_not_called()
        mock_send_verification_email.assert_not_called()
    @patch('TrafficViolationReport.accounts.views.send_verification_email')
    @patch('TrafficViolationReport.accounts.views.create_user_profile')
    @patch('TrafficViolationReport.accounts.views.validate_and_create_user')
    def test_register_form_invalid(self, mock_validate_and_create_user, mock_create_user_profile, mock_send_verification_email):
        mock_form = self.mock_form_and_request(self.mock_request)
        mock_form.is_valid.return_value = False
        self.patch_form_and_call_register(self.mock_request, mock_form)
        mock_create_user.assert_not_called()
        mock_create_user_profile.assert_not_called()
        mock_send_verification_email.assert_not_called()
    @patch('TrafficViolationReport.accounts.views.send_verification_email')
    @patch('TrafficViolationReport.accounts.views.create_user_profile')
    @patch('TrafficViolationReport.accounts.views.validate_and_create_user')
    def test_register_success(self, mock_validate_and_create_user, mock_create_user_profile, mock_send_verification_email):
        mock_form = self.mock_form_and_request(self.mock_request)
        self.patch_form_and_call_register(self.mock_request, mock_form)
        mock_create_user.assert_called_once()
        mock_create_user_profile.assert_called_once()
        mock_send_verification_email.assert_called_once()
    @patch('TrafficViolationReport.accounts.views.authenticate_and_login_user')
    @patch('TrafficViolationReport.accounts.views.create_user_profile')
    @patch('TrafficViolationReport.accounts.views.validate_and_create_user')
    def test_handle_post_request(self, mock_validate_and_create_user, mock_create_user_profile, mock_authenticate_and_login_user):
        mock_request = RequestFactory().post('/fake-path')
        mock_form = MagicMock()
        with patch('TrafficViolationReport.accounts.views.CustomUserCreationForm', return_value=mock_form):
            response = handle_post_request(mock_request)

        mock_validate_and_create_user.assert_called_once_with(mock_request, mock_form)
        mock_create_user_profile.assert_called_once_with(mock_validate_and_create_user.return_value)
        mock_authenticate_and_login_user.assert_called_once_with(mock_request, mock_validate_and_create_user.return_value, mock_form)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'accounts:verify')
    def test_handle_get_request(self):
        response = handle_get_request()
        # Further assertions can be added once the expected behavior of handle_get_request is known

    @patch('TrafficViolationReport.accounts.views.create_user')
    @patch('TrafficViolationReport.accounts.views.create_user_profile')
    @patch('TrafficViolationReport.accounts.views.send_verification_email')
    def test_register(self, mock_send_verification_email, mock_create_user_profile, mock_validate_and_create_user):
        mock_form = self.mock_form_and_request(self.mock_request)
        self.patch_form_and_call_register(self.mock_request, mock_form)
        mock_create_user.assert_called_once_with(self.mock_request, mock_form)
        mock_create_user_profile.assert_called_once_with(self.mock_user)
