from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from license_plate_insights.image_processing import ImageProcessor
from license_plate_insights.object_detection import ObjectDetector
from license_plate_insights.ocr import OCR
import numpy as np

class LicensePlateInsightsTests(TestCase):

    def test_object_detector(self):
        detector = ObjectDetector('path/to/weights')
        img = np.zeros((640, 480, 3), dtype=np.uint8)
        results = detector.recognize_license_plate(img)
        self.assertTrue(isinstance(results, list), 'ObjectDetector did not return a list.')
        self.assertGreater(len(results), 0, 'ObjectDetector did not detect any objects.')

    def test_ocr(self):
        ocr = OCR()
        roi = np.zeros((80, 250, 3), dtype=np.uint8)  # Simulated region of interest for OCR
        text = ocr.extract_license_plate_text(roi)
        self.assertTrue(isinstance(text, str), 'OCR did not return a string.')
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
        # Check response content (placeholder assertion to be updated according to implementation)
        self.assertTrue('license_plate' in response.json(), 'License plate data not found in response.')
        print(response.content)
