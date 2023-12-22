import unittest
from unittest.mock import patch, Mock
import numpy as np

import numpy as np
from license_plate_insights.inference import CarLicensePlateDetector, ImageProcessor, ObjectDetector, OCR
from google.cloud import vision
from google.protobuf.json_format import ParseDict
import cv2


class TestCarLicensePlateDetector(unittest.TestCase):

    @patch('license_plate_insights.ocr.OCR')
    @patch('license_plate_insights.object_detection.ObjectDetector')
    @patch('license_plate_insights.image_processing.ImageProcessor')
    def setUp(self, mock_ocr, mock_object_detector, mock_image_processor):
        self.image_processor = mock_image_processor.return_value
        self.object_detector = mock_object_detector.return_value
        self.ocr = mock_ocr.return_value
        self.detector = CarLicensePlateDetector(self.image_processor, self.object_detector, self.ocr)


    @patch('license_plate_insights.inference.CarLicensePlateDetector.annotate_image')
    @patch('license_plate_insights.inference.CarLicensePlateDetector.detect_license_plate')
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
                result = self.detector.recognize_license_plate('mock_image_path')
                self.assertEqual(result, scenario['expected_result'])

    @patch('license_plate_insights.inference.CarLicensePlateDetector.draw_text')
    def test_draw_text_on_image(self, mock_draw_text):
        mock_draw_text.return_value = 'mock_image_with_text'
        output_image = self.detector.draw_text('mock_image', 'mock_text', (0, 0))
        self.assertEqual(output_image, 'mock_image_with_text')

    # Test case for extract_license_plate_text method
    @patch('google.cloud.vision.ImageAnnotatorClient')
    def test_extract_license_plate_text(self):
        mock_roi = np.random.rand(100, 100, 3) * 255
        mock_roi = mock_roi.astype(np.uint8)
        expected_text = 'TEST1234'
        text_annotation_dict = {'description': expected_text}
        text_annotation = ParseDict(text_annotation_dict, vision.TextAnnotation())
        response_dict = {'text_annotations': [text_annotation], 'error': {'message': ''}}
        response = ParseDict(response_dict, vision.AnnotateImageResponse())

        with patch('cv2.imencode') as mock_imencode, \
            patch('google.cloud.vision.ImageAnnotatorClient') as mock_client:
            mock_imencode.return_value = (None, np.frombuffer(b'mock\x00binary\x00data', dtype=np.uint8))
            mock_client = mock_client.return_value
            mock_client.text_detection.return_value = response
            extracted_text = self.detector.extract_license_plate_text(mock_roi)
            self.assertEqual(extracted_text, expected_text)

    # Test case for load_image method
    @patch('cv2.imdecode')
    @patch('np.fromfile', return_value=np.frombuffer(b'mock binary data', dtype=np.uint8))
    def test_load_image(self, mock_fromfile, mock_imdecode):
        mock_image_path = 'mock_image.jpg'
        mock_returned_image = np.random.rand(100, 100, 3) * 255
        mock_returned_image = mock_returned_image.astype(np.uint8)
        mock_imdecode.return_value = mock_returned_image
        loaded_image = self.detector.load_image(mock_image_path)
        np.testing.assert_array_equal(loaded_image, mock_returned_image[:, :, ::-1])

    # Test case for process_video method
    @patch('cv2.VideoCapture')
    @patch('cv2.VideoWriter')
    @patch('license_plate_insights.inference.CarLicensePlateDetector.process_video')
    def test_process_video(self, mock_process_video, mock_video_writer, mock_video_capture):
        mock_process_video.return_value = None
        mock_video_path = 'mock_video_path.mp4'
        mock_output_path = 'mock_output_path.mp4'
        self.detector.process_video(mock_video_path, mock_output_path)
        mock_process_video.assert_called_once_with(mock_video_path, mock_output_path)

    def test_detect_license_plate(self):
        with patch('license_plate_insights.object_detection.ObjectDetector.recognize_license_plate') as mock_recognize_license_plate:
            # Setup mocks
            mock_image = np.zeros((640, 480, 3), dtype=np.uint8)
            expected_output = ('ABC123', np.array([50, 50, 200, 200]))
            mock_recognize_license_plate.return_value = expected_output

            # Call the function
            recognized_text, roi = self.detector.detect_license_plate(mock_image)

            # Assertions
            mock_recognize_license_plate.assert_called_once_with(mock_image)
            self.assertEqual(recognized_text, expected_output[0])
            np.testing.assert_array_equal(roi, expected_output[1])

    def test_annotate_image(self):
        with patch('license_plate_insights.inference.ImageProcessor.draw_text') as mock_draw_text, \
             patch('license_plate_insights.inference.CarLicensePlateDetector.load_image', return_value='mock_image'):
            # Setup mocks
            recognized_text = 'test_plate'
            roi = (50, 50, 200, 200)
            mock_draw_text.return_value = 'mock_annotated_image'

            # Call the function
            annotated_image = self.detector.annotate_image(recognized_text, roi, 'mock_image')

            # Assertions
            mock_draw_text.assert_called_once_with('mock_image', recognized_text, (roi[0], roi[1] - 20))
            self.assertEqual(annotated_image, 'mock_annotated_image')

