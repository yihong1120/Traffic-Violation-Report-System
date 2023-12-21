import unittest
from unittest.mock import patch

from license_plate_insights.inference import CarLicensePlateDetector


class TestCarLicensePlateDetector(unittest.TestCase):
    def setUp(self):
        self.detector = CarLicensePlateDetector('mock_weights_path')

    @patch('license_plate_insights.inference.CarLicensePlateDetector.recognize_license_plate')
    def test_recognize_license_plate(self, mock_recognize_license_plate):
        mock_recognize_license_plate.return_value = 'ABC123', None
        recognized_text, _ = self.detector.recognize_license_plate('mock_image_path')
        self.assertEqual(recognized_text, 'ABC123')

        mock_recognize_license_plate.return_value = '', None
        recognized_text, _ = self.detector.recognize_license_plate('mock_image_path')
        self.assertEqual(recognized_text, '')

    @patch('license_plate_insights.inference.CarLicensePlateDetector.draw_text')
    def test_draw_text_on_image(self, mock_draw_text):
        mock_draw_text.return_value = 'mock_image_with_text'
        output_image = self.detector.draw_text('mock_image', 'mock_text', (0, 0))
        self.assertEqual(output_image, 'mock_image_with_text')

if __name__ == '__main__':
    unittest.main()
