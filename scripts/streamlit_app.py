import streamlit as st
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from PIL import Image
import tempfile
from register import register_fingerprint
from authenticate import authenticate_fingerprint

# Load trained fingerprint model
FINGERPRINT_MODEL_PATH = r"C:\Users\USER\MFA_Biometric_Auth\models\new_fingerprint_model.h5"
fingerprint_model = load_model(FINGERPRINT_MODEL_PATH)

# Streamlit UI
st.title("🔒 Biometric Fingerprint Authentication System")

# Select mode
mode = st.radio("Choose an option:", ["Register", "Authenticate"])

# User Input
username = st.text_input("Enter Full Name")

# Upload Fingerprint
uploaded_file = st.file_uploader("Upload Fingerprint", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    
    # Resize the image before displaying
    image = image.resize((150, 150))  # Set thumbnail size

    st.image(image, caption="Uploaded Fingerprint", width=150)  # Reduce size in UI

    # Save temp file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    image.save(temp_file.name)

    if st.button("Proceed"):
        if mode == "Register":
            register_fingerprint(username, temp_file.name)
            st.success(f"✅ {username} registered successfully!")
        elif mode == "Authenticate":
            result = authenticate_fingerprint(temp_file.name, username)
            st.success(result)
