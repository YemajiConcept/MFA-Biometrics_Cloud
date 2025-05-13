# Biometric Multi-Factor Authentication (MFA) System

This project implements a secure biometric-based Multi-Factor Authentication (MFA) system for cloud environments, integrating fingerprint and facial recognition with AI-driven anomaly detection and advanced encryption. It is deployed on AWS Elastic Beanstalk, using Amazon S3 for biometric template storage, RDS PostgreSQL for user metadata, and AWS KMS for encryption key management. The system achieves a False Acceptance Rate (FAR) and False Rejection Rate (FRR) below 5%, 90% spoofing detection, 100% replay attack prevention, and an average latency of 500 ms for 100 concurrent users, with a user satisfaction score of 4/5 via a Streamlit interface.

This work was developed as part of a dissertation for an MSc in Computer Science (Cyber Security) at Staffordshire University, focusing on enhancing cloud security through biometric MFA, AI, and encryption.

## Features
- **Biometric Authentication**: Uses FaceNet for facial recognition and minutiae-based algorithms for fingerprint recognition.
- **Datasets**: Utilizes Labeled Faces in the Wild (LFW) and Sokoto Fingerprint (SOCOFing) datasets for training and testing.
- **Security Enhancements**:
  - Fernet encryption with AWS KMS for securing biometric templates.
- **Cloud Deployment**: Hosted on AWS Elastic Beanstalk with autoscaling for scalability.
- **User Interface**: Streamlit-based UI for enrollment and authentication, scoring 4/5 in user satisfaction.
- **Privacy Compliance**: GDPR-compliant with encrypted template storage and no retention of raw biometric data.

## Prerequisites
- **Software**:
  - Python 3.9
  - AWS CLI (configured with your credentials)
  - Elastic Beanstalk CLI (`eb`)
  - Docker (for containerized deployment)
  - PostgreSQL client (`psql`) for local testing
- **Hardware** (Recommended for Development):
  - CPU: Intel Core i7 or equivalent
  - RAM: 16GB
  - GPU: NVIDIA GTX 1660 Ti or better (for FaceNet inference)
- **AWS Services**:
  - Elastic Beanstalk, S3, RDS PostgreSQL, KMS, Lambda, Secrets Manager
  - Ensure your AWS account has appropriate permissions (e.g., `AmazonS3FullAccess`, `AWSKMSFullAccess`).
- **Datasets** (Not Included in Repo):
  - LFW dataset for facial recognition
  - SOCOFing dataset for fingerprint recognition
  - Place datasets in a `data/` directory (excluded from Git via `.gitignore`).
- **Model Files** (Not Included in Repo):
  - FaceNet model files (e.g., `saved_model.pb`, `variables/`)
  - Place in `models/facenet_tensorflow/` (excluded from Git via `.gitignore`).

## Installation and Setup
1. **Clone the Repository**:
   ```bash
   git clone https://YemajiConcept@github.com/YemajiConcept/MFA-Biometrics_Cloud.git
   cd scripts
      ```

2. **Install Dependencies**:
   - Create a virtual environment and install required packages:
     ```bash
     python -m venv venv
     source venv/bin/activate  # On Windows: venv\Scripts\activate
     pip install -r requirements.txt
     ```
   - Key dependencies include `tensorflow`, `opencv-python`, `scikit-learn`, `streamlit`, `boto3`, `psycopg2`, and `cryptography`.

