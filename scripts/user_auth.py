import streamlit as st
import os
import uuid
from PIL import Image
from authenticate import authenticate_fingerprint
from face_auth import verify_user
from database import get_user_metadata

def save_uploaded_file(uploaded_file, prefix="temp"):
    """Save uploaded file and return its path."""
    file_id = str(uuid.uuid4())
    file_path = f"{prefix}_{file_id}.jpg"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def user_authentication_page():
    st.markdown("""
        <style>
        .stApp {background-color: #000000;}
        .stButton>button {background-color: #2196F3; color: white; border-radius: 5px; padding: 10px 24px;}
        .stButton>button:hover {background-color: #1976D2;}
        .stFileUploader>label {font-size: 16px; font-weight: bold; color: #ffffff;}
        </style>
    """, unsafe_allow_html=True)

    st.title("🔑 User Authentication")
    st.markdown("<p style='font-size: 16px; color: #ffffff;'>Please upload your fingerprint and face images to authenticate.</p>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        fingerprint_file = st.file_uploader("Upload Fingerprint Image", type=["png", "jpg", "jpeg"], key="auth_fingerprint")
        if fingerprint_file:
            fingerprint_image = Image.open(fingerprint_file).resize((150, 150))
            st.image(fingerprint_image, caption="Preview Fingerprint", width=150)
    with col2:
        face_file = st.file_uploader("Upload Face Image", type=["png", "jpg", "jpeg"], key="auth_face")
        if face_file:
            face_image = Image.open(face_file).resize((150, 150))
            st.image(face_image, caption="Preview Face", width=150)

    if st.button("🔍 Authenticate", help="Click to verify your biometrics"):
        if not fingerprint_file or not face_file:
            st.error("Please upload both fingerprint and face images.")
        else:
            with st.spinner("🔍 Authenticating..."):
                # Save temporary files with unique names
                fingerprint_path = save_uploaded_file(fingerprint_file, "temp_fingerprint_auth")
                face_path = save_uploaded_file(face_file, "temp_face_auth")

                try:
                    # Fingerprint authentication
                    user_id, fingerprint_result = authenticate_fingerprint(fingerprint_path, user_id=None)
                    if not user_id:
                        st.error(fingerprint_result)
                        return
                    st.success(fingerprint_result)

                    # Fetch username after fingerprint authentication
                    username = get_user_metadata(user_id)
                    if not username:
                        st.error(f"User metadata not found for user_id: {user_id}")
                        return
                    st.write(f"Fingerprint authenticated for user: {username}")

                    # Face authentication
                    verified_user_id, face_result = verify_user(face_path, user_id)
                    if verified_user_id and "Successful" in face_result:
                        # Username already fetched, no need to re-fetch
                        st.session_state["authenticated_user"] = username
                        st.success(face_result)
                        st.balloons()
                    else:
                        st.error(face_result)
                except Exception as e:
                    st.error(f"Authentication error: {str(e)}")
                finally:
                    # Clean up
                    if os.path.exists(fingerprint_path):
                        os.remove(fingerprint_path)
                    if os.path.exists(face_path):
                        os.remove(face_path)

if __name__ == "__main__":
    user_authentication_page()