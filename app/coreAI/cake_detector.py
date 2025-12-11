import os
import cv2
from ultralytics import YOLO

from common_utils.file_utils import download_image


class Yolo11CakeDetector:
    """
    A utility class for loading a YOLO11 model and cropping detected objects of specified classes from images.
    """

    def __init__(self,
                 model_weights: str,
                 device: str = "cpu",
                 target_classes: list = None,
                 conf_threshold: float = 0.25):
        """
        Initializes the cropper with the given configuration.

        Args:
            model_weights (str): Path to YOLO11 weights file (e.g., 'yolo11n.pt').
            device (str): Device to use for inference ('cpu' or 'cuda').
            target_classes (list): List of class names to crop (e.g., ['cake', 'pizza', 'donut']).
            conf_threshold (float): Confidence threshold for detections.
        """
        self.model_weights = model_weights
        self.device = device
        self.target_classes = target_classes or ['cake', 'pizza', 'donut', "vase"]
        self.conf_threshold = conf_threshold

        # Load YOLO model
        self.model = YOLO(self.model_weights)
        # Ensure output directory exists
        # Class name mapping from model
        self.class_names = self.model.names

    def crop_from_image(self, img_path: str) -> list:
        """
        Process a single image: detect target classes and save crops.

        Args:
            img_path (str): Path to the image file.
        """
        if img_path.startswith("https://"):
            img_path = download_image(img_path)
        img = cv2.imread(img_path)
        if img is None:
            print(f"Warning: Unable to read image at {img_path}")
            return []
        img_list = []
        # Detect objects
        results = self.model(img_path, conf=self.conf_threshold, device=self.device)
        for res in results:
            boxes = res.boxes
            for i, box in enumerate(boxes):
                cls_id = int(box.cls[0])
                cls_name = self.class_names[cls_id]
                if cls_name in self.target_classes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    crop = img[y1:y2, x1:x2]
                    img_list.append(crop)
        if not img_list:
            img_list.append(img)
        return img_list
