import sqlite3
import numpy as np
import pickle
import os
from cryptography.fernet import Fernet

DB_PATH = r"C:\Users\USER\MFA_Biometric_Auth\Fingerprint_app\mfa_auth.db"
KEY_PATH = r"C:\Users\USER\MFA_Biometric_Auth\Fingerprint_app\scripts\database_key\encryption_key.key"

# 🔑 Generate encryption key if it doesn't exist
if not os.path.exists(KEY_PATH):
    key = Fernet.generate_key()
    with open(KEY_PATH, "wb") as key_file:
        key_file.write(key)

# 🔐 Load encryption key
with open(KEY_PATH, "rb") as key_file:
    ENCRYPTION_KEY = key_file.read()

cipher = Fernet(ENCRYPTION_KEY)

# 🔒 Encrypt data
def encrypt_data(data):
    return cipher.encrypt(pickle.dumps(data))

# 🔓 Decrypt data
def decrypt_data(data):
    return pickle.loads(cipher.decrypt(data))

# ✅ Initialize the database
def init_db():
    """Creates a secure database for fingerprint and face authentication."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # Create table for fingerprint authentication
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                fingerprint_vector BLOB NOT NULL,
                face_embedding BLOB NOT NULL
            )
        """)

        conn.commit()
    print("✅ Database Initialized Securely!")

# 🟢 REGISTER USER (Fingerprint + Face)
def register_user(name, fingerprint_vector, face_embedding):
    """Stores a user's encrypted fingerprint and face embedding in the database."""
    
    # ✅ Ensure NumPy arrays before storage
    fingerprint_vector = np.array(fingerprint_vector, dtype=np.float32)
    face_embedding = np.array(face_embedding, dtype=np.float32)

    # ✅ Ensure feature vector size is exactly 5000
    fixed_size = 5000
    if fingerprint_vector.shape[0] != fixed_size:
        print(f"⚠ Warning: Feature vector size mismatch! Expected {fixed_size}, got {fingerprint_vector.shape[0]}")
        fingerprint_vector = np.pad(fingerprint_vector, (0, max(0, fixed_size - fingerprint_vector.shape[0])), mode='constant')[:fixed_size]

    # 🔐 Encrypt before storing
    encrypted_fingerprint = encrypt_data(fingerprint_vector)
    encrypted_face = encrypt_data(face_embedding)

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (name, fingerprint_vector, face_embedding) VALUES (?, ?, ?)", 
                           (name, encrypted_fingerprint, encrypted_face))
            print(f"✅ User {name} Registered Securely!")
        except sqlite3.IntegrityError:
            cursor.execute("UPDATE users SET fingerprint_vector = ?, face_embedding = ? WHERE name = ?", 
                           (encrypted_fingerprint, encrypted_face, name))
            print(f"✅ User {name} Updated Successfully!")
        conn.commit()

# 🔵 RETRIEVE ALL USERS
def get_all_users():
    """Retrieve all stored user data with decryption."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, fingerprint_vector, face_embedding FROM users")
        results = cursor.fetchall()

    users = {}
    for name, fingerprint_blob, face_blob in results:
        try:
            decrypted_fingerprint = decrypt_data(fingerprint_blob)
            decrypted_face = decrypt_data(face_blob)
            users[name] = {"fingerprint": decrypted_fingerprint, "face": decrypted_face}
        except Exception as e:
            print(f"❌ Error decrypting data for {name}: {str(e)}")

    return users

# 🛠 CLEAR DATABASE (SECURE RESET)
def clear_database():
    """Deletes all stored biometric data securely."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users")
        conn.commit()
        cursor.execute("VACUUM")  # ✅ Properly reset auto-increment IDs
    print("🗑️ Secure Database Cleared!")

# ✅ Run database initialization when script is executed
if __name__ == "__main__":
    init_db()
    print("✅ Secure Database Ready!")
