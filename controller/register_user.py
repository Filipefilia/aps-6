import cv2
import numpy as np
import os
import time
from pathlib import Path
import face_recognition
from config.config import DATASET_DIR
import tkinter as tk
from PIL import Image, ImageEnhance, ImageFilter
import random

# constant setups
PICTURE_QT = 20
CAPTURE_LAPSE = 1.0
CAPTURE_PREPARATION = 3
MIN_WIDHT = 150
MIN_HEIGHT = 150

# Data Augmentation settings
AUGMENTATION_FACTOR = 4  # Generate 4 augmented versions per original
ENABLE_AUGMENTATION = True

def set_augmentation_level(level="standard"):
    """
    Configure augmentation level based on requirements.
    Levels: 'basic' (2x), 'standard' (4x), 'enhanced' (6x), 'maximum' (8x)
    """
    global AUGMENTATION_FACTOR
    levels = {
        'basic': 2,
        'standard': 4, 
        'enhanced': 6,
        'maximum': 8
    }
    AUGMENTATION_FACTOR = levels.get(level, 4)
    print(f"[INFO] Augmentation level set to '{level}' ({AUGMENTATION_FACTOR}x factor)")
    return AUGMENTATION_FACTOR

def apply_data_augmentation(image):
    """
    Apply various augmentation techniques to improve dataset diversity and robustness.
    Returns a list of augmented images including the original.
    """
    augmented_images = [image]  # Start with original
    
    if not ENABLE_AUGMENTATION:
        return augmented_images
    
    # Convert to PIL for easier manipulation
    pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    
    # 1. Brightness variations (simulate different lighting conditions)
    brightness_variations = [0.7, 0.85, 1.15, 1.3]
    for brightness in brightness_variations[:2]:  # Use 2 variations
        enhancer = ImageEnhance.Brightness(pil_image)
        bright_img = enhancer.enhance(brightness)
        augmented_images.append(cv2.cvtColor(np.array(bright_img), cv2.COLOR_RGB2BGR))
    
    # 2. Contrast adjustments (improve robustness to different cameras)
    contrast_variations = [0.8, 1.2]
    for contrast in contrast_variations:
        enhancer = ImageEnhance.Contrast(pil_image)
        contrast_img = enhancer.enhance(contrast)
        augmented_images.append(cv2.cvtColor(np.array(contrast_img), cv2.COLOR_RGB2BGR))
    
    # 3. Slight rotations (head pose variations)
    rotation_angles = [-5, 5]
    for angle in rotation_angles:
        rotated = pil_image.rotate(angle, expand=False, fillcolor=(128, 128, 128))
        augmented_images.append(cv2.cvtColor(np.array(rotated), cv2.COLOR_RGB2BGR))
    
    # 4. Gaussian blur (simulate slight motion or focus issues)
    blurred = pil_image.filter(ImageFilter.GaussianBlur(radius=0.5))
    augmented_images.append(cv2.cvtColor(np.array(blurred), cv2.COLOR_RGB2BGR))
    
    # 5. Horizontal flip (mirror image for additional variation)
    flipped = pil_image.transpose(Image.FLIP_LEFT_RIGHT)
    augmented_images.append(cv2.cvtColor(np.array(flipped), cv2.COLOR_RGB2BGR))
    
    return augmented_images[:AUGMENTATION_FACTOR + 1]  # Return original + augmentations

# user dir setup
def create_new_user(user_name, access_level):
    folder_name = f"access_level{access_level}-{user_name}"
    user_dir = os.path.join(DATASET_DIR, folder_name)

    os.makedirs(user_dir)

    if not os.path.exists(user_dir):
        print("[ERROR] Could not create folder")
        return "null"
    
    print(f"[INFO] Folder created in path: {user_dir}")

    path_user_dir = Path(user_dir)
    return path_user_dir