if __name__ == '__main__':
    unittest.main()
    # Test case for display_and_save method
    @patch('matplotlib.pyplot.subplot')
    @patch('matplotlib.pyplot.axis')
    @patch('matplotlib.pyplot.imshow')
    @patch('matplotlib.pyplot.savefig')
    def test_display_and_save(self, mock_savefig, mock_imshow, mock_axis, mock_subplot):
        """
        Test the display_and_save method of CarLicensePlateDetector class to ensure images
        are correctly displayed and saved as specified.
        """
        mock_imgs = [np.random.rand(100, 100, 3) * 255 for _ in range(3)]
        mock_imgs = [img.astype(np.uint8) for img in mock_imgs]
        mock_save_path = 'mock_save_path.jpg'
        self.detector.display_and_save(mock_imgs, mock_save_path)
        mock_savefig.assert_called_once_with(mock_save_path, bbox_inches='tight')

    # Test case for get_media_info method
    @patch('license_plate_insights.inference.CarLicensePlateDetector.get_image_info')
    @patch('license_plate_insights.inference.CarLicensePlateDetector.get_video_info')
    def test_get_media_info(self, mock_get_video_info, mock_get_image_info):
        """
        Test the get_media_info method of the CarLicensePlateDetector class to check if it
        correctly returns the media information based on the file extension.
        """
        mock_file_path = 'mock_file_path'
        test_scenarios = [
            {
                'file_extension': '.jpg',
                'get_info_output': 'mock_image_info',
                'expected_result': 'mock_image_info'
            },
            {
                'file_extension': '.mp4',
                'get_info_output': 'mock_video_info',
                'expected_result': 'mock_video_info'
            },
            {
                'file_extension': '.txt',
                'expected_result': 'Unsupported file format'
            }
        ]

        # Test different scenarios
        for scenario in test_scenarios:
            with self.subTest(scenario=scenario):
                mock_file_path = 'mock_file_path' + scenario['file_extension']
                if 'get_info_output' in scenario:
                    if scenario['file_extension'] in ('.png', '.jpg', '.jpeg'):
                        mock_get_image_info.return_value = scenario['get_info_output']
                    else:
                        mock_get_video_info.return_value = scenario['get_info_output']
                result = self.detector.get_media_info(mock_file_path)
                self.assertEqual(result, scenario['expected_result'])

    # Test case for get_image_info method
    @patch('PIL.Image.open')
    @patch('license_plate_insights.inference.CarLicensePlateDetector.extract_gps_data')
    def test_get_image_info(self, mock_extract_gps_data, mock_open):
        """
        Test the get_image_info method of the CarLicensePlateDetector class to ensure it
        correctly returns the image information including metadata and GPS data.
        """
        mock_file_path = 'mock_file_path.jpg'
        mock_datetime = '2022:01:01 00:00:00'
        mock_gps_info = {'GPSLatitude': 25.0330, 'GPSLongitude': 121.5654}
        mock_extract_gps_data.return_value = mock_gps_info
        mock_image = Mock()
        mock_image._getexif.return_value = {36867: mock_datetime}  # 36867 is the tag for DateTime
        mock_open.return_value = mock_image
        image_info = self.detector.get_image_info(mock_file_path)
        expected_info = {'DateTime': mock_datetime, **mock_gps_info}
        self.assertEqual(image_info, expected_info)

    # Test case for extract_gps_data method
    @patch('exifread.process_file')
    def test_extract_gps_data(self, mock_process_file):
        """
        Test the extract_gps_data method of the CarLicensePlateDetector class to ensure it
        correctly extracts the GPS data from an image.
        """
        mock_file_path = 'mock_file_path.jpg'
        mock_tags = {
            'GPS GPSLatitude': '25 deg 1\' 58.80" N',
            'GPS GPSLatitudeRef': 'N',
            'GPS GPSLongitude': '121 deg 33\' 56.40" E',
            'GPS GPSLongitudeRef': 'E'
        }
        mock_process_file.return_value = mock_tags
        gps_info = self.detector.extract_gps_data(mock_file_path)
        expected_info = {'GPSLatitude': 25.0330, 'GPSLongitude': 121.5654}
        self.assertEqual(gps_info, expected_info)

    # Test case for parse_gps_info method
    def test_parse_gps_info(self):
        mock_gps_info = {
            'GPS GPSLatitude': '25 deg 1\' 58.80" N',
            'GPS GPSLatitudeRef': 'N',
            'GPS GPSLongitude': '121 deg 33\' 56.40" E',
            'GPS GPSLongitudeRef': 'E'
        }
        parsed_info = self.detector.parse_gps_info(mock_gps_info)
        expected_info = {'GPSLatitude': 25.0330, 'GPSLongitude': 121.5654}
        self.assertEqual(parsed_info, expected_info)

    # Test case for convert_to_degrees method
    def test_convert_to_degrees(self):
        mock_value = (25, 1, 58.8)
        degrees = self.detector.convert_to_degrees(mock_value)
        expected_degrees = 25.0330
        self.assertAlmostEqual(degrees, expected_degrees, places=4)

    # Test case for get_video_info method
    @patch('hachoir.parser.createParser')
    @patch('hachoir.metadata.extractMetadata')
    def test_get_video_info(self, mock_extract_metadata, mock_create_parser):
        mock_file_path = 'mock_file_path.mp4'
        mock_metadata = Mock()
        mock_metadata.exportDictionary.return_value = 'mock_video_info'
        mock_extract_metadata.return_value = mock_metadata
        video_info = self.detector.get_video_info(mock_file_path)
        self.assertEqual(video_info, 'mock_video_info')
