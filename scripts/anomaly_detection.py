# anomaly_detection.py
from sklearn.ensemble import IsolationForest
import pandas as pd

fingerprint_logs = pd.DataFrame(columns=["username", "fingerprint_distance", "timestamp"])
face_logs = pd.DataFrame(columns=["username", "face_distance", "timestamp"])

def log_fingerprint_auth(username, fingerprint_distance):
    global fingerprint_logs
    new_log = pd.DataFrame({
        "username": [username],
        "fingerprint_distance": [fingerprint_distance],
        "timestamp": [pd.Timestamp.now()]
    })
    fingerprint_logs = pd.concat([fingerprint_logs, new_log], ignore_index=True)

def log_face_auth(username, face_distance):
    global face_logs
    new_log = pd.DataFrame({
        "username": [username],
        "face_distance": [face_distance],
        "timestamp": [pd.Timestamp.now()]
    })
    face_logs = pd.concat([face_logs, new_log], ignore_index=True)

def detect_fingerprint_anomaly(username, fingerprint_distance):
    global fingerprint_logs
    model = IsolationForest(contamination=0.1)
    if len(fingerprint_logs) < 10:
        return False
    features = fingerprint_logs[["fingerprint_distance"]]
    model.fit(features)
    new_data = np.array([[fingerprint_distance]])
    prediction = model.predict(new_data)
    return prediction[0] == -1

def detect_face_anomaly(username, face_distance):
    global face_logs
    model = IsolationForest(contamination=0.1)
    if len(face_logs) < 10:
        return False
    features = face_logs[["face_distance"]]
    model.fit(features)
    new_data = np.array([[face_distance]])
    prediction = model.predict(new_data)
    return prediction[0] == -1