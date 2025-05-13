import numpy as np
import boto3
from database import init_db, get_user_metadata
from extract_fingerprint_features import extract_fingerprint_features
from cryptography.fernet import Fernet
import base64
import hashlib
from config import KMS_KEY_ID, BUCKET_NAME

s3 = boto3.client("s3")
kms = boto3.client("kms", region_name="us-east-1")

def decrypt_data_key(encrypted_key):
    try:
        response = kms.decrypt(CiphertextBlob=encrypted_key)
        return response["Plaintext"]
    except Exception as e:
        print(f"❌ Error decrypting data key: {e}")
        return None

def decrypt_template(ciphertext, plaintext_key):
    try:
        fernet_key = base64.urlsafe_b64encode(plaintext_key)
        fernet = Fernet(fernet_key)
        decrypted_data = fernet.decrypt(ciphertext)
        return np.frombuffer(decrypted_data, dtype=np.float32)
    except Exception as e:
        print(f"❌ Error decrypting template: {e}")
        return None

def delete_invalid_template(user_id):
    try:
        s3.delete_object(Bucket=BUCKET_NAME, Key=f"{user_id}_fingerprint.enc")
        s3.delete_object(Bucket=BUCKET_NAME, Key=f"{user_id}_fingerprint.key")
        print(f"🛠 Deleted invalid fingerprint template for user {user_id}. Please re-register.")
    except Exception as e:
        print(f"❌ Error deleting template for user {user_id}: {e}")

def authenticate_fingerprint(image_path, user_id, nonce):
    conn = init_db()
    cursor = conn.cursor()
    # Check for nonce replay (this prevents actual replay attacks)
    cursor.execute("SELECT 1 FROM nonces WHERE nonce = %s AND used_at > NOW() - INTERVAL '5 minutes'", (nonce,))
    if cursor.fetchone():
        conn.close()
        return None, "❌ Replay attack detected."

    if not isinstance(image_path, str) or not image_path:
        print("❌ ERROR: Invalid fingerprint image path.")
        return None, "❌ Invalid fingerprint image."

    print("🛠 Extracting fingerprint features...")
    extracted_features = extract_fingerprint_features(image_path)
    if extracted_features is None or not isinstance(extracted_features, np.ndarray):
        print("❌ ERROR: Failed to extract valid fingerprint features.")
        return None, "❌ Error extracting fingerprint features."

    print(f"✅ Extracted Features Shape: {extracted_features.shape}")
    print(f"Extracted Features Sample: {extracted_features[:10]}")
    print(f"Extracted Features Norm: {np.linalg.norm(extracted_features)}")

    # Compute hash of transformed features to detect static image usage
    feature_hash = hashlib.sha256(extracted_features.tobytes()).hexdigest()

    cursor.execute("SELECT user_id FROM users")
    user_ids = [row[0] for row in cursor.fetchall()]
    print(f"🛠 Found {len(user_ids)} registered users: {user_ids}")
    conn.close()

    if not user_ids:
        print("❌ ERROR: No registered fingerprints found in the database. Please register a user.")
        return None, "❌ Authentication Failed! No registered users found in the database."

    min_distance = float("inf")
    matched_user = None
    matched_username = None
    static_image_warning = None

    for uid in user_ids:
        username = get_user_metadata(uid) or uid
        # Check for static image usage (potential replay attack warning)
        # --- START OF REPLAY ATTACK DETECTION (REMOVE OR ADJUST LATER) ---
        conn = init_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 1 FROM nonces 
            WHERE user_id = %s AND feature_hash = %s AND used_at > NOW() - INTERVAL '5 minutes'
        """, (uid, feature_hash))
        if cursor.fetchone():
            static_image_warning = "⚠ Warning: Same fingerprint features detected. This may indicate a replay attack using a static image."
            print(static_image_warning)
        conn.close()
        # --- END OF REPLAY ATTACK DETECTION ---

        try:
            key_obj = s3.get_object(Bucket=BUCKET_NAME, Key=f"{uid}_fingerprint.key")
            fingerprint_obj = s3.get_object(Bucket=BUCKET_NAME, Key=f"{uid}_fingerprint.enc")
            encrypted_key = key_obj["Body"].read()
            encrypted_fingerprint = fingerprint_obj["Body"].read()
        except s3.exceptions.NoSuchKey:
            print(f"⚠ Warning: No fingerprint data found in S3 for user {username}")
            continue

        plaintext_key = decrypt_data_key(encrypted_key)
        if plaintext_key is None:
            print(f"⚠ Warning: Failed to decrypt key for user {username}")
            continue

        stored_vector = decrypt_template(encrypted_fingerprint, plaintext_key)
        if stored_vector is None:
            print(f"⚠ Warning: Failed to decrypt template for user {username}")
            delete_invalid_template(uid)
            continue

        print(f"Stored fingerprint shape for {username}: {stored_vector.shape}")
        print(f"Stored fingerprint sample: {stored_vector[:10]}")
        stored_norm = np.linalg.norm(stored_vector)
        print(f"Stored fingerprint norm: {stored_norm}")
        print(f"Stored fingerprint min/max: {np.min(stored_vector)}/{np.max(stored_vector)}")

        if stored_vector.shape[0] == 0 or stored_norm < 1e-3 or np.any(np.isnan(stored_vector)) or np.any(np.isinf(stored_vector)):
            print(f"⚠ Warning: Invalid stored fingerprint for {username} (shape={stored_vector.shape}, norm={stored_norm}, has NaN={np.any(np.isnan(stored_vector))}, has Inf={np.any(np.isinf(stored_vector))}).")
            delete_invalid_template(uid)
            continue

        if np.max(np.abs(stored_vector)) < 1e-10:
            print(f"⚠ Warning: Stored fingerprint for {username} has extremely small values (max abs value={np.max(np.abs(stored_vector))}). Likely corrupted during registration.")
            delete_invalid_template(uid)
            continue

        if stored_vector.shape[0] != extracted_features.shape[0]:
            print(f"🛠 Adjusting stored vector shape from {stored_vector.shape[0]} to match extracted features {extracted_features.shape[0]}")
            if stored_vector.shape[0] < extracted_features.shape[0]:
                stored_vector = np.pad(stored_vector, (0, extracted_features.shape[0] - stored_vector.shape[0]), mode='constant')
            else:
                stored_vector = stored_vector[:extracted_features.shape[0]]

        stored_vector = stored_vector / stored_norm
        extracted_norm = np.linalg.norm(extracted_features)
        if extracted_norm > 0:
            extracted_features_normalized = extracted_features / extracted_norm
        else:
            print("❌ ERROR: Extracted features have zero norm.")
            return None, "❌ Error processing input fingerprint."

        distance = np.linalg.norm(stored_vector - extracted_features_normalized)
        print(f"🔍 Distance from {username}: {distance}")

        if distance < min_distance:
            min_distance = distance
            matched_user = uid
            matched_username = username

    threshold = 0.3
    if min_distance < threshold and matched_user is not None:
        conn = init_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO nonces (nonce, user_id, used_at, feature_hash) VALUES (%s, %s, NOW(), %s)", (nonce, matched_user, feature_hash))
        conn.commit()
        conn.close()
        result = f"✅ Fingerprint Authentication Successful! User: {matched_username}"
        if static_image_warning:
            result += f"\n{static_image_warning}"
        return matched_user, result
    else:
        return None, f"❌ Authentication Failed! No matching fingerprint found (min distance: {min_distance})"