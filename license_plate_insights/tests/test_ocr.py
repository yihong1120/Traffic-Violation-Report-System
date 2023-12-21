import unittest
from unittest.mock import patch, MagicMock
import numpy as np
from google.cloud import vision
from google.protobuf.json_format import ParseDict

from license_plate_insights.ocr import OCR


class TestOCR(unittest.TestCase):
    def setUp(self):
        """
        Sets up the test case by creating an instance of OCR.
        """
        self.ocr = OCR()

    @patch('google.cloud.vision.ImageAnnotatorClient')
    def test_extract_license_plate_text(self, mock_client):
        """
        Tests the extract_license_plate_text method of the OCR class.
        """
        mock_client.return_value.text_detection.return_value.text_annotations = [{'description': 'ABC123'}]
        recognized_text = self.ocr.extract_license_plate_text('mock_roi')
        self.assertEqual(recognized_text, 'ABC123')

        mock_client.return_value.text_detection.return_value.text_annotations = []
        recognized_text = self.ocr.extract_license_plate_text('mock_roi')
        self.assertEqual(recognized_text, '')

        mock_client.return_value.text_detection.return_value.text_annotations = [{'description': 'XYZ789'}]
        recognized_text = self.ocr.extract_license_plate_text('mock_roi')
        self.assertEqual(recognized_text, 'XYZ789')

    @patch('license_plate_insights.ocr.vision.ImageAnnotatorClient')
    def test_extract_license_plate_text_success(self, mock_vision_client):
        # Setup test data and mock responses
        mock_roi = np.random.rand(100, 100, 3) * 255
        mock_roi = mock_roi.astype(np.uint8)
        text_annotation_dict = {'description': 'ABC123'}
        text_annotation = ParseDict(text_annotation_dict, vision.TextAnnotation())
        response_dict = {'text_annotations': [text_annotation], 'error': {'message': ''}}
        response = ParseDict(response_dict, vision.AnnotateImageResponse())

        # Expected success response from Google Vision text_detection
        mock_vision_client.return_value.text_detection.return_value = response

        # Call method under test
        recognized_text = self.ocr.extract_license_plate_text(mock_roi)
        self.assertEqual(recognized_text, 'ABC123')

    @patch('license_plate_insights.ocr.vision.ImageAnnotatorClient')
    def test_extract_license_plate_text_no_text(self, mock_vision_client):
        # Setup test data and mock responses
        mock_roi = np.random.rand(100, 100, 3) * 255
        mock_roi = mock_roi.astype(np.uint8)
        response_dict = {'text_annotations': [], 'error': {'message': ''}}
        response = ParseDict(response_dict, vision.AnnotateImageResponse())

        # Expected empty response from Google Vision text_detection
        mock_vision_client.return_value.text_detection.return_value = response

        # Call method under test
        recognized_text = self.ocr.extract_license_plate_text(mock_roi)
        self.assertEqual(recognized_text, '')

    @patch('license_plate_insights.ocr.vision.ImageAnnotatorClient')
    def test_extract_license_plate_text_error(self, mock_vision_client):
        # Set up test data and mock responses
        mock_roi = np.random.rand(100, 100, 3) * 255
        mock_roi = mock_roi.astype(np.uint8)
        response_dict = {'error': {'message': 'Error during OCR'}}
        response = ParseDict(response_dict, vision.AnnotateImageResponse())

        # Expected error response from Google Vision text_detection
        mock_vision_client.return_value.text_detection.return_value = response

        # Call method under test and verify exception raised
        with self.assertRaises(Exception) as context:
            self.ocr.extract_license_plate_text(mock_roi)
        self.assertIn('Error during OCR', str(context.exception))

if __name__ == '__main__':
    unittest.main()
