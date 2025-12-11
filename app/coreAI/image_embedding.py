import numpy as np
import cv2
import tflite_runtime.interpreter as tflite

from common_utils.file_utils import download_image


class ImageEmbedder:
    def __init__(self, model_path):
        """Khởi tạo ImageEmbedder với mô hình TFLite"""
        self.interpreter = tflite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()

        # Lấy thông tin tensor input và output
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        # Kiểm tra kích thước đầu vào
        self.input_shape = self.input_details[0]['shape']
        if len(self.input_shape) != 4:
            raise ValueError(f"Expected 4D input shape, got {self.input_shape}")

        self.input_height, self.input_width = self.input_shape[1], self.input_shape[2]

    def preprocess_image(self, image):
        """
        Tiền xử lý ảnh: có thể nhập từ đường dẫn hoặc numpy array
        """
        if isinstance(image, str):
            if image.startswith("https://"):
                image = download_image(image)
            img = cv2.imread(image)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        elif isinstance(image, np.ndarray):  # Nếu là numpy array, sử dụng trực tiếp
            img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            raise TypeError("Input should be a file path or a NumPy array.")

        img = cv2.resize(img, (self.input_width, self.input_height))
        img = np.expand_dims(img, axis=0).astype(np.float32)
        img = img / 255.0  # Chuẩn hóa ảnh về [0,1]
        return img, image

    def get_embedding(self, image):
        """
        Trích xuất embedding từ ảnh đầu vào (đường dẫn hoặc numpy array)
        """
        img, image_path = self.preprocess_image(image)

        # Đưa ảnh vào mô hình
        self.interpreter.set_tensor(self.input_details[0]['index'], img)
        self.interpreter.invoke()

        # Lấy output embedding
        embedding = self.interpreter.get_tensor(self.output_details[0]['index'])

        # Chuẩn hóa embedding (nếu cần)
        embedding = embedding / np.linalg.norm(embedding)  # Normalize về vector đơn vị
        return embedding[0], image_path