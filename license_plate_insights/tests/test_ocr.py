import unittest
from unittest.mock import patch

from license_plate_insights.ocr import OCR


class TestOCR(unittest.TestCase):
    def setUp(self):
        self.ocr = OCR()

    @patch('google.cloud.vision.ImageAnnotatorClient')
    def test_extract_license_plate_text(self, mock_client):
        mock_client.return_value.text_detection.return_value.text_annotations = [{'description': 'ABC123'}]
        recognized_text = self.ocr.extract_license_plate_text('mock_roi')
        self.assertEqual(recognized_text, 'ABC123')

        mock_client.return_value.text_detection.return_value.text_annotations = []
        recognized_text = self.ocr.extract_license_plate_text('mock_roi')
        self.assertEqual(recognized_text, '')

        mock_client.return_value.text_detection.return_value.text_annotations = [{'description': 'XYZ789'}]
        recognized_text = self.ocr.extract_license_plate_text('mock_roi')
        self.assertEqual(recognized_text, 'XYZ789')

if __name__ == '__main__':
    unittest.main()
