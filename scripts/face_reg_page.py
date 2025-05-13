import streamlit as st
from register_face import register_face

def face_registration_page():
    st.title("📝 Face Registration")
    username = st.text_input("Enter Full Name")
    uploaded_file = st.file_uploader("Upload Face Image", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Face Image", use_column_width=True)
        if st.button("Register Face"):
            register_face(username, uploaded_file)
            st.success(f"✅ {username} registered successfully!")
