import cv2
import numpy as np

def detect_blink(video_path, num_frames=30):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")

    cap = cv2.VideoCapture(video_path)
    blink_detected = False
    frame_count = 0
    eyes_open_frames = 0

    while frame_count < num_frames:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            eyes = eye_cascade.detectMultiScale(roi_gray)
            if len(eyes) >= 2:
                eyes_open_frames += 1
            elif eyes_open_frames > 0:
                blink_detected = True
                break
        frame_count += 1
    cap.release()
    return blink_detected