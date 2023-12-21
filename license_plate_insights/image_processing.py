from typing import List, Tuple

import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw


class ImageProcessor:
    @staticmethod
    def load_image(img_path: str) -> np.ndarray:
        img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        return img[:, :, ::-1].copy()

    @staticmethod
    def draw_text(img: np.ndarray, text: str, xy: Tuple[int, int], color: Tuple[int, int, int] = (0, 255, 0)) -> np.ndarray:
        pil_img = Image.fromarray(img)
        draw = ImageDraw.Draw(pil_img)
        draw.text(xy, text, fill=color)
        return np.array(pil_img)

    def display_and_save(self, imgs: List[np.ndarray], save_path: str = "images/yolov8_car.jpg") -> None:
        for i, img in enumerate(imgs):
            plt.subplot(1, len(imgs), i + 1)
            plt.axis("off")
            plt.imshow(img)
        plt.savefig(save_path, bbox_inches='tight')
