# face_recognition.py
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input
import boto3
import os
import platform
import tempfile

# Initialize S3 client
s3 = boto3.client("s3")
BUCKET_NAME = "mfa-biometric-templates"
MODEL_S3_PATH = "facenet_tensorflow"

# Define local model paths
LOCAL_MODEL_PATH = "C:/Users/USER/MFA_Biometric_Auth/models/facenet_tensorflow"  # Your local model path
FALLBACK_MODEL_DIR = os.path.join(tempfile.gettempdir(), "facenet_tensorflow")  # Fallback for S3 download

def download_model_from_s3():
    """Download the FaceNet model from S3 if it doesn't exist locally."""
    if not os.path.exists(FALLBACK_MODEL_DIR):
        os.makedirs(FALLBACK_MODEL_DIR, exist_ok=True)
        print(f"Downloading model from S3 to {FALLBACK_MODEL_DIR}...")
        try:
            for obj in s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=MODEL_S3_PATH)["Contents"]:
                local_path = os.path.join(FALLBACK_MODEL_DIR, obj["Key"].replace(MODEL_S3_PATH + "/", ""))
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                s3.download_file(BUCKET_NAME, obj["Key"], local_path)
                print(f"Downloaded {obj['Key']} to {local_path}")
        except Exception as e:
            print(f"Error downloading model from S3: {e}")
            raise

def load_facenet_model():
    """Load the FaceNet model, prioritizing the local system path."""
    model_path = LOCAL_MODEL_PATH

    # Check if the local model exists
    if os.path.exists(os.path.join(LOCAL_MODEL_PATH, "saved_model.pb")):
        print(f"Loading model from local path: {LOCAL_MODEL_PATH}")
    else:
        print(f"Local model not found at {LOCAL_MODEL_PATH}. Falling back to S3 download...")
        model_path = FALLBACK_MODEL_DIR
        download_model_from_s3()

    # Load the model
    try:
        model = tf.saved_model.load(model_path)
        print(f"Model signatures: {list(model.signatures.keys())}")
        return model.signatures['serving_default']
    except Exception as e:
        print(f"Error loading model from {model_path}: {e}")
        raise

facenet_model = load_facenet_model()

def preprocess_image(img_path):
    if not isinstance(img_path, str):
        img = img_path
    else:
        img = image.load_img(img_path, target_size=(160, 160))
        img = image.img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img = preprocess_input(img)
    return img

def get_face_embedding(img_input):
    print(f"🛠 Debug: Received input of type {type(img_input)} with value: {img_input if isinstance(img_input, str) else 'Image Array'}")
    img = preprocess_image(img_input)
    result = facenet_model(tf.convert_to_tensor(img, dtype=tf.float32))
    print(f"Model output keys: {list(result.keys())}")
    embedding = result.get("Bottleneck_BatchNorm")
    if embedding is None:
        raise KeyError("Output key 'Bottleneck_BatchNorm' not found in model output.")
    embedding = embedding.numpy()
    return embedding.flatten()

import hashlib

def transform_features(features):
    transformed = hashlib.sha256(features.tobytes()).digest()
    return np.frombuffer(transformed, dtype=np.uint8)