def register_user_face(user_dir):
    cap = cv2.VideoCapture(2)

    if not cap.isOpened():
        print("[ERROR] Could not open camera")
        exit()

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    print("\n[INSTRUCT] Look at the camera and press 'k' to capture images")
    print(f"[INSTRUCT] Press 'q' to leave at any moment")

    count_photos = 0
    while count_photos < PICTURE_QT:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Could not capture frame")
            break
        
        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(grey, scaleFactor=1.2, minNeighbors=5, minSize=(MIN_WIDHT, MIN_HEIGHT))

        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        cv2.putText(frame, f"Press 'k' to capture ({count_photos}/{PICTURE_QT})", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, "Press 'q' to leave", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow('User registration - Capture face', frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('k'):
            if len(faces) > 0:
                picture_dir = os.path.join(user_dir, f"{count_photos}.jpg")

                face_img = frame[y:y+h, x:x+w]
                cv2.imwrite(picture_dir, face_img)
                print(f"[INFO] Picture {count_photos} saved in path: {picture_dir}")
                
                count_photos += 1

        if key == ord('q'):
            break
    
    print(f"\n[SUCCESS] {count_photos} pictures captured")
    cap.release()
    cv2.destroyAllWindows()

def register_new_user():
    # initial setup
    user_name = input("Inform user name: ")
    access_level = input("Inform user access level: ")

    user_dir = create_new_user(user_name, access_level)

    if user_dir != "null":
        #register_user_face(user_dir)
        auto_register_user_face(user_dir)

def auto_register_user_face(user_dir, cap):
    if not cap.isOpened():
        print("[ERROR] Camera is not open")
        return

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    known_encodings = []
    window_name = 'User Registration'

    # --- Window Centering Logic ---
    # Get screen resolution from a temporary Tkinter root
    root = tk.Tk()
    root.withdraw() # Hide the root window
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.destroy()

    # Get video frame dimensions to calculate window size
    ret, frame = cap.read()
    if not ret:
        print("[ERROR] Cannot read from camera for initial setup.")
        return
    h, w, _ = frame.shape

    # Calculate center position
    center_x = int(screen_width/2 - w/2)
    center_y = int(screen_height/2 - h/2)

    cv2.namedWindow(window_name)
    cv2.moveWindow(window_name, center_x, center_y)
    # --- End Centering Logic ---

    print(f"[INFO] Get ready! Image captor will start in {CAPTURE_PREPARATION} seconds...")
    for i in range(CAPTURE_PREPARATION, 0, -1):
        ret, frame = cap.read()
        if ret:
            h, w, _ = frame.shape
            
            # Add the same semi-transparent background as the capture screen
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (w, 80), (0,0,0), -1)
            cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

            # Draw centered text inside the banner
            text = f"Preparando: {i}"
            (text_w, text_h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
            center_x_text = int(w/2 - text_w/2)
            cv2.putText(frame, text, (center_x_text, 55), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
            
            cv2.imshow(window_name, frame)
            cv2.waitKey(1000)

    print("[INFO] Initializing captor. Move your head slowly")
    count_encodings = 0
    last_capture_time = time.time()

    while count_encodings < PICTURE_QT:
        ret, frame = cap.read()
        if not ret:
            break

        h, w, _ = frame.shape
        
        # Face detection using Haar Cascade
        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(grey, scaleFactor=1.2, minNeighbors=5, minSize=(100, 100))

        if len(faces) > 0:
            (x, y, w_face, h_face) = faces[0]
            cv2.rectangle(frame, (x, y), (x+w_face, y+h_face), (255, 0, 0), 2)
        
        # Add semi-transparent background for text
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 80), (0,0,0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

        # Draw centered text
        cv2.putText(frame, "Move your head slowly", (int(w/2) - 250, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        cv2.putText(frame, f"Capturing: {count_encodings + 1}/{PICTURE_QT}", (int(w/2) - 150, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        cv2.putText(frame, f"Enhanced Dataset: {len(known_encodings)} encodings", (int(w/2) - 200, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        cv2.imshow(window_name, frame)

        current_time = time.time()
        if (current_time - last_capture_time) >= CAPTURE_LAPSE:
            if len(faces) > 0:
                # Extract face region for augmentation
                face_region = frame[y:y+h_face, x:x+w_face]
                
                # Apply data augmentation
                augmented_faces = apply_data_augmentation(face_region)
                print(f"[INFO] Generated {len(augmented_faces)} variations for capture {count_encodings + 1}")
                
                # Process each augmented version
                encodings_batch = []
                for idx, aug_face in enumerate(augmented_faces):
                    # Resize to consistent size for better encoding
                    aug_face_resized = cv2.resize(aug_face, (160, 160))
                    rgb_aug_face = cv2.cvtColor(aug_face_resized, cv2.COLOR_BGR2RGB)
                    
                    # Get face locations in the resized image
                    face_locations = face_recognition.face_locations(rgb_aug_face)
                    if face_locations:
                        encodings = face_recognition.face_encodings(rgb_aug_face, face_locations)
                        if encodings:
                            encodings_batch.extend(encodings)
                            if idx == 0:
                                print(f"[INFO] Original encoding {count_encodings + 1} captured")
                            else:
                                print(f"[INFO] Augmented encoding {count_encodings + 1}.{idx} captured")
                
                # Add all successful encodings
                if encodings_batch:
                    known_encodings.extend(encodings_batch)
                    count_encodings += 1
                    last_capture_time = current_time
                    print(f"[INFO] Total encodings so far: {len(known_encodings)}")
                else:
                    print(f"[WARNING] No valid encodings generated for capture {count_encodings + 1}")
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    if count_encodings > 0:
        print(f"\n[SUCCESS] {count_encodings} original captures processed.")
        print(f"[SUCCESS] {len(known_encodings)} total encodings generated (including augmentations).")
        encodings_path = user_dir / "encodings.npy"
        np.save(encodings_path, np.array(known_encodings))
        print(f"[INFO] Enhanced dataset with {len(known_encodings)} encodings saved to {encodings_path}")
        print(f"[INFO] Augmentation factor: {len(known_encodings)/count_encodings:.1f}x improvement")
    else:
        print("\n[ERROR] No encodings were captured. Please try again.")

    if 'frame' in locals() and frame is not None:
        h, w, _ = frame.shape
        final_screen = np.zeros((h, w, 3), dtype="uint8")
        text = "Concluido, retornando ao sistema..."
        (text_w, text_h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
        center_x_text, center_y_text = int(w/2 - text_w/2), int(h/2 - text_h/2)
        cv2.putText(final_screen, text, (center_x_text, center_y_text), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        cv2.imshow(window_name, final_screen)
        cv2.waitKey(2000)

    cv2.destroyAllWindows()