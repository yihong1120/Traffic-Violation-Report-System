import cv2
from google.cloud import vision


class OCR:
    def __init__(self, vision_client=None):
        """
        Initializes the OCR with a given vision client.

        Args:
            vision_client: A vision client from Google Cloud Vision API.
        """
        self.vision_client = vision_client or vision.ImageAnnotatorClient()

    def extract_license_plate_text(self, roi: np.ndarray) -> str:
        """
        Extracts the text from a region of interest (ROI) in an image using Google Cloud Vision API and returns the recognized text.

        Args:
            roi: A numpy array representing the region of interest in the image.

        Returns:
            The recognized text as a string.
        """
        _, encoded_image = cv2.imencode('.jpg', roi)
        roi_bytes = encoded_image.tobytes()

        client = self.vision_client
        image = vision.Image(content=roi_bytes)

        response = client.text_detection(image=image)

        if response.error.message:
            raise Exception(
                "{}\nFor more info on error messages, check: "
                "https://cloud.google.com/apis/design/errors".format(response.error.message)
            )

        texts = response.text_annotations
        if texts:
            recognized_text = texts[0].description.strip()
            return recognized_text
        else:
            return ""
