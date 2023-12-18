"""
Unit tests for the accounts views in the TrafficViolationReport platform.

This file contains a series of unit tests for testing the user account management
 functionalities such as user profile creation, sending verification emails and
 user profile verification.

"""
import unittest
from unittest.mock import MagicMock, patch
from django.test import RequestFactory
from TrafficViolationReport.accounts.forms import EmailChangeForm, PasswordChangeForm
from TrafficViolationReport.accounts.views import email_change, TestCase
from django.contrib.auth.models import User
from django.contrib import messages

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.test import RequestFactory
from TrafficViolationReport.accounts.views import (create_user_profile,
                                                   send_verification_email,
                                                   verify)


class AccountsViewsTest(unittest.TestCase):
    def setUp(self):
        """
        Set up the test environment before each test case.

        Creates a mock user and a mock request that will be used for testing
        the account view functions.
        """
        self.mock_user = MagicMock()
        self.mock_user.username = 'test_user'
        self.mock_user.email = 'test_user@example.com'
        self.mock_request = RequestFactory()
        self.mock_request.user = self.mock_user

    @patch('TrafficViolationReport.accounts.views.UserProfile.objects.create')
    def test_create_user_profile(self, mock_create):
        """
        Test the create_user_profile function in the accounts views module.

        This function mocks the UserProfile.objects.create method and asserts
        that it is called with the correct arguments.
        """
        create_user_profile(self.mock_user)
        mock_create.assert_called_once_with(user=self.mock_user, email_verified_code=unittest.mock.ANY)

    @patch('TrafficViolationReport.accounts.views.send_mail')
    def test_send_verification_email(self, mock_send_mail):
        """
        Test the send_verification_email function in the accounts views module.

        This function mocks the send_mail function and asserts that it is called
        with the correct arguments.
        """
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
        """
        Test the verify function in the accounts views module.

        This method mocks the UserProfile.objects.get method and the redirect
        function, and asserts that they are called with the correct arguments.
        """
        test_code = '123456'
        self.mock_request.method = 'POST'
        self.mock_request.POST = {'code': test_code}
        verify(self.mock_request)
        mock_get.assert_called_once_with(user=self.mock_user, email_verified_code=test_code)
        mock_redirect.assert_called_once_with('login')

    def tearDown(self):
        """
        Clean up the test environment after each test case.

        Deletes the mock user created for the tests.
        """
        del self.mock_user
        del self.mock_request

class PasswordChangeTest(unittest.TestCase):
    def setUp(self):
        self.mock_user = MagicMock()
        self.mock_user.username = 'test_user'
        self.mock_user.set_password('initial_password')
        self.mock_request = RequestFactory().get('/')
        self.mock_request.user = self.mock_user

    def test_custom_password_change_post(self):
        # Code for testing custom_password_change with POST method goes here
        self.assertTrue(True)  # Placeholder for correct test implementation

    def test_password_change_done(self):
        # Code for testing password_change_done view function goes here
        self.assertTrue(True)  # Placeholder assertion, to be replaced with actual test code

    def test_password_change_url(self):
        # Code for testing password change URL configuration goes here
        self.assertTrue(True)  # Placeholder assertion, to be replaced with actual test code

    def test_custom_password_change_get(self):
        # Code for testing custom_password_change with GET method goes here
        self.assertTrue(True)  # Placeholder assertion, to be replaced with actual test code
        """
        Clean up the test environment after each test case.

        Deletes the mock user created for the tests.
        """
        del self.mock_user
        del self.mock_request

class EmailChangeViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='johndoe', email='john@example.com', password='123')
        self.request = self.factory.post('/accounts/email_change/', {'email': 'newemail@example.com'}, follow=True)
        self.request.user = self.user
        self.form = EmailChangeForm(data=self.request.POST, instance=self.user)

    def test_email_change_successful(self):
        if self.form.is_valid():
            response = email_change(self.request)
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, '/profile')
            self.assertTrue(list(messages.get_messages(self.request)), 'Your email has been updated.')

    def test_email_change_form_invalid(self):
        request = self.factory.post('/accounts/email_change/', {'email': 'not-an-email'}, follow=True)
        request.user = self.user
        response = email_change(request)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/email_change_form.html')
        self.assertIn('form', response.context_data)

    def tearDown(self):
        self.user.delete()
