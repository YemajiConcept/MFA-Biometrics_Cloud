import streamlit as st
import tempfile
import os
import cv2
import numpy as np
from PIL import Image
from register import register_fingerprint
from extract_fingerprint_features import extract_fingerprint_features

def registration_page():
    st.title("📝 User Registration - Biometric Authentication")

    username = st.text_input("Enter Full Name")

    uploaded_file = st.file_uploader("Upload Fingerprint", type=["png", "jpg", "jpeg", "bmp"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Fingerprint", use_container_width=True)

        # Convert RGBA to RGB if needed
        if image.mode == "RGBA":
            image = image.convert("RGB")

        # Save image properly
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        file_path = temp_file.name  # Store actual file path
        image.save(file_path, format="JPEG")

        # Debugging: Ensure the file is saved correctly
        if not os.path.exists(file_path):
            st.error(f"❌ Error: The file was not saved properly at {file_path}.")
            return  # Stop further execution if file is not saved
        else:
            st.success(f"✅ Fingerprint image saved successfully at {file_path}.")

        # Extract fingerprint features
        print(f"🛠 Debug: Sending file_path to extract_fingerprint_features: {file_path} ({type(file_path)})")
        features = extract_fingerprint_features(file_path)

        if features is None:
            st.error("❌ Error: Could not extract fingerprint features. Try again.")
            return  # Stop further execution if feature extraction fails

        # Register user when button is clicked
        if st.button("Register User"):
            print(f"🛠 Debug: Sending file_path to register_fingerprint: {file_path} ({type(file_path)})")
            register_fingerprint(username, file_path)  # ✅ FIXED: Pass file path instead of features
            st.success(f"✅ {username} registered successfully!")
