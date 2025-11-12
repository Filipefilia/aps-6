import cv2
import numpy as np
import os
import face_recognition
from config.config import DATASET_DIR

def _calculate_ear(eye_landmarks):
    """Calculates the Eye Aspect Ratio (EAR) for a single eye."""
    # Vertical eye landmarks
    v1 = np.linalg.norm(np.array(eye_landmarks[1]) - np.array(eye_landmarks[5]))
    v2 = np.linalg.norm(np.array(eye_landmarks[2]) - np.array(eye_landmarks[4]))
    # Horizontal eye landmark
    h = np.linalg.norm(np.array(eye_landmarks[0]) - np.array(eye_landmarks[3]))
    # Compute EAR
    ear = (v1 + v2) / (2.0 * h)
    return ear

def _calculate_mar(mouth_landmarks):
    """Calculates the Mouth Aspect Ratio (MAR) for detecting a smile."""
    # Vertical mouth landmarks
    v1 = np.linalg.norm(np.array(mouth_landmarks[13]) - np.array(mouth_landmarks[19]))
    v2 = np.linalg.norm(np.array(mouth_landmarks[14]) - np.array(mouth_landmarks[18]))
    v3 = np.linalg.norm(np.array(mouth_landmarks[15]) - np.array(mouth_landmarks[17]))
    # Horizontal mouth landmark
    h = np.linalg.norm(np.array(mouth_landmarks[12]) - np.array(mouth_landmarks[16]))
    # Compute MAR
    mar = (v1 + v2 + v3) / (2.0 * h)
    return mar

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

def process_frame_for_recognition(frame, known_face_encodings, known_face_names, known_face_access_levels, draw_annotations=True):
    """
    Processes a single frame to detect and recognize faces and facial landmarks.
    
    Args:
        frame: The input frame to process
        known_face_encodings: List of known face encodings
        known_face_names: List of corresponding names
        known_face_access_levels: List of corresponding access levels
        draw_annotations: Whether to draw rectangles and names on the frame (default: True)
    
    Returns:
        A tuple containing:
        - The processed frame (with or without rectangles and names drawn on it).
        - The name of the recognized person ("Unknown" if not recognized).
        - The access level of the recognized person ("" if not recognized).
        - The average Eye Aspect Ratio (EAR) of the detected face.
        - The Mouth Aspect Ratio (MAR) of the detected face.
    """
    TOLERANCE = 0.6
    
    # Convert frame to RGB for face_recognition library (moderate resize for performance)
    small_frame = cv2.resize(frame, (0, 0), fx=0.75, fy=0.75)
    rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    
    # Find all face locations and landmarks in the resized frame
    face_locations = face_recognition.face_locations(rgb_frame)
    face_landmarks_list = face_recognition.face_landmarks(rgb_frame, face_locations)
    
    # Scale back face locations to original frame size
    scale_factor = 1.0 / 0.75
    face_locations = [(int(top*scale_factor), int(right*scale_factor), int(bottom*scale_factor), int(left*scale_factor)) 
                     for (top, right, bottom, left) in face_locations]
    
    recognized_name = "Unknown"
    recognized_access_level = ""
    ear = 0.0
    mar = 0.0

    # Process the first detected face
    if face_locations:
        face_location = face_locations[0]
        face_landmarks = face_landmarks_list[0]

        # Scale landmarks back to original frame size
        scale_factor = 1.0 / 0.75
        scaled_landmarks = {}
        for feature_name, points in face_landmarks.items():
            scaled_landmarks[feature_name] = [(int(x*scale_factor), int(y*scale_factor)) for (x, y) in points]

        # Get encoding for the current face from small frame
        small_face_location = (int(face_location[0]/scale_factor), int(face_location[1]/scale_factor), 
                              int(face_location[2]/scale_factor), int(face_location[3]/scale_factor))
        current_face_encodings = face_recognition.face_encodings(rgb_frame, [small_face_location])

        name = "Unknown"
        access_level = ""
        if current_face_encodings:
            face_distances = face_recognition.face_distance(known_face_encodings, current_face_encodings[0])
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if face_distances[best_match_index] < TOLERANCE:
                    name = known_face_names[best_match_index]
                    access_level = known_face_access_levels[best_match_index]
        
        recognized_name = name
        recognized_access_level = access_level

        # Calculate EAR and MAR using scaled landmarks
        left_eye_ear = _calculate_ear(scaled_landmarks['left_eye'])
        right_eye_ear = _calculate_ear(scaled_landmarks['right_eye'])
        ear = (left_eye_ear + right_eye_ear) / 2.0
        mar = _calculate_mar(scaled_landmarks['top_lip'] + scaled_landmarks['bottom_lip'])

        # Draw rectangle and name on the frame only if annotations are enabled
        if draw_annotations:
            top, right, bottom, left = face_location
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    return frame, recognized_name, recognized_access_level, ear, mar

def recognize_faces_in_video():
    """
    Main loop for testing recognition; not used by the GUI app.
    """
    known_face_encodings, known_face_names, known_face_access_levels = load_known_faces()

    if not known_face_names:
        return

    cap = cv2.VideoCapture(2)
    if not cap.isOpened():
        print("[ERROR] Could not open camera")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Could not capture frame")
            break

        frame, name, access_level, ear, mar = process_frame_for_recognition(frame, known_face_encodings, known_face_names, known_face_access_levels)
        
        # Display EAR and MAR for debugging
        cv2.putText(frame, f"EAR: {ear:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"MAR: {mar:.2f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow('Face Recognition', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    recognize_faces_in_video()