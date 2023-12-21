from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

class LicensePlateInsightsTests(TestCase):
    def test_upload_file(self):
        # 准备测试文件
        with open('images/image1.jpg', 'rb') as file:
            uploaded_file = SimpleUploadedFile(name='test.jpg', content=file.read(), content_type='image/jpeg')

        # 准备测试请求
        url = reverse('license_plate_insights:upload_file')  # 确保您在urls.py中设置了命名空间和URL名称
        response = self.client.post(url, {'file': uploaded_file})

        # 检查响应
        self.assertEqual(response.status_code, 200)
        # 这里可以添加更多的断言来检查响应内容

        # 打印响应（可选）
        print(response.content)
