import streamlit as st
import os
from PIL import Image
from authenticate import authenticate_fingerprint

def authentication_page():
    st.markdown("""
        <style>
        .stApp {background-color: #000000;}
        .stButton>button {background-color: #2196F3; color: white; border-radius: 5px; padding: 10px 24px;}
        .stButton>button:hover {background-color: #1976D2;}
        .stFileUploader>label {font-size: 16px; font-weight: bold; color: #ffffff;}
        </style>
    """, unsafe_allow_html=True)

    st.title("🔑 User Authentication - Fingerprint")
    st.markdown("<p style='font-size: 16px; color: #ffffff;'>Please upload your fingerprint image to begin authentication.</p>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload Fingerprint Image", type=["png", "jpg", "jpeg"], key="auth_fingerprint")
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Preview Fingerprint", use_column_width=True, width=200)

        fingerprint_path = "temp_fingerprint_auth.jpg"
        image.save(fingerprint_path, format="JPEG")

        if st.button("🔍 Authenticate Fingerprint", help="Click to verify your fingerprint"):
            user_id, result = authenticate_fingerprint(fingerprint_path)
            os.remove(fingerprint_path)

            if user_id:
                st.session_state["fingerprint_user_id"] = user_id
                st.success(result)
                st.markdown("Please proceed to face authentication.")
            else:
                st.error(result)

if __name__ == "__main__":
    authentication_page()