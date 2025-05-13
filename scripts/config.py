import streamlit as st

# Load secrets
KMS_KEY_ID = st.secrets["kms_key_id"]
BUCKET_NAME = "mfa-biometric-templates"
DB_HOST = "mfa-db.cyfq20c64vrw.us-east-1.rds.amazonaws.com"
DB_NAME = "mfa_db"
DB_USER = "admin_1"
DB_PASSWORD = "MFAsecure2025!"
DB_PORT = 5432