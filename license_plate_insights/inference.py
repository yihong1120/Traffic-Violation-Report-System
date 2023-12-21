    """
    The CarLicensePlateDetector class is responsible for detecting and recognizing car
    license plates in an image or a stream of images from a video.

    It utilizes a pre-trained YOLO (You Only Look Once) model for efficient and accurate
    object detection and an OCR (Optical Character Recognition) system to read characters
    on the plates. The class provides methods for processing still images, videos, and
    extracting license plate text using the OCR.

    Attributes:
        image_processor (ImageProcessor): Instance used for image pre-processing.
        object_detector (ObjectDetector): YOLO-based detector for finding license plates.
        ocr (OCR): OCR system instance for recognizing characters on the plates.

    Methods:
        recognize_license_plate: Recognizes and annotates the license plate in an image.
        load_image: Loads an image from disk.
        extract_license_plate_text: Extracts text from a region containing a license plate.
        display_and_save: Displays a list of images and saves them to disk.
        process_video: Processes a video to detect and recognize license plates in every frame.
        get_media_info: Returns media information like DateTime, GPSLatitude, and GPSLongitude.
        get_image_info: Extracts information from an image file.
        extract_gps_data: Extracts GPS information from an image file.
        parse_gps_info: Parses raw GPS metadata info to human-readable format.
        convert_to_degrees: Converts raw GPS degree data into decimal degrees.
        get_video_info: Extracts metadata information from a video file.
    """from license_plate_insights.image_processing import ImageProcessor
from license_plate_insights.object_detection import ObjectDetector
from license_plate_insights.ocr import OCR

