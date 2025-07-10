import cv2
import numpy as np
from PIL import Image

def preprocess_image(image, size=(100, 100)):
    img = image.resize(size)
    img = np.array(img)
    if img.shape[-1] == 4:  # RGBA to RGB
        img = img[:, :, :3]
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    return img

def extract_features_for_leaf_classifier(img):
    img = cv2.resize(img, (100, 100))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)
    return edges.flatten()

def extract_features_for_disease_model(image):
    # Assumes image is already resized to (64, 64)
    img = cv2.resize(image, (64, 64))  # Match training
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsv], [0, 1, 2], None,
                        [8, 8, 8], [0, 180, 0, 256, 0, 256])
    hist = cv2.normalize(hist, hist).flatten()

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150).flatten()

    return np.concatenate((hist, edges))  


def prepare_for_nn(image):
    img = cv2.resize(image, (128, 128))   # ✅ Resize to match training
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype('float32') / 255.0   # ✅ Normalize to 0-1 range
    return img
