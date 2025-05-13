import streamlit as st
from admin_enroll import admin_enrollment_page
from user_auth import user_authentication_page
from dashboard import user_dashboard
from about_us_page import about_us

st.set_page_config(
    page_title="MFA Biometric Authentication",
    page_icon="🔒",
    layout="wide"
)

st.markdown("""
    <style>
    .stApp {background-color: #000000;}
    .big-title {font-size: 30px; text-align: center; font-weight: bold; color: #ffffff;}
    .success-message {font-size: 24px; font-weight: bold; color: darkgreen;}
    .sidebar .css-1lcbmhc {color: #ffffff !important;}
    .stRadio > label {color: #ffffff; font-size: 16px;}
    </style>
""", unsafe_allow_html=True)

if "authenticated_user" not in st.session_state:
    st.session_state["authenticated_user"] = None

st.sidebar.title("🔍 Navigation")
page = st.sidebar.radio("Select an Option", [
    "🏠 Home",
    "👤 Admin Enrollment",
    "🔑 User Authentication",
    "☁️ User Dashboard",
    "ℹ️ About Us"
])

if page == "🏠 Home":
    st.markdown("<h1 class='big-title'>🔒 Multi-Factor Authentication Using Biometrics for Cloud Security</h1>", unsafe_allow_html=True)
    st.markdown("""
        ## Welcome to the MFA Biometric Authentication System!  
        **This system enhances security using fingerprint & facial recognition before accessing cloud services.**  
        
        ### 🔑 Why Enroll?
        - 🆕 **New users must enroll first** before gaining access.  
        - 🔐 **Admins handle all enrollments** to ensure security.  
        - ✅ **Already enrolled?** Proceed to authentication.  

        ### 📌 Navigation:
        - 👤 **Admin Enrollment**: Register new users.
        - 🔑 **User Authentication**: Verify identity using fingerprint & face.
        - ☁️ **User Dashboard**: Access cloud security features **after authentication**.
        - ℹ️ **About Us**: Learn about the algorithms, datasets, and methodology used.
    """)
elif page == "👤 Admin Enrollment":
    admin_enrollment_page()
elif page == "🔑 User Authentication":
    user_authentication_page()
elif page == "☁️ User Dashboard":
    if st.session_state["authenticated_user"]:
        user_dashboard()
    else:
        st.warning("⚠️ Access Denied: Please authenticate first.")
elif page == "ℹ️ About Us":
    about_us()

if __name__ == "__main__":
    import os
    if 'AWS_EXECUTION_ENV' in os.environ:  # Running on EB
        port = int(os.environ.get("PORT", 8501))
        st.run(host='0.0.0.0', port=port)
    else:  # Local development
        st.run()