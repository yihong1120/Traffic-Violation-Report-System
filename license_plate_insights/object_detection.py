import cv2
from ultralytics import YOLO


class ObjectDetector:
    def __init__(self, model):
        """
        Initializes the ObjectDetector with a given model.

        Args:
            model: The YOLO model to use for object detection.
        """
        # Allows injection of a YOLO model for better testability
        self.model = model

    def recognize_license_plate(self, img_path: str) -> np.ndarray:
        """
        Recognizes the license plate in a given image and returns the recognized text and the image.

        Args:
            img_path: A string representing the path to the image file.

        Returns:
            A tuple containing the recognized text and the numpy array representing the image.
        """
        img = self.read_image(img_path)
        results = self.model.predict(img, save=False)
        boxes = results[0].boxes.xyxy
        recognized_text = None

        for box in boxes:
            recognized_text, img = self.process_detected_box(box, img)
    def read_image(self, img_path: str) -> np.ndarray:
        """
        Reads an image from the given path and converts it to an RGB numpy array.

        Args:
            img_path: A string path to the image file.

        Returns:
            np.ndarray: The image represented as a numpy array.
        """
        img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        return img[:, :, ::-1].copy()

    def get_vision_client(self):
        """
        Provides an instance of Google Vision ImageAnnotatorClient.

        Returns:
            vision.ImageAnnotatorClient: An instance of the client.
        """
        return vision.ImageAnnotatorClient()

    def process_detected_box(self, box, img):
        """
        Processes a detected box in an image, extracts the text from the box using Google Cloud Vision API, and draws a rectangle around the box in the image.

        Args:
            box: The coordinates of the detected box in the image.
            img: The numpy array representing the image.

        Returns:
            A tuple containing the recognized text and the modified image with the box drawn.
        """
        x1, y1, x2, y2 = map(int, box[:4])
        roi = img[y1:y2, x1:x2]
            _, encoded_image = cv2.imencode('.jpg', roi)
            roi_bytes = encoded_image.tobytes()
            client = self.get_vision_client()
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
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        return recognized_text, img
