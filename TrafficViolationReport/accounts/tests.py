import unittest
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import RequestFactory
from TrafficViolationReport.accounts.views import (create_user_profile,
                                                   send_verification_email,
                                                   verify)


class AccountsViewsTest(unittest.TestCase):
    def setUp(self):
        self.mock_user = MagicMock()
        self.mock_user.username = 'test_user'
        self.mock_user.email = 'test_user@example.com'
        self.mock_request = RequestFactory()
        self.mock_request.user = self.mock_user

    @patch('TrafficViolationReport.accounts.views.UserProfile.objects.create')
    def test_create_user_profile(self, mock_create):
        create_user_profile(self.mock_user)
        mock_create.assert_called_once_with(user=self.mock_user, email_verified_code=unittest.mock.ANY)

    @patch('TrafficViolationReport.accounts.views.send_mail')
    def test_send_verification_email(self, mock_send_mail):
        test_code = '123456'
        send_verification_email(self.mock_user, test_code)
        mock_send_mail.assert_called_once_with(
            subject="驗證您的帳戶",
            message="您的驗證碼是：{code}".format(code=test_code),
            from_email="trafficviolationtaiwan@gmail.com",
            recipient_list=[self.mock_user.email],
            fail_silently=False,
        )

    @patch('TrafficViolationReport.accounts.views.UserProfile.objects.get')
    @patch('TrafficViolationReport.accounts.views.redirect')
    def test_verify(self, mock_redirect, mock_get):
        test_code = '123456'
        self.mock_request.method = 'POST'
        self.mock_request.POST = {'code': test_code}
        verify(self.mock_request)
        mock_get.assert_called_once_with(user=self.mock_user, email_verified_code=test_code)
        mock_redirect.assert_called_once_with('login')

    def tearDown(self):
        del self.mock_user
        del self.mock_request
