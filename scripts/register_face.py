import numpy as np
import boto3
from face_recognition import get_face_embedding
from database import store_user_metadata
import botocore.exceptions
from cryptography.fernet import Fernet
import base64
from config import KMS_KEY_ID, BUCKET_NAME

s3 = boto3.client("s3")
kms = boto3.client("kms")

def generate_and_encrypt_data_key():
    try:
        response = kms.generate_data_key(
            KeyId=KMS_KEY_ID,
            KeySpec='AES_256'
        )
        return response['Plaintext'], response['CiphertextBlob']
    except botocore.exceptions.ClientError as e:
        print(f"❌ Error generating data key with KMS: {e}")
        raise

def encrypt_template(data, plaintext_key):
    fernet_key = base64.urlsafe_b64encode(plaintext_key)
    fernet = Fernet(fernet_key)
    data_bytes = data.tobytes()
    return fernet.encrypt(data_bytes)

def store_biometric_template(user_id, biometric_data):
    try:
        plaintext_key, encrypted_key = generate_and_encrypt_data_key()
        encrypted_data = encrypt_template(biometric_data, plaintext_key)
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=f"{user_id}_face.enc",
            Body=encrypted_data
        )
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=f"{user_id}_face.key",
            Body=encrypted_key
        )
        print(f"🛠 Stored encrypted face and key for user {user_id} in S3.")
    except botocore.exceptions.ClientError as e:
        print(f"❌ Error storing biometric template in S3: {e}")
        raise

def register_user(user_id, username, face_image_path):
    if not isinstance(face_image_path, str):
        print(f"❌ Error: Expected file path, got {type(face_image_path)}")
        return False
    
    face_embedding = get_face_embedding(face_image_path)
    if face_embedding is None:
        print("❌ Failed to register face! Embedding not extracted.")
        return False
    
    if face_embedding.shape[0] != 128:
        print(f"❌ Expected 128-dimensional embedding, got {face_embedding.shape}")
        return False
    
    face_embedding = face_embedding.astype(np.float32)
    print(f"Face embedding shape: {face_embedding.shape}, dtype: {face_embedding.dtype}")
    
    try:
        store_user_metadata(user_id, username)
        store_biometric_template(user_id, face_embedding)
        print(f"✅ {username} face registered!")
        return True
    except Exception as e:
        print(f"❌ Error during face registration: {e}")
        return False