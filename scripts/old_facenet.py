import tensorflow as tf
import boto3
import os
import tempfile

s3 = boto3.client("s3")
BUCKET_NAME = "mfa-biometric-templates"
MODEL_S3_PATH = "facenet_tensorflow"
LOCAL_MODEL_DIR = tempfile.gettempdir() + "/facenet_tensorflow"

def download_model_from_s3():
    if not os.path.exists(LOCAL_MODEL_DIR):
        os.makedirs(LOCAL_MODEL_DIR)
        for obj in s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=MODEL_S3_PATH)["Contents"]:
            local_path = os.path.join(LOCAL_MODEL_DIR, obj["Key"].replace(MODEL_S3_PATH + "/", ""))
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            s3.download_file(BUCKET_NAME, obj["Key"], local_path)

def load_facenet_model():
    download_model_from_s3()
    model = tf.saved_model.load(LOCAL_MODEL_DIR)
    return model.signatures['serving_default']

facenet_model = load_facenet_model()