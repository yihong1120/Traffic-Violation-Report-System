from django.test import TestCase, Client

# Create your tests here.

class LogoutViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_logout_view(self):
        response = self.client.get('/logout/')
        self.assertEqual(response.status_code, 302)