3. **Download Datasets and Models**:
   - **LFW Dataset**: Download from [http://vis-www.cs.umass.edu/lfw/](http://vis-www.cs.umass.edu/lfw/) and place in `data/raw/lfw_funneled/`.
   - **SOCOFing Dataset**: Obtain from the official source and place in `data/raw/SOCOFing/`.
   - **FaceNet Model**: Download the TensorFlow FaceNet model and place in `models/facenet_tensorflow/`.
   - Note: These files are excluded from the repository due to size and sensitivity.

4. **Configure AWS Credentials**:
   - Ensure your AWS CLI is configured:
     ```bash
     aws configure
     ```
   - Set up environment variables for sensitive configurations in `.ebextensions/options.config`:
     ```yaml
     option_settings:
       aws:elasticbeanstalk:application:environment:
         db_user: your_db_user
         db_password: your_db_password
         db_host: your_db_host
         db_port: 5432
         db_name: postgres
         kms_key_id: your_kms_key_id
         BUCKET_NAME: your_bucket_name
     ```
   - Alternatively, set these as environment variables in your Elastic Beanstalk environment.

5. **Initialize the Database**:
   - Set up an RDS PostgreSQL instance and note the credentials.
   - Update `database.py` to use environment variables for DB connection (already configured to use `os.environ`).

## Deployment on AWS Elastic Beanstalk
1. **Initialize Elastic Beanstalk**:
   ```bash
   eb init -p docker mfa-app --region us-east-1
   ```
   - Select your AWS region and application name.

2. **Create Environment**:
   ```bash
   eb create mfa-env --instance_type t3.large --scale 1-5
   ```
   - This sets up an environment with auto-scaling (1-5 instances).

3. **Deploy the Application**:
   ```bash
   eb deploy
   ```

4. **Access the App**:
   - Open the application URL:
     ```bash
     eb open
     ```
   - The Streamlit interface will be accessible (e.g., `http://mfa-env.us-east-1.elasticbeanstalk.com:8501`).

## Usage
1. **Run Locally (Optional)**:
   - Start the Streamlit app locally for testing:
     ```bash
     streamlit run Testing/scripts/main.py
     ```
   - Access at `http://localhost:8501`.

2. **Enrollment**:
   - Use the Streamlit interface (`admin_enroll.py`) to register users.
   - Upload a facial image (JPG) and a fingerprint image (BMP).
   - The system will extract features, encrypt them, and store them in S3 with metadata in RDS.

3. **Authentication**:
   - Use the authentication interface (`main.py`) to verify users.
   - Upload live facial and fingerprint images.
   - The system will compare against stored templates, perform liveness detection, and check for anomalies.

4. **Monitoring**:
   - Check CloudWatch logs for performance metrics (e.g., latency, scaling events).
   - View RDS logs for authentication attempts and anomaly detection results.

## Project Structure
- `Testing/scripts/`: Core Python scripts for the application.
  - `main.py`: Streamlit app for user authentication.
  - `admin_enroll.py`: Interface for enrolling new users.
  - `face_recognition.py`, `register_face.py`, `face_auth.py`: Facial recognition and authentication logic.
  - `database.py`: Database connection and management.
  - `config.py`: Configuration settings (uses environment variables).
- `.ebextensions/`: Elastic Beanstalk configuration files (e.g., `options.config`, excluded from Git).
- `requirements.txt`: Python dependencies.
- `Dockerfile`: Configuration for containerized deployment on Elastic Beanstalk.

## Security and Privacy Notes
- **Sensitive Data**: Do not commit AWS credentials, RDS credentials, or KMS keys to Git. Use environment variables or AWS Secrets Manager.
- **Biometric Data**: Raw biometric data is not stored; only encrypted templates are kept in S3.
- **GDPR Compliance**: The system ensures privacy by encrypting templates and deleting raw data after processing.

## Future Work
- Integrate additional biometric modalities (e.g., iris, voice) for a more robust multi-modal system.
- Explore blockchain for decentralized, tamper-proof template storage.
- Optimize FaceNet and Isolation Forest for resource-constrained devices using lightweight architectures or federated learning.
- Conduct broader testing to mitigate demographic biases across diverse populations.


## Acknowledgments
This project was developed as part of a dissertation under the supervision of Dr. Hassan Malik at Staffordshire University. Special thanks to the university staff, family, and friends for their support.
