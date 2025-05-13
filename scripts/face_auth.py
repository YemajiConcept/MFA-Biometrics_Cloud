import numpy as np
import boto3
from database import get_user_metadata
from face_recognition import get_face_embedding
from cryptography.fernet import Fernet
import base64
from config import KMS_KEY_ID, BUCKET_NAME

s3 = boto3.client("s3")
kms = boto3.client("kms", region_name="us-east-1")

def decrypt_data_key(encrypted_key):
    response = kms.decrypt(CiphertextBlob=encrypted_key)
    return response["Plaintext"]

def decrypt_template(ciphertext, plaintext_key):
    fernet_key = base64.urlsafe_b64encode(plaintext_key)
    fernet = Fernet(fernet_key)
    decrypted_data = fernet.decrypt(ciphertext)
    return np.frombuffer(decrypted_data, dtype=np.float32)

def verify_user(image_path, user_id):
    if not isinstance(image_path, str):
        return None, "❌ Error: Invalid image path."
    
    new_embedding = get_face_embedding(image_path)
    if new_embedding is None or new_embedding.shape[0] != 128:
        return None, f"❌ Error extracting face embedding: {new_embedding.shape if new_embedding is not None else 'None'}"

    try:
        key_obj = s3.get_object(Bucket=BUCKET_NAME, Key=f"{user_id}_face.key")
        face_obj = s3.get_object(Bucket=BUCKET_NAME, Key=f"{user_id}_face.enc")
        encrypted_key = key_obj["Body"].read()
        encrypted_face = face_obj["Body"].read()
    except s3.exceptions.NoSuchKey:
        return None, "❌ User not found."

    plaintext_key = decrypt_data_key(encrypted_key)
    stored_face = decrypt_template(encrypted_face, plaintext_key)
    print(f"Stored face shape: {stored_face.shape}, dtype: {stored_face.dtype}")
    print(f"New embedding shape: {new_embedding.shape}, dtype: {new_embedding.dtype}")

    if stored_face.shape != new_embedding.shape:
        return None, f"❌ Shape mismatch: stored_face {stored_face.shape} vs new_embedding {new_embedding.shape}"

    # Normalize embeddings
    stored_face = stored_face / np.linalg.norm(stored_face)
    new_embedding = new_embedding / np.linalg.norm(new_embedding)
    
    # Compute Euclidean distance and cosine similarity
    distance = np.linalg.norm(stored_face - new_embedding)
    cosine_sim = np.dot(stored_face, new_embedding)
    print(f"🔍 Face distance: {distance}, Cosine similarity: {cosine_sim}")

    # Stricter threshold
    threshold = 0.5  # Stricter than 0.4, aligns with local app
    cosine_threshold = 0.10  # Increased for robustness

    # Fetch username for the specific user_id
    username = get_user_metadata(user_id)  # Fixed: Pass user_id
    if not username:
        username = "Unknown User"

    if distance < threshold and cosine_sim > cosine_threshold:
        return user_id, f"✅ Face Authentication Successful! Welcome, {username}!"
    else:
        return None, f"❌ Face Authentication Failed! Distance: {distance}, Cosine similarity: {cosine_sim}"