class CarLicensePlateDetector:
    """
    This class is used for detecting and recognizing car license plates.

    It leverages a trained YOLO (You Only Look Once) model for object detection,
    and an OCR (Optical Character Recognition) system to recognize and decode
    the characters on the license plates. The processing of images and videos to
    identify and annotate license plates is encapsulated within this class.

    Attributes:
        weights_path (str): The path to the weights file for the YOLO model.

    Methods:
        recognize_license_plate(img: np.ndarray) -> Tuple[str, np.ndarray]:
            Recognizes the license plate in a given image and returns the
            recognized text alongside an annotated image with a bounding box around
            the license plate.
    """

    def __init__(self, image_processor, object_detector, ocr):
        """
        Initializes the CarLicensePlateDetector with injected dependencies.

        Args:
            image_processor (ImageProcessor): An instance of the image processing class.
            object_detector (ObjectDetector): An instance of the object detection class.
            ocr (OCR): An instance of the OCR class.
        """
        self.image_processor = image_processor
        self.object_detector = object_detector
        self.ocr = ocr

    def detect_license_plate(self, image: np.ndarray) -> Tuple[str, np.ndarray]:
        """
        Detects the license plate in an image and returns the recognized text and the region of interest.

        Args:
            image (np.ndarray): The image to analyze.

        Returns:
            Tuple[str, np.ndarray]: A tuple containing the recognized text and the region of interest.
        """
        recognized_text, roi = self.object_detector.recognize_license_plate(image)
        return recognized_text, roi

    def recognize_license_plate(self, img_path: str) -> Tuple[str, np.ndarray]:
        """
        Recognizes the license plate in an image provided by the image path and returns the recognized text along with the annotated image.

        Args:
            img_path (str): The path to the input image file.

        Returns:
            Tuple[str, np.ndarray]: A tuple containing the recognized text and the annotated image with a bounding box around the license plate.
        """
        def annotate_image(self, recognized_text: str, roi: Tuple[int, int, int, int], image: np.ndarray) -> np.ndarray:
            """
            Annotates the image with the recognized text at the specified region of interest.

            Args:
                recognized_text (str): The text recognized from the license plate.
                roi (Tuple[int, int, int, int]): The region of interest where the license plate is detected.
                image (np.ndarray): The image to annotate.

            Returns:
                np.ndarray: The image with the annotation.
            """
            x1, y1, x2, y2 = roi
            return self.image_processor.draw_text(image, recognized_text, (x1, y1 - 20))

        image = self.load_image(img_path)
        recognized_text, roi = self.detect_license_plate(image)
        if recognized_text:
            annotated_image = self.annotate_image(recognized_text, roi, image)
            print(f"License: {recognized_text}")
            return recognized_text, annotated_image
        else:
            return "", img
        info = {
            'DateTime': image_info.get('DateTime', None),
            'GPSLatitude': image_info.get('GPSLatitude', None),
            'GPSLongitude': image_info.get('GPSLongitude', None),
            'License': recognized_text
        }

        return info, img

        Returns:
            np.ndarray: The image with the text drawn on it.
        """
        pil_img = Image.fromarray(img)
        draw = ImageDraw.Draw(pil_img)
        draw.text(xy, text, fill=color)
        return np.array(pil_img)

    @staticmethod
    def load_image(img_path: str) -> np.ndarray:
        """
        Loads an image from the specified path.

        Args:
            img_path (str): The path to the image file.

        Returns:
            np.ndarray: The loaded image.
        """
        img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        return img[:, :, ::-1].copy()  # Convert BGR to RGB

    @staticmethod
    def extract_license_plate_text(roi: np.ndarray) -> str:
        """
        Extracts the text from a region of interest (ROI) in an image using Google Cloud Vision API.

        Args:
            roi (np.ndarray): The region of interest in the image where the license plate is located.

        Returns:
            str: The recognized text from the license plate.
        """
        # Convert the ROI to bytes for the Vision API
        _, encoded_image = cv2.imencode('.jpg', roi)
        roi_bytes = encoded_image.tobytes()

        # Initialize the Google Cloud Vision client
        client = vision.ImageAnnotatorClient()

        # Prepare the image for the Vision API
        image = vision.Image(content=roi_bytes)

        # Perform text detection
        response = client.text_detection(image=image)

        # In case of errors
        if response.error.message:
            raise Exception(
                "{}\nFor more info on error messages, check: "
                "https://cloud.google.com/apis/design/errors".format(response.error.message)
            )

        # Extract and return the recognized text
        texts = response.text_annotations
        if texts:
            recognized_text = texts[0].description.strip()  # The first annotation contains the full detected text
            return recognized_text
        else:
            return ""

    def display_and_save(self, imgs: List[np.ndarray], save_path: str = "images/yolov8_car.jpg") -> None:
        """
        Displays and saves a list of images without altering their size.

        Args:
            imgs (List[np.ndarray]): A list of images to be displayed and saved.
            save_path (str): The file path where the image will be saved.
        """
        for i, img in enumerate(imgs):
            plt.subplot(1, len(imgs), i + 1)
            plt.axis("off")
            plt.imshow(img)
        plt.savefig(save_path, bbox_inches='tight')

    def process_video(self, video_path: str, output_path: str) -> None:
        """
        Processes a video file to detect and recognize license plates in each frame.

        Args:
            video_path (str): The path to the video file.
            output_path (str): The path where the output video will be saved.
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise IOError("Error opening video file")

        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, 30.0,
                             (int(cap.get(3)), int(cap.get(4))))

        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                # Process the frame
                _, annotated_frame = self.recognize_license_plate(frame)
                # Write the frame
                out.write(cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR))
            else:
                break

        # Release everything when done
        cap.release()
        out.release()
        cv2.destroyAllWindows()

    def get_media_info(self, file_path: str) -> Union[str, Dict[str, Any]]:
        """
        Get media information from a file.

        Args:
            file_path (str): The path to the media file.

        Returns:
            Union[str, Dict[str, Any]]: A dictionary containing media information or an error message.

        Raises:
            Exception: If an error occurs while reading the file.
        """
        if file_extension.lower() in ('.png', '.jpg', '.jpeg'):
            return self.get_image_info(content)
        elif file_extension.lower() in ('.mp4', '.mov', '.avi'):
            return self.get_video_info(content)
        else:
            return "Unsupported file format"

    def get_image_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get information from an image file.

        Args:
            file_path (str): The path to the image file.

        Returns:
            Dict[str, Any]: A dictionary containing image information.

        Raises:
            Exception: If an error occurs while reading the image data.
        """
        try:
            image = Image.open(file_path)
            raw_exif_data = image._getexif()

            if raw_exif_data is None:
                return {"Error": "No EXIF data found in the image."}

            exif_data = {
                TAGS[key]: value
                for key, value in raw_exif_data.items()
                if key in TAGS and value
            }
            datetime = exif_data.get('DateTime', 'Unknown')
            gps_info = self.extract_gps_data(file_path)
            return {'DateTime': datetime, **gps_info}
        except Exception as e:
            return f"Error reading image data: {e}"

    def extract_gps_data(self, file_path: str) -> Dict[str, Any]:
        """
        Extract GPS data from an image file.

        Args:
            file_path (str): The path to the image file.

        Returns:
            Dict[str, Any]: A dictionary containing GPS information.

        Raises:
            Exception: If an error occurs while extracting GPS data.
        """
        with open(file_path, 'rb') as f:
            tags = exifread.process_file(f)
        gps_info = {}
        for tag in tags.keys():
            if tag.startswith("GPS"):
                gps_info[tag] = tags[tag]
        return self.parse_gps_info(gps_info)

    def parse_gps_info(self, gps_info: Dict[str, Any]) -> Dict[str, float]:
        """
        Parse GPS information from a dictionary.

        Args:
            gps_info (Dict[str, Any]): A dictionary containing GPS information.

        Returns:
            Dict[str, float]: A dictionary containing parsed GPS information.

        Raises:
            Exception: If an error occurs while parsing GPS data.
        """
        gps_data = {}
        if 'GPS GPSLatitude' in gps_info and 'GPS GPSLatitudeRef' in gps_info:
            gps_data['GPSLatitude'] = self.convert_to_degrees(gps_info['GPS GPSLatitude'].values)
            if gps_info['GPS GPSLatitudeRef'].printable != 'N':
                gps_data['GPSLatitude'] = -gps_data['GPSLatitude']
        if 'GPS GPSLongitude' in gps_info and 'GPS GPSLongitudeRef' in gps_info:
            gps_data['GPSLongitude'] = self.convert_to_degrees(gps_info['GPS GPSLongitude'].values)
            if gps_info['GPS GPSLongitudeRef'].printable != 'E':
                gps_data['GPSLongitude'] = -gps_data['GPSLongitude']
        return gps_data

    def convert_to_degrees(self, value: Tuple[int, int, int]) -> float:
        """
        Convert GPS coordinate values to degrees.

        Args:
            value (Tuple[int, int, int]): A tuple containing degrees, minutes, and seconds.

        Returns:
            float: The coordinate value in degrees.
        """
        d, m, s = value
        d = float(d.numerator) / float(d.denominator)
        m = float(m.numerator) / float(m.denominator)
        s = float(s.numerator) / float(s.denominator)
        return d + (m / 60.0) + (s / 3600.0)

    def get_video_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get information from a video file.

        Args:
            file_path (str): The path to the video file.

        Returns:
            Dict[str, Any]: A dictionary containing video information or an error message.

        Raises:
            Exception: If an error occurs while reading the video data.
        """
        try:
            parser = createParser(file_path)
            if not parser:
                return "Unable to parse video file"
            with parser:
                metadata = extractMetadata(parser)
            return metadata.exportDictionary() if metadata else "No metadata found in video"
        except Exception as e:
            return f"Error reading video data: {e}"


if __name__ == '__main__':
    weights_path: str = 'models/best.pt'
    detector = CarLicensePlateDetector(weights_path)

    file_path = 'medias/taiwan_taxi.jpg'
    info, _ = detector.recognize_license_plate(file_path)
    print(info)

    if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        # Use the already loaded image
        _, recognized_img = detector.recognize_license_plate(file_path)
        image_output_path = './medias/yolov8_Scooter.jpg'
        cv2.imwrite(image_output_path, cv2.cvtColor(recognized_img, cv2.COLOR_RGB2BGR))
        print(f"Saved the image with the license plate to {image_output_path}")
    elif file_path.lower().endswith(('.mp4', '.mov', '.avi')):
        video_output_path = '/path/to/save/processed.mp4'
        detector.process_video(file_path, video_output_path)
        print(f"Saved the processed video to {video_output_path}")
    else:
        print("Unsupported media format")