import cv2
import numpy as np

def preprocess_fingerprint(image_path):
    """Loads, enhances, converts to RGB, resizes, and normalizes the fingerprint image."""
    
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    if img is None:
        print("❌ Error: Could not load fingerprint image.")
        return None
    
    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to enhance ridges
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    img = clahe.apply(img)

    img = cv2.resize(img, (96, 103))  # Resize to match model input
    
    # Convert grayscale to RGB (needed for model)
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    
    img = img / 255.0  # Normalize pixel values to [0,1]
    img = np.expand_dims(img, axis=0)  # Add batch dimension
    
    return img
