import unittest
from unittest.mock import patch

from license_plate_insights.object_detection import ObjectDetector


class TestObjectDetector(unittest.TestCase):
    def setUp(self):
        self.detector = ObjectDetector('mock_weights_path')

    @patch('license_plate_insights.object_detection.ObjectDetector.recognize_license_plate')
    def test_recognize_license_plate(self, mock_recognize_license_plate):
        mock_recognize_license_plate.return_value = 'ABC123', None
        recognized_text, _ = self.detector.recognize_license_plate('mock_image_path')
        self.assertEqual(recognized_text, 'ABC123')

        mock_recognize_license_plate.return_value = '', None
        recognized_text, _ = self.detector.recognize_license_plate('mock_image_path')
        self.assertEqual(recognized_text, '')

        mock_recognize_license_plate.return_value = 'XYZ789', None
        recognized_text, _ = self.detector.recognize_license_plate('mock_image_path')
        self.assertEqual(recognized_text, 'XYZ789')

if __name__ == '__main__':
    unittest.main()
