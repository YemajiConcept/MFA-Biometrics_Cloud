import streamlit as st

def about_us():
    """About Us - Detailed Explanation of Algorithms Used in MFA Biometric System"""

    st.title("📖 About Us - Multi-Factor Authentication System")
    
    st.markdown("""
    ## 🔍 Introduction  
    Welcome to the **Multi-Factor Authentication (MFA) Biometric System**. This system enhances security using **fingerprint and facial recognition** to authenticate users. Below, we provide an in-depth explanation of the technologies, datasets, and algorithms used in this project.  

    **👨‍💻 Author:** Ajileru  
    **🔬 Core Technologies:**  
    - **Fingerprint Recognition:** Feature extraction using SOCOFing dataset  
    - **Facial Recognition:** Deep learning using LFW dataset and FaceNet model  
    - **Authentication:** Euclidean distance-based identity verification  
    """)

    st.markdown("---")

    # 📌 DATA COLLECTION SECTION
    st.header("📂 Data Collection & Preprocessing")
    
    st.subheader("1️⃣ Facial Recognition Dataset - LFW")
    st.markdown("""
    - We use the **Labeled Faces in the Wild (LFW) dataset**, a collection of over **13,000 images of faces** from the internet.  
    - Each image is labeled with the person's name, allowing us to build a dataset of known identities.  
    - **Preprocessing Steps:**
      - Convert images to grayscale (if needed)  
      - Resize images to **160x160 pixels** (FaceNet input size)  
      - Normalize pixel values  
      - Extract **128-dimensional feature vectors** using **FaceNet**  
    """)

    st.subheader("2️⃣ Fingerprint Recognition Dataset - SOCOFing")
    st.markdown("""
    - We use the **SOCOFing dataset**, which contains **6,000 fingerprint images**.  
    - Each fingerprint has variations such as rotation, occlusion, and altered pressure, making it ideal for training robust models.  
    - **Preprocessing Steps:**
      - Convert images to grayscale  
      - Apply **Gabor filters** to enhance ridge structures  
      - Extract **minutiae points** (ridge endings and bifurcations)  
      - Generate feature vectors for authentication  
    """)

    st.markdown("---")

    # 📌 FEATURE EXTRACTION SECTION
    st.header("🧠 Feature Extraction Techniques")
    
    st.subheader("🔹 Face Feature Extraction - FaceNet")
    st.markdown("""
    - We use **FaceNet**, a deep learning model that maps images to a **128-dimensional embedding space**.  
    - **Steps:**
      1. The input face image is passed through a **pretrained FaceNet model**.
      2. The network extracts **high-level facial features**.
      3. The output is a **128-dimensional vector** that represents the face.
      4. During authentication, the new face embedding is compared with stored embeddings using **Euclidean distance**.
    """)

    st.subheader("🔹 Fingerprint Feature Extraction - Minutiae-based")
    st.markdown("""
    - We use a **minutiae-based extraction approach**, which identifies **ridge endings and bifurcations**.  
    - **Steps:**
      1. Apply **Gabor filters** to enhance ridges.  
      2. Detect **ridge endings and bifurcations**.  
      3. Encode these features as a **fixed-length vector**.  
      4. During authentication, compare the new feature vector with stored ones using **Euclidean distance**.  
    """)

    st.markdown("---")

    # 📌 AUTHENTICATION PROCESS
    st.header("🔐 Authentication Process")
    st.markdown("""
    Our system requires **both fingerprint and face verification** to authenticate a user.

    ### 1️⃣ Fingerprint Authentication
    - Extracts **fingerprint features** from uploaded images.
    - Compares the extracted feature vector with stored vectors.
    - If the **Euclidean distance is below the threshold**, authentication succeeds.

    ### 2️⃣ Face Authentication
    - Extracts **face embeddings** using **FaceNet**.
    - Compares with stored embeddings using **Euclidean distance**.
    - If the distance is below **1.0**, authentication succeeds.

    ### 3️⃣ Multi-Factor Decision
    - If **both** fingerprint and face authentication succeed, access is granted.
    - If either fails, authentication is **denied**.
    """)

    st.markdown("---")

    # 📌 SECURITY MEASURES
    st.header("🛡 Security Measures")
    
    st.subheader("✅ Preventing Spoof Attacks")
    st.markdown("""
    - Liveness detection techniques can be added to prevent attacks using **fake fingerprints or photos**.  
    - Possible solutions:
      - **Fingerprint Texture Analysis**: Detects artificial fingerprint materials.  
      - **Blink Detection in Faces**: Ensures a real face instead of a static image.  
    """)

    st.subheader("✅ Secure Storage")
    st.markdown("""
    - Biometric data is **not stored as raw images** but as **feature vectors**.  
    - **Encryption methods** like AES-256 can be used to protect stored embeddings.  
    """)

    st.markdown("---")

    st.header("🚀 Conclusion")
    st.markdown("""
    Our MFA biometric system leverages state-of-the-art techniques in **fingerprint and facial recognition**.  
    By using the **LFW** and **SOCOFing** datasets, along with **FaceNet** for face embeddings and **minutiae-based fingerprint recognition**, we ensure a **robust and secure** authentication process.  
    """)

    st.success("🔑 Thank you for using our secure biometric authentication system!")

# ✅ Run the page
if __name__ == "__main__":
    about_us()
