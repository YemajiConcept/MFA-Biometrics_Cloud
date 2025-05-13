import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input
import cv2
import hashlib
import os
import boto3
import botocore
from config import BUCKET_NAME

# Path to store the model temporarily on Elastic Beanstalk
MODEL_PATH = "/tmp/facenet_tensorflow"

# Initialize S3 client
s3 = boto3.client("s3")

def load_facenet_model():
    """Load the FaceNet model by downloading it from S3."""
    os.makedirs(MODEL_PATH, exist_ok=True)
    os.makedirs(f"{MODEL_PATH}/variables", exist_ok=True)
    try:
        print(f"🛠 Downloading saved_model.pb from S3...")
        s3.download_file(BUCKET_NAME, "facenet_tensorflow/saved_model.pb", f"{MODEL_PATH}/saved_model.pb")
        print(f"🛠 Downloading variables.data-00000-of-00001 from S3...")
        s3.download_file(BUCKET_NAME, "facenet_tensorflow/variables/variables.data-00000-of-00001", f"{MODEL_PATH}/variables/variables.data-00000-of-00001")
        print(f"🛠 Downloading variables.index from S3...")
        s3.download_file(BUCKET_NAME, "facenet_tensorflow/variables/variables.index", f"{MODEL_PATH}/variables/variables.index")
    except botocore.exceptions.ClientError as e:
        print(f"❌ Error downloading model files from S3: {e}")
        raise

    required_files = [
        f"{MODEL_PATH}/saved_model.pb",
        f"{MODEL_PATH}/variables/variables.data-00000-of-00001",
        f"{MODEL_PATH}/variables/variables.index"
    ]
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ Missing file: {file_path}")
            print(f"🛠 Listing contents of {MODEL_PATH}:")
            for root, dirs, files in os.walk(MODEL_PATH):
                print(f"  Directory: {root}")
                for file in files:
                    print(f"    File: {file}")
            raise FileNotFoundError(f"❌ Required model file not found: {file_path}")
        print(f"🛠 Verified: {file_path} exists")

    try:
        print(f"🛠 Loading model from {MODEL_PATH}...")
        model = tf.saved_model.load(MODEL_PATH)
        print(f"🛠 Model signatures: {list(model.signatures.keys())}")
        return model.signatures['serving_default']
    except Exception as e:
        raise Exception(f"❌ Failed to load FaceNet model from {MODEL_PATH}: {str(e)}")

facenet_model = load_facenet_model()

def detect_face(img):
    """Detect and crop the face using OpenCV's Haar Cascade."""
    # Convert to uint8 if not already
    if img.dtype != np.uint8:
        img = img.astype(np.uint8)
    
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    if face_cascade.empty():
        raise ValueError("❌ Haar Cascade classifier not found at: " + cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    if len(faces) == 0:
        print("❌ No face detected in the image.")
        return None
    
    x, y, w, h = faces[0]
    face_img = img[y:y+h, x:x+w]
    return cv2.resize(face_img, (160, 160))

def preprocess_image(img_input):
    """Preprocess an image (path or array) to match FaceNet's input requirements: (1, 160, 160, 3)."""
    print(f"🛠 Debug: Preprocessing input of type {type(img_input)}")
    if isinstance(img_input, str):
        img = image.load_img(img_input)
        img = image.img_to_array(img)  # float32
    else:
        img = img_input
        if len(img.shape) == 2:
            img = np.stack((img, img, img), axis=-1)
        elif len(img.shape) == 3 and img.shape[-1] == 1:
            img = np.repeat(img, 3, axis=-1)
        elif len(img.shape) == 3 and img.shape[-1] != 3:
            raise ValueError(f"❌ Expected 3 channels, got {img.shape[-1]} channels")

    # Face detection
    face_img = detect_face(img)
    if face_img is None:
        return None

    img = face_img
    if img.shape[:2] != (160, 160):
        img = cv2.resize(img, (160, 160))

    if len(img.shape) == 3:
        img = np.expand_dims(img, axis=0)
    elif len(img.shape) != 4:
        raise ValueError(f"❌ Expected 3D or 4D input, got shape {img.shape}")

    img = preprocess_input(img)
    print(f"🛠 Preprocessed image shape: {img.shape}")
    return img

def get_face_embedding(img_input):
    """Generate a face embedding using FaceNet."""
    print(f"🛠 Debug: Received input of type {type(img_input)} with value: {img_input if isinstance(img_input, str) else 'Image Array'}")
    try:
        img = preprocess_image(img_input)
        if img is None:
            return None
        result = facenet_model(tf.convert_to_tensor(img, dtype=tf.float32))
        print(f"🛠 Model output keys: {list(result.keys())}")
        embedding = result.get("Bottleneck_BatchNorm")
        if embedding is None:
            raise KeyError("❌ Output key 'Bottleneck_BatchNorm' not found")
        embedding = embedding.numpy().flatten()
        print(f"🛠 Embedding shape: {embedding.shape}, dtype: {embedding.dtype}")
        return embedding.astype(np.float32)
    except Exception as e:
        print(f"❌ Error extracting face embedding: {str(e)}")
        return None

# Commented-out for future AWS use
# def transform_features(features):
#     """Applies a transformation to the biometric template before storage."""
#     transformed = hashlib.sha256(features.tobytes()).digest()
#     return np.frombuffer(transformed, dtype=np.uint8).astype(np.float32)