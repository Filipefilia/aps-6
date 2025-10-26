import cv2
import numpy as np
import os
import face_recognition
from config.config import DATASET_DIR

def load_known_faces():
    """
    Loads all known face encodings from the dataset directory.
    Returns tuple of (encodings, names, access_levels)
    """
    known_face_encodings = []
    known_face_names = []
    known_face_access_levels = []

    print("[INFO] Loading known faces...")
    if not os.path.exists(DATASET_DIR):
        print(f"[ERROR] Dataset directory not found at {DATASET_DIR}")
        return [], [], []

    for user_folder in os.listdir(DATASET_DIR):
        user_dir_path = os.path.join(DATASET_DIR, user_folder)
        if os.path.isdir(user_dir_path):
            # Extract user name and access level from folder name "access_levelX-username"
            try:
                parts = user_folder.split('-', 1)
                access_level_part = parts[0]
                user_name = parts[1]
                access_level = access_level_part.replace('access_level', '')
            except IndexError:
                print(f"[WARNING] Skipping folder with unexpected name format: {user_folder}")
                continue

            encodings_file = os.path.join(user_dir_path, "encodings.npy")
            if os.path.exists(encodings_file):
                encodings = np.load(encodings_file)
                for encoding in encodings:
                    known_face_encodings.append(encoding)
                    known_face_names.append(user_name)
                    known_face_access_levels.append(access_level)
                print(f"[INFO] Loaded {len(encodings)} encodings for user: {user_name} (Access Level: {access_level})")
            else:
                print(f"[WARNING] No encodings.npy file found for user: {user_name}")
    
    if not known_face_encodings:
        print("[ERROR] No known faces loaded. Please register users first.")

    return known_face_encodings, known_face_names, known_face_access_levels

# Find the path to the haarcascade file more robustly
cv2_base_dir = os.path.dirname(os.path.abspath(cv2.__file__))
HAAR_CASCADE_PATH = os.path.join(cv2_base_dir, 'data', 'haarcascade_frontalface_default.xml')
face_cascade = cv2.CascadeClassifier(HAAR_CASCADE_PATH)

def process_frame_for_recognition(frame, known_face_encodings, known_face_names, known_face_access_levels):
    """
    Processes a single frame to detect and recognize faces.
    
    Args:
        frame: The video frame to process.
        known_face_encodings: A list of known face encodings.
        known_face_names: A list of names corresponding to the encodings.
        known_face_access_levels: A list of access levels corresponding to the encodings.
        
    Returns:
        A tuple containing:
        - The processed frame with rectangles and names drawn on it.
        - The name of the recognized person ("Unknown" if not recognized).
        - The access level of the recognized person ("" if not recognized).
    """
    TOLERANCE = 0.6  # Lower is more strict

    # Use Haar Cascade for fast face location
    grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(grey, scaleFactor=1.2, minNeighbors=5, minSize=(100, 100))

    # Convert frame to RGB for face_recognition library
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    recognized_name = "Unknown"
    recognized_access_level = ""

    # Process each face found
    for (x, y, w, h) in faces:
        # The face_recognition library uses CSS order (top, right, bottom, left)
        face_location = (y, x + w, y + h, x)
        
        # Get encoding for the current face
        current_face_encodings = face_recognition.face_encodings(rgb_frame, [face_location])

        name = "Unknown"
        access_level = ""
        if current_face_encodings:
            # Compare the current face with all known faces
            face_distances = face_recognition.face_distance(known_face_encodings, current_face_encodings[0])
            
            best_match_index = np.argmin(face_distances)
            if face_distances[best_match_index] < TOLERANCE:
                name = known_face_names[best_match_index]
                access_level = known_face_access_levels[best_match_index]
        
        recognized_name = name
        recognized_access_level = access_level

        # Draw rectangle and name on the frame
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
        cv2.rectangle(frame, (x, y+h - 35), (x+w, y+h), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (x + 6, y+h - 6), font, 1.0, (255, 255, 255), 1)

    return frame, recognized_name, recognized_access_level

def recognize_faces_in_video():
    """
    Captures video from the camera, detects and recognizes faces in real-time using a separate processing function.
    """
    known_face_encodings, known_face_names, known_face_access_levels = load_known_faces()

    if not known_face_names:
        return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Could not open camera")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Could not capture frame")
            break

        frame, name, access_level = process_frame_for_recognition(frame, known_face_encodings, known_face_names, known_face_access_levels)

        # Here you could add logic based on the access_level
        # For example:
        # if name != "Unknown":
        #     from config.config import REQUIRED_ACCESS_LEVEL
        #     if int(access_level) >= int(REQUIRED_ACCESS_LEVEL):
        #         print(f"Access Granted for {name}")
        #     else:
        #         print(f"Access Denied for {name} (Insufficient Level)")


        cv2.imshow('Face Recognition', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    recognize_faces_in_video()