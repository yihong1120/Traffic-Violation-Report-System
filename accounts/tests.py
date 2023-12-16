from django.test import TestCase, Client

# Create your tests here.

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
