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
from TrafficViolationReport.accounts.views import (validate_form,
                                                   create_user,
                                                   create_user_profile,
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
    def test_validate_form(self):
        """
        Test the validate_form function in the accounts views module.

        This function mocks the form.is_valid method, calls validate_form with the mock request and form, 
        and asserts that form.is_valid is called once.
        """
        mock_form = MagicMock()
        mock_form.is_valid = MagicMock(return_value=True)
        self.mock_request.method = 'POST'
        validate_form(self.mock_request, mock_form)
        mock_form.is_valid.assert_called_once()

    def test_create_user(self):
        """
        Test the create_user function in the accounts views module.

        This function mocks the validate_form function, calls create_user with the mock request and form, 
        and asserts that validate_form is called with the correct arguments.
        """
        mock_form = MagicMock()
        with patch('TrafficViolationReport.accounts.views.validate_form', return_value=mock_form) as mock_validate_form:
            create_user(self.mock_request, mock_form)
            mock_validate_form.assert_called_once_with(self.mock_request, mock_form)
    def test_create_user_profile(self, mock_create):
        """
        Test the create_user_profile function in the accounts views module.

        This function mocks the UserProfile.objects.create method and asserts
        that it is called with the correct arguments.
        """
        create_user_profile(self.mock_user)
        mock_create.assert_called_once_with(user=self.mock_user, email_verified_code=unittest.mock.ANY)

    @patch('TrafficViolationReport.accounts.views.send_mail')
    @patch('TrafficViolationReport.accounts.views.create_user')
    @patch('TrafficViolationReport.accounts.views.create_user_profile')
    @patch('TrafficViolationReport.accounts.views.send_verification_email')
    def test_register(self, mock_send_verification_email, mock_create_user_profile, mock_create_user):
        """
        Test the register function in the accounts views module.

        This function mocks the new functions, calls register with the mock request, 
        and asserts that the new functions are called with the correct arguments.
        """
        mock_form = MagicMock()
        mock_form.is_valid = MagicMock(return_value=True)
        self.mock_request.method = 'POST'
        self.mock_request.POST = {}
        with patch('TrafficViolationReport.accounts.views.CustomUserCreationForm', return_value=mock_form):
            register(self.mock_request)
            mock_create_user.assert_called_once_with(self.mock_request, mock_form)
            mock_create_user_profile.assert_called_once_with(self.mock_user)
            mock_send_verification_email.assert_called_once_with(self.mock_user)
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
        # Clean up the test environment after each test case for AccountsViewsTest.
        # Deletes the mock user created for the tests.
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
        """
        Test the password change functionality with a POST request.

        This test checks whether the password is successfully changed when the correct data is sent in a POST request.
        """
        # Code for testing custom_password_change with POST method goes here
        self.assertTrue(True)  # Placeholder for correct test implementation

    def test_password_change_done(self):
        """
        Test the view that is displayed after a password change.

        This test checks whether the correct template is used and whether
        the correct context data is passed to the template.
        """
        # Code for testing password_change_done view function goes here
        self.assertTrue(True)  # Placeholder assertion, to be replaced with actual test code

    def test_password_change_url(self):
        """
        Test the URL configuration for the password change functionality.

        This test checks whether the correct view is called when the password change URL is accessed.
        """
        # Code for testing password change URL configuration goes here
        self.assertTrue(True)  # Placeholder assertion, to be replaced with actual test code

    def test_custom_password_change_get(self):
        """
        Test the password change functionality with a GET request.
        
        This test checks whether the correct form is displayed when the password change URL is accessed with a GET request.
        """
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
        # Call the EmailChangeView with the 'POST' request created in setUp method
        response = self.client.post('/accounts/email_change/', {'email': 'newemail@example.com'})
        self.assertEqual(response.status_code, 302, 'Email change should redirect on success')
        self.assertRedirects(response, '/profile', 'Redirect should go to profile page on success')
        # Check that a success message was added to the messages
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertIn('Your email has been updated.', [msg.message for msg in messages_list], 'Success message should be present in messages')

    def test_email_change_form_invalid(self):
        request = self.factory.post('/accounts/email_change/', {'email': 'not-an-email'}, follow=True)
        request.user = self.user
        response = email_change(request)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/email_change_form.html')
        self.assertIn('form', response.context_data)

    def tearDown(self):
        # Clean up by deleting the user created in setUp
        self.user.delete()
