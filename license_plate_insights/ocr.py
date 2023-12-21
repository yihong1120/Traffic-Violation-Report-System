import cv2
from google.cloud import vision


# OCR class containing OCR logic


class OCR:
    @staticmethod
    def extract_license_plate_text(roi: np.ndarray) -> str:
        _, encoded_image = cv2.imencode('.jpg', roi)
        roi_bytes = encoded_image.tobytes()

        client = vision.ImageAnnotatorClient()
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
