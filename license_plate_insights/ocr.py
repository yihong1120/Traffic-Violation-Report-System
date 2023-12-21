import cv2
from google.cloud import vision


class OCR:
    def __init__(self, vision_client=None):
        self.vision_client = vision_client or vision.ImageAnnotatorClient()

    def extract_license_plate_text(self, roi: np.ndarray) -> str:
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
