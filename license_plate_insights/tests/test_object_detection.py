import unittest
from unittest.mock import patch

import numpy as np
from google.cloud import vision
from license_plate_insights.object_detection import ObjectDetector


class TestObjectDetector(unittest.TestCase):
    @patch('ultralytics.YOLO', autospec=True)
    def setUp(self, mock_model):
        """
        Sets up the test case by creating an instance of ObjectDetector.
        """
        self.model = mock_model.return_value
        self.detector = ObjectDetector(self.model)

    @patch('license_plate_insights.object_detection.ObjectDetector.recognize_license_plate')
    def test_recognize_license_plate(self, mock_recognize_license_plate):
        """
        Tests the recognize_license_plate method of the ObjectDetector class.
        """
        mock_recognize_license_plate.return_value = 'ABC123', None
        recognized_text, _ = self.detector.recognize_license_plate('mock_image_path')
        self.assertEqual(recognized_text, 'ABC123')

        mock_recognize_license_plate.return_value = '', None
        recognized_text, _ = self.detector.recognize_license_plate('mock_image_path')
        self.assertEqual(recognized_text, '')

        mock_recognize_license_plate.return_value = 'XYZ789', None
        recognized_text, _ = self.detector.recognize_license_plate('mock_image_path')
        self.assertEqual(recognized_text, 'XYZ789')

    def test_read_image(self):
        mock_img_path = 'path/to/mock_image.jpg'
        with patch('cv2.imdecode') as mock_imdecode, \
                patch('numpy.fromfile') as mock_fromfile:
            mock_image = np.random.rand(100, 100, 3) * 255
            mock_image = mock_image.astype(np.uint8)
            mock_fromfile.return_value = np.frombuffer(b'mock_image_binary_data', dtype=np.uint8)
            mock_imdecode.return_value = mock_image

            result_image = self.detector.read_image(mock_img_path)

            np.testing.assert_array_equal(result_image, mock_image)
            mock_fromfile.assert_called_once_with(mock_img_path, dtype=np.uint8)
            mock_imdecode.assert_called_once()

    def test_process_detected_box(self):
        mock_box = [50, 50, 150, 150]
        mock_img = np.random.rand(200, 200, 3) * 255
        mock_img = mock_img.astype(np.uint8)
        expected_text = 'ABC123'
        with patch('cv2.imencode') as mock_imencode, \
                patch('google.cloud.vision.ImageAnnotatorClient') as mock_client:
            mock_client_instance = mock_client.return_value
            mock_text_annotation = vision.TextAnnotation()
            mock_text_annotation.description = expected_text
            mock_response = vision.AnnotateImageResponse(text_annotations=[mock_text_annotation])
            mock_client_instance.text_detection.return_value = mock_response
            mock_imencode.return_value = (True, np.frombuffer(b'roi_image_binary_data', dtype=np.uint8))

            detected_text, processed_img = self.detector.process_detected_box(mock_box, mock_img)

            self.assertEqual(detected_text, expected_text)
            self.assertIsInstance(processed_img, np.ndarray)
            mock_client_instance.text_detection.assert_called_once()
            mock_imencode.assert_called_once_with('.jpg', mock_img[50:150, 50:150])

if __name__ == '__main__':
    unittest.main()
