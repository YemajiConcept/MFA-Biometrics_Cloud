import streamlit as st
import os
from face_auth import verify_user

def face_authentication_page():
    st.markdown("""
        <style>
        .stApp {background-color: #000000;}
        .stButton>button {background-color: #2196F3; color: white; border-radius: 5px; padding: 10px 24px;}
        .stButton>button:hover {background-color: #1976D2;}
        .stFileUploader>label {font-size: 16px; font-weight: bold; color: #ffffff;}
        </style>
    """, unsafe_allow_html=True)

    st.title("🔑 User Authentication - Face")
    st.markdown("<p style='font-size: 16px; color: #ffffff;'>Please upload your face image to complete authentication.</p>", unsafe_allow_html=True)

    if "fingerprint_user_id" not in st.session_state:
        st.warning("⚠️ Please complete fingerprint authentication first.")
        return

    user_id = st.session_state["fingerprint_user_id"]
    uploaded_file = st.file_uploader("Upload Face Image", type=["png", "jpg", "jpeg"], key="auth_face")
    if uploaded_file:
        st.image(uploaded_file, caption="Preview Face", use_column_width=True, width=200)

        face_path = "temp_face_auth.jpg"
        with open(face_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        if st.button("🔍 Authenticate Face", help="Click to verify your face"):
            _, result = verify_user(face_path, user_id)
            os.remove(face_path)

            if "✅" in result:
                st.session_state["authenticated_user"] = result.split("Welcome, ")[1].split("!")[0]
                st.success(result)
            else:
                st.error(result)

if __name__ == "__main__":
    face_authentication_page()