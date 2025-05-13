import streamlit as st
import time

def logout():
    st.session_state.pop("authenticated_user", None)
    st.session_state.pop("fingerprint_user_id", None)
    st.success("✅ Logged out successfully!")
    time.sleep(2)
    st.rerun()

def view_secure_files():
    st.markdown("""
        <style>
        .stApp {background-color: #000000;}
        </style>
    """, unsafe_allow_html=True)
    st.title("📂 View Secure Files")
    st.markdown("<p style='font-size: 16px; color: #ffffff;'>You are now viewing your secure files. Below is a sample list of files:</p>", unsafe_allow_html=True)
    st.markdown("""
        - file1_encrypted.pdf
        - file2_secure.docx
        - file3_protected.jpg
    """)
    st.button("🔙 Back to Dashboard", on_click=lambda: st.session_state.update({"current_page": "dashboard"}))

def access_encrypted_data():
    st.markdown("""
        <style>
        .stApp {background-color: #000000;}
        </style>
    """, unsafe_allow_html=True)
    st.title("🔒 Access Encrypted Data")
    st.markdown("<p style='font-size: 16px; color: #ffffff;'>You are now accessing encrypted data. Decryption in progress (simulated):</p>", unsafe_allow_html=True)
    with st.spinner("Decrypting..."):
        time.sleep(2)
    st.success("✅ Data decrypted successfully!")
    st.button("🔙 Back to Dashboard", on_click=lambda: st.session_state.update({"current_page": "dashboard"}))

def monitor_security_logs():
    st.markdown("""
        <style>
        .stApp {background-color: #000000;}
        </style>
    """, unsafe_allow_html=True)
    st.title("📊 Monitor Security Logs")
    st.markdown("<p style='font-size: 16px; color: #ffffff;'>Viewing security logs. Here’s a sample log entry:</p>", unsafe_allow_html=True)
    st.text("2025-05-09 10:00:00 - User authenticated successfully.")
    st.text("2025-05-09 09:45:00 - Access attempt blocked.")
    st.button("🔙 Back to Dashboard", on_click=lambda: st.session_state.update({"current_page": "dashboard"}))

def user_dashboard():
    if "authenticated_user" not in st.session_state:
        st.warning("⚠️ Unauthorized Access! Please authenticate first.")
        return

    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "dashboard"

    user_name = st.session_state["authenticated_user"]
    st.markdown("""
        <style>
        .stApp {background-color: #000000;}
        .stButton>button {background-color: #FF9800; color: white; border-radius: 5px; padding: 10px 24px;}
        .stButton>button:hover {background-color: #F57C00;}
        </style>
    """, unsafe_allow_html=True)

    if st.session_state["current_page"] == "dashboard":
        st.title("☁️ Secure Cloud Access")
        st.markdown(f"### 👋 Welcome, **{user_name}**! 🎉", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 16px; color: #ffffff;'>You have successfully authenticated using multi-factor biometric authentication.</p>", unsafe_allow_html=True)

        st.subheader("🔐 Cloud Operations")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.button("📂 View Secure Files", on_click=lambda: st.session_state.update({"current_page": "view_secure_files"}))
        with col2:
            st.button("🔒 Access Encrypted Data", on_click=lambda: st.session_state.update({"current_page": "access_encrypted_data"}))
        with col3:
            st.button("📊 Monitor Security Logs", on_click=lambda: st.session_state.update({"current_page": "monitor_security_logs"}))

        st.subheader("🛡️ Security Monitoring & Alerts")
        st.info("🚀 Security logs & threat detection will be integrated soon!")

        st.button("🔓 Logout", on_click=logout)
    elif st.session_state["current_page"] == "view_secure_files":
        view_secure_files()
    elif st.session_state["current_page"] == "access_encrypted_data":
        access_encrypted_data()
    elif st.session_state["current_page"] == "monitor_security_logs":
        monitor_security_logs()

if __name__ == "__main__":
    user_dashboard()