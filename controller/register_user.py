import cv2
import os
from config.config import DATASET_DIR

# constant setups
PICTURE_QT = 20
MIN_WIDHT = 100
MIN_HEIGHT = 100

# user dir setup
def create_new_user(user_name, access_level):
    folder_name = f"access_level{access_level}-{user_name}"
    user_dir = os.path.join(DATASET_DIR, folder_name)

    os.makedirs(user_dir)

    if not os.path.exists(user_dir):
        print("[ERROR] Could not create folder")
        return "null"
    
    print(f"[INFO] Folder created in path: {user_dir}")

    return user_dir

def register_user_face(user_dir):
    cap = cv2.VideoCapture(0)

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
        register_user_face(user_dir)    
