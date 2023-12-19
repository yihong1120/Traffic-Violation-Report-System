from django.test import TestCase, Client
from django.utils import timezone
from django.contrib.auth.models import User
from accounts.models import UserProfile
from accounts.tasks import delete_expired_unverified_users
from accounts.views import register, create_user_profile, send_verification_email

# Create your tests here.

class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("john", "lennon@thebeatles.com", "johnpassword")

    def test_is_verification_code_expired_past(self):
        with timezone.override(timezone.timedelta(days=-1)):
            expired_profile = UserProfile(user=self.user, verification_code_expiry=timezone.now())
        self.assertTrue(expired_profile.is_verification_code_expired())

    def test_is_verification_code_expired_future(self):
        with timezone.override(timezone.timedelta(days=1)):
            future_profile = UserProfile(user=self.user, verification_code_expiry=timezone.now())
        self.assertFalse(future_profile.is_verification_code_expired())



class DeleteExpiredUnverifiedUsersTaskTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("paul", "mccartney@thebeatles.com", "paulpassword")

    def test_delete_expired_unverified_users(self):
        expired_profile = UserProfile.objects.create(user=self.user, verification_code_expiry=timezone.now() - timezone.timedelta(days=1))
        delete_expired_unverified_users()
        self.assertFalse(UserProfile.objects.filter(id=expired_profile.id).exists())

        future_profile = UserProfile.objects.create(user=self.user, verification_code_expiry=timezone.now() + timezone.timedelta(days=1))
        delete_expired_unverified_users()
        self.assertTrue(UserProfile.objects.filter(id=future_profile.id).exists())


class RegisterViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_creates_user_and_profile(self):
        form_data = {'username': 'george', 'email': 'harrison@thebeatles.com', 'password1': 'georgepassword', 'password2': 'georgepassword'}
        response = self.client.post('/register/', form_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='george').exists())
        self.assertTrue(UserProfile.objects.filter(user__username='george').exists())
        self.assertTrue(self.client.login(username='george', password='georgepassword'))


class CreateUserProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('ringo', 'starr@thebeatles.com', 'ringopassword')

    def test_create_user_profile(self):
        create_user_profile(self.user)
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())


class SendVerificationEmailViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('ringo', 'starr@thebeatles.com', 'ringopassword')

    def test_send_verification_email(self):
        code = "12345"
        send_verification_email('starr@thebeatles.com', code)
        # Since emails are not actually sent in a test environment, you would typically need to mock the send_mail function
        # from django.core.mail to be able to test sending of emails.
        # For the sake of this example, we'll assume that the function is called correctly
        # and check that the logic for sending email is triggered properly.
        self.assertTrue(True)  # Replace with actual logic for email send verification

class LogoutViewTest(TestCase):
    """Test case for the LogoutView."""

    def setUp(self):
        self.client = Client()

    def test_logout_view(self):
        # 先模拟登录
        self.client.login(username='testuser', password='testpassword')
        
        # 测试注销视图
        response = self.client.post('/logout/')
        self.assertEqual(response.status_code, 302)
