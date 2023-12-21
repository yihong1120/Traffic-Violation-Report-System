import cv2
from ultralytics import YOLO


class ObjectDetector:
    def __init__(self, weights_path: str):
        self.model = YOLO(weights_path)


class ObjectDetector:
    def __init__(self, weights_path: str):
        self.model = YOLO(weights_path)

    def recognize_license_plate(self, img_path: str) -> np.ndarray:
        img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        img = img[:, :, ::-1].copy()
        results = self.model.predict(img, save=False)
        boxes = results[0].boxes.xyxy
        recognized_text = None

    def recognize_license_plate(self, img_path: str):
        img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        img = img[:, :, ::-1].copy()  # Convert BGR to RGB
        results = self.model.predict(img, save=False)
        boxes = results[0].boxes.xyxy
        recognized_text = None

        for box in boxes:
            x1, y1, x2, y2 = map(int, box[:4])
            roi = img[y1:y2, x1:x2]
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
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        return recognized_text, img
