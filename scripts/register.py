import numpy as np
import boto3
from extract_fingerprint_features import extract_fingerprint_features, transform_features
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
        plaintext_data_key = response['Plaintext']
        encrypted_data_key = response['CiphertextBlob']
        return plaintext_data_key, encrypted_data_key
    except botocore.exceptions.ClientError as e:
        print(f"❌ Error generating data key with KMS: {e}")
        raise

def encrypt_template(data, plaintext_key):
    fernet_key = base64.urlsafe_b64encode(plaintext_key)
    fernet = Fernet(fernet_key)
    data_bytes = data.tobytes()
    encrypted_data = fernet.encrypt(data_bytes)
    return encrypted_data

def store_biometric_template(user_id, biometric_data):
    try:
        plaintext_key, encrypted_key = generate_and_encrypt_data_key()
        encrypted_data = encrypt_template(biometric_data, plaintext_key)
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=f"{user_id}_fingerprint.enc",
            Body=encrypted_data
        )
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=f"{user_id}_fingerprint.key",
            Body=encrypted_key
        )
        print(f"🛠 Stored encrypted fingerprint and key for user {user_id} in S3.")
    except botocore.exceptions.ClientError as e:
        print(f"❌ Error storing biometric template in S3: {e}")
        raise

def register_fingerprint_user(user_id, username, image_path):
    fingerprint_features = extract_fingerprint_features(image_path)
    if fingerprint_features is None:
        print("❌ Error: Fingerprint features are None.")
        return False

    norm = np.linalg.norm(fingerprint_features)
    if norm < 1e-3 or np.any(np.isnan(fingerprint_features)) or np.any(np.isinf(fingerprint_features)):
        print(f"❌ Error: Invalid fingerprint features (norm={norm}, has NaN={np.any(np.isnan(fingerprint_features))}, has Inf={np.any(np.isinf(fingerprint_features))}).")
        return False

    print(f"🛠 Registering fingerprint features: shape={fingerprint_features.shape}, norm={norm}, sample={fingerprint_features[:10]}")

    try:
        store_user_metadata(user_id, username)
        store_biometric_template(user_id, fingerprint_features)
        print(f"✅ {username} fingerprint registered!")
        return True
    except Exception as e:
        print(f"❌ Error during registration: {e}")
        return False