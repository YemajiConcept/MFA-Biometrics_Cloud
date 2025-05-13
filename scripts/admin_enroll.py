import streamlit as st
import os
import uuid
import time
from PIL import Image
from register import register_fingerprint_user
from register_face import register_user
from face_recognition import get_face_embedding

def admin_enrollment_page():
    """Admin-controlled user enrollment page for biometric authentication."""
    
    st.markdown("""
        <style>
        .main {background-color: #f0f2f6; padding: 20px;}
        .stButton>button {background-color: #4CAF50; color: white; border-radius: 5px; padding: 10px 24px;}
        .stButton>button:hover {background-color: #45a049;}
        .stTextInput>div>input {border-radius: 5px; padding: 8px; background-color: #ffffff; color: #333;}
        .stFileUploader>label {font-size: 16px; font-weight: bold; color: #ffffff;}
        </style>
    """, unsafe_allow_html=True)

    st.title("👤 Admin User Enrollment")
    st.markdown("""
        <p style='font-size: 16px; color: #ffffff;'>Enroll new users securely using biometric authentication.<br>
        Ensure fingerprint and face images are clear and properly captured.</p>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("Enter User's Full Name", placeholder="e.g., John Doe", key="username_input")
    with col2:
        st.empty()

    st.subheader("📌 Biometric Data Upload")
    col3, col4 = st.columns(2)
    with col3:
        fingerprint_file = st.file_uploader("Upload Fingerprint Image", type=["png", "jpg", "jpeg"], key="fingerprint_upload")
        if fingerprint_file:
            st.image(fingerprint_file, caption="Preview Fingerprint", use_container_width=True, width=200)
    with col4:
        face_file = st.file_uploader("Upload Face Image", type=["png", "jpg", "jpeg"], key="face_upload")
        if face_file:
            st.image(face_file, caption="Preview Face", use_container_width=True, width=200)

    user_id = str(uuid.uuid4())

    if st.button("✅ Enroll User", help="Click to enroll the user with provided biometrics"):
        if username and fingerprint_file and face_file:
            with st.spinner("📥 Processing Enrollment..."):
                time.sleep(1)

                # Save temporary files
                fingerprint_path = f"temp_fingerprint_{user_id}.jpg"
                face_path = f"temp_face_{user_id}.jpg"
                with open(fingerprint_path, "wb") as f:
                    f.write(fingerprint_file.getbuffer())
                with open(face_path, "wb") as f:
                    f.write(face_file.getbuffer())

                try:
                    # Register fingerprint
                    success_fingerprint = register_fingerprint_user(user_id, username, fingerprint_path)
                    if not success_fingerprint:
                        st.error("❌ Fingerprint registration failed.")
                        return

                    # Register face
                    success_face = register_user(user_id, username, face_path)
                    if not success_face:
                        st.error("❌ Face registration failed.")
                        return

                    st.success(f"✅ {username} enrolled successfully! (Internal User ID: {user_id})")
                    time.sleep(2)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Enrollment error: {str(e)}")
                finally:
                    # Clean up
                    if os.path.exists(fingerprint_path):
                        os.remove(fingerprint_path)
                    if os.path.exists(face_path):
                        os.remove(face_path)
        else:
            st.warning("⚠️ Please provide all required fields: username, fingerprint, and face image.")

if __name__ == "__main__":
    admin_enrollment_page()