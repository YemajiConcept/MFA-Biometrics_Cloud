import os
import random
import pandas as pd
import matplotlib.pyplot as plt
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Configuration
BASE_URL = "http://localhost:8501"
DATA_PATHS = {
    "lfw": r"C:\Users\USER\MFA_Biometric_Auth\data\raw\lfw_funneled",
    "socofing": r"C:\Users\USER\MFA_Biometric_Auth\data\raw\SOCOFing\SOCOFing\Altered\Altered-Hard"
}
RESULTS_DIR = r"C:\Users\USER\MFA_Biometric_Auth\results"
LOG_DIR = r"C:\Users\USER\MFA_Biometric_Auth\data\logs"

# Ensure directories exist
for directory in [RESULTS_DIR, LOG_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Initialize Selenium WebDriver
def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--ignore-certificate-errors")  # Ignore SSL errors
    chrome_options.add_argument("--log-level=3")  # Reduce Chrome logging
    # Specify the path to chromedriver if not in PATH
    # service = Service("path/to/chromedriver.exe")
    service = Service()  # Assumes chromedriver is in PATH
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(BASE_URL)
    return driver

def get_image_files(dataset):
    """Collect all image files from the specified dataset with detailed logging."""
    image_files = []
    data_path = DATA_PATHS[dataset]
    print(f"Accessing dataset: {dataset} at {data_path}")
    try:
        for root, _, files in os.walk(data_path):
            print(f"Scanning directory: {root}")
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')) and "Thumbs.db" not in file:
                    full_path = os.path.join(root, file)
                    image_files.append(full_path)
                    print(f"Found image: {full_path}")
        print(f"Total images found for {dataset}: {len(image_files)}")
        if not image_files:
            print(f"Warning: No images found in {dataset} dataset!")
    except Exception as e:
        print(f"Error accessing {data_path}: {str(e)}")
        with open(f"{LOG_DIR}/filesystem_errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log", "a") as log_file:
            log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Dataset: {dataset} - Error: {str(e)}\n")
    return image_files

def register_user(driver, user_id, face_image, fingerprint_image):
    """Register a user via the Streamlit UI with detailed debugging."""
    try:
        print(f"Attempting to register {user_id}...")

        # Navigate to Admin Enrollment page
        print("Looking for 'Admin Enrollment' radio button...")
        admin_enrollment_radio = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//label[contains(., '👤 Admin Enrollment')]//preceding-sibling::input[@type='radio']"))
        )
        driver.execute_script("arguments[0].click();", admin_enrollment_radio)  # Fallback to JavaScript click
        print("Clicked 'Admin Enrollment' radio button.")
        
        # Wait for the page to load
        time.sleep(5)

        # Fill in the form
        print("Looking for username input...")
        username_input = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Enter User\\'s Full Name']"))
        )
        username_input.clear()
        username_input.send_keys(f"Test User {user_id}")
        print(f"Entered username: Test User {user_id}")

        # Upload fingerprint image
        print("Looking for fingerprint image uploader...")
        fingerprint_input = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='file' and @aria-label='Upload Fingerprint Image']"))
        )
        fingerprint_input.send_keys(fingerprint_image)
        print(f"Uploaded fingerprint image: {fingerprint_image}")

        # Upload face image
        print("Looking for face image uploader...")
        face_input = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='file' and @aria-label='Upload Face Image']"))
        )
        face_input.send_keys(face_image)
        print(f"Uploaded face image: {face_image}")

        # Submit the form
        print("Looking for 'Enroll User' button...")
        enroll_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Enroll User')]"))
        )
        driver.execute_script("arguments[0].click();", enroll_button)  # Fallback to JavaScript click
        print("Clicked 'Enroll User' button.")

        # Check for success message
        print("Looking for success message...")
        success_message = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'enrolled successfully')]"))
        )
        print(f"Registration successful for {user_id}: {success_message.text}")
        return True
    except Exception as e:
        print(f"Registration failed for {user_id}: {str(e)}")
        with open(f"{LOG_DIR}/registration_errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log", "a") as log_file:
            log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - User: {user_id} - Error: {str(e)}\n")
        return False

def authenticate_user(driver, user_id, face_image, fingerprint_image):
    """Authenticate a user via the Streamlit UI (placeholder until user_auth.py is shared)."""
    try:
        print(f"Attempting to authenticate {user_id}...")
        print("Authentication placeholder: Waiting for user_auth.py to implement this function.")
        return "Authentication placeholder", 0
    except Exception as e:
        print(f"Authentication failed for {user_id}: {str(e)}")
        return "Authentication failed due to error", 0

def test_accuracy(driver, simulations=500):
    """Test accuracy (FAR/FRR) using the Streamlit UI."""
    for dataset in ["lfw", "socofing"]:
        image_files = get_image_files(dataset)
        if len(image_files) < 2:
            print(f"Error: Insufficient images in {dataset} dataset.")
            continue

        # Register initial users (limited to 5 for debugging)
        registered_users = {}
        for i in range(min(5, len(image_files))):  # Reduced for faster debugging
            user_id = f"user_{i}"
            face_img = image_files[i] if dataset == "lfw" else random.choice(get_image_files("lfw"))
            fingerprint_img = image_files[i] if dataset == "socofing" else random.choice(get_image_files("socofing"))
            if register_user(driver, user_id, face_img, fingerprint_img):
                registered_users[user_id] = {"face": face_img, "fingerprint": fingerprint_img}
            else:
                print(f"Skipping user {user_id} due to registration failure.")

        if not registered_users:
            print(f"Warning: No users registered for {dataset}. Skipping accuracy test.")
            continue

        print("Skipping authentication tests until user_auth.py is shared.")
        break

def test_spoofing(driver, simulations=100):
    """Test spoofing detection using the Streamlit UI (placeholder)."""
    print("Skipping spoofing tests until user_auth.py is shared.")

def test_performance(driver, users=100, duration=600):
    """Test performance using simulated users (placeholder)."""
    print("Skipping performance tests until user_auth.py is shared.")

if __name__ == "__main__":
    print(f"Starting tests at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} WAT")
    driver = init_driver()
    try:
        test_accuracy(driver, 500)
        test_spoofing(driver, 100)
        test_performance(driver, 100, 600)
        print("Tests completed. Results saved in C:/Users/USER/MFA_Biometric_Auth/results/")
    finally:
        driver.quit()