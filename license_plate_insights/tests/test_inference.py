import unittest
from unittest.mock import patch, Mock
import numpy as np

from license_plate_insights.inference import CarLicensePlateDetector


class TestCarLicensePlateDetector(unittest.TestCase):
    def setUp(self):
        self.detector = CarLicensePlateDetector('mock_weights_path')

    @patch('license_plate_insights.inference.ImageProcessor.draw_text')
    @patch('license_plate_insights.object_detection.ObjectDetector.recognize_license_plate')
    def test_recognize_license_plate(self, mock_recognize_license_plate_object, mock_draw_text):
        # Create a mock image
        mock_image = np.zeros((640, 480, 3), dtype=np.uint8)

        # Define test scenarios
        test_scenarios = [
            {
                'recognize_output': ('ABC123', (50, 50, 200, 200)),
                'draw_output': mock_image,
                'expected_result': ('ABC123', mock_image)
            },
            {
                'recognize_output': ('', (50, 50, 200, 200)),
                'draw_output': mock_image,
                'expected_result': ('', mock_image)
            }
        ]

        # Test different scenarios
        for scenario in test_scenarios:
            with self.subTest(scenario=scenario):
                mock_recognize_license_plate_object.return_value = scenario['recognize_output']
                mock_draw_text.return_value = scenario['draw_output']
                result = self.detector.recognize_license_plate(mock_image)
                self.assertEqual(result, scenario['expected_result'])

    @patch('license_plate_insights.inference.CarLicensePlateDetector.draw_text')
    def test_draw_text_on_image(self, mock_draw_text):
        mock_draw_text.return_value = 'mock_image_with_text'
        output_image = self.detector.draw_text('mock_image', 'mock_text', (0, 0))
        self.assertEqual(output_image, 'mock_image_with_text')

if __name__ == '__main__':
    unittest.main()
