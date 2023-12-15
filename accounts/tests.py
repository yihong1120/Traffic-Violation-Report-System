from django.test import TestCase, Client

# Create your tests here.

class LogoutViewTest(TestCase):
    """Test case for the LogoutView."""

    def setUp(self):
        self.client = Client()

    def test_logout_view(self):
        """Test the behavior of the logout view."""
        response = self.client.get('/logout/')
        self.assertEqual(response.status_code, 302)
