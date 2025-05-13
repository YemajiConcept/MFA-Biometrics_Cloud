import cv2
import numpy as np
import os
from PIL import Image
import hashlib

def transform_features(features):
    """Applies a transformation to the biometric template before storage."""
    transformed = hashlib.sha256(features.tobytes()).digest()
    return np.frombuffer(transformed, dtype=np.uint8).astype(np.float32)

def extract_fingerprint_features(image_path):
    """Extracts fingerprint features while ensuring correct file path input."""
    print(f"🛠 Debug: Received image_path of type {type(image_path)} with value: {image_path}")

    if not isinstance(image_path, str):
        print(f"❌ ERROR: Expected a file path, but got {type(image_path)}")
        return None

    if not os.path.exists(image_path):
        print(f"❌ ERROR: File does not exist at {image_path}")
        return None

    try:
        img = Image.open(image_path).convert("L")
        img = np.array(img, dtype=np.uint8)
        print(f"Image min: {np.min(img)}, max: {np.max(img)}")
    except Exception as e:
        print(f"❌ ERROR: Could not read image file - {str(e)}")
        return None

    if np.var(img) < 100:
        print("❌ ERROR: Image has low variance, likely poor quality.")
        return None

    # Resize to match local app
    img = cv2.resize(img, (96, 96))
    print(f"Resized image min: {np.min(img)}, max: {np.max(img)}")

    img_float = np.float32(img)

    # Harris Corner Detection (same as local app)
    harris_corners = cv2.cornerHarris(img_float, blockSize=2, ksize=3, k=0.04)
    harris_corners = cv2.normalize(harris_corners, None, 0, 255, cv2.NORM_MINMAX)
    harris_corners = np.uint8(harris_corners)
    print(f"Harris corners min: {np.min(harris_corners)}, max: {np.max(harris_corners)}")
    print(f"Harris corners sample: {harris_corners.flatten()[:10]}")

    # Ridge Feature Extraction (try alternative if needed)
    ridge_features = cv2.adaptiveThreshold(
        img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )
    non_zero_count = np.count_nonzero(ridge_features)
    print(f"Ridge features min: {np.min(ridge_features)}, max: {np.max(ridge_features)}")
    print(f"Ridge features sample: {ridge_features.flatten()[:10]}")
    print(f"Ridge features non-zero count: {non_zero_count}")

    # Fallback to Otsu's thresholding if sparse
    if non_zero_count < 0.3 * ridge_features.size:  # Less than 30% non-zero
        print("🛠 Warning: Sparse ridge features. Trying Otsu's thresholding.")
        _, ridge_features = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        ridge_features = cv2.morphologyEx(ridge_features, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        non_zero_count = np.count_nonzero(ridge_features)
        print(f"Otsu ridge features min: {np.min(ridge_features)}, max: {np.max(ridge_features)}")
        print(f"Otsu ridge features sample: {ridge_features.flatten()[:10]}")
        print(f"Otsu ridge features non-zero count: {non_zero_count}")

    # Flatten and pad features
    fixed_size = 2500
    harris_flattened = np.pad(harris_corners.flatten(), (0, max(0, fixed_size - len(harris_corners.flatten()))), mode='constant')[:fixed_size]
    ridge_flattened = np.pad(ridge_features.flatten(), (0, max(0, fixed_size - len(ridge_features.flatten()))), mode='constant')[:fixed_size]

    # Combine features
    fingerprint_features = np.hstack((harris_flattened, ridge_flattened)).astype(np.float32)
    print(f"✅ Extracted Feature Vector Shape: {fingerprint_features.shape}")
    print(f"Feature vector sample: {fingerprint_features[:10]}")
    norm = np.linalg.norm(fingerprint_features)
    print(f"Feature vector norm: {norm}")

    # Validate feature vector
    unique_values = np.unique(fingerprint_features)
    non_zero_ratio = np.count_nonzero(fingerprint_features) / len(fingerprint_features)
    if len(unique_values) <= 2 or non_zero_ratio < 0.1 or norm < 1e-3:
        print("❌ ERROR: Feature vector is uniform, has too few non-zero elements, or has near-zero norm.")
        return None

    # Transform features (match local app)
    fingerprint_features = transform_features(fingerprint_features)
    print(f"✅ Transformed Feature Vector Shape: {fingerprint_features.shape}")
    print(f"Transformed feature vector sample: {fingerprint_features[:10]}")
    norm = np.linalg.norm(fingerprint_features)
    print(f"Transformed feature vector norm: {norm}")

    if norm > 0:
        fingerprint_features = fingerprint_features / norm
    else:
        print("❌ ERROR: Feature vector norm is zero.")
        return None

    return fingerprint_features