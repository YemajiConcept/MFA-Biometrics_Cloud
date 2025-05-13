import numpy as np
from database import get_all_fingerprints, get_all_faces

def check_database_duplicates():
    # Check fingerprints
    fingerprints = get_all_fingerprints()
    for name1, vec1 in fingerprints.items():
        for name2, vec2 in fingerprints.items():
            if name1 != name2:
                distance = np.linalg.norm(vec1 / np.linalg.norm(vec1) - vec2 / np.linalg.norm(vec2))
                if distance < 1e-6:
                    print(f"⚠️ Duplicate fingerprint detected: {name1} and {name2} (Distance: {distance})")

    # Check faces
    faces = get_all_faces()
    for name1, vec1 in faces.items():
        for name2, vec2 in faces.items():
            if name1 != name2:
                distance = np.linalg.norm(vec1 / np.linalg.norm(vec1) - vec2 / np.linalg.norm(vec2))
                if distance < 1e-6:
                    print(f"⚠️ Duplicate face detected: {name1} and {name2} (Distance: {distance})")

if __name__ == "__main__":
    check_database_duplicates()