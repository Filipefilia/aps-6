import tkinter as tk
from tkinter import font as tkFont
import cv2
from PIL import Image, ImageTk
from controller import recognize_user, register_user
import time
from config.config import REQUIRED_ACCESS_LEVEL

class App:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        # Center the window
        window_width = 800
        window_height = 700
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        center_x = int(screen_width/2 - window_width / 2)
        center_y = int(screen_height/2 - window_height / 2)
        self.window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.window.configure(bg="#2c3e50")

        # --- State Variables ---
        self.is_recognition_running = False
        self.recognized_name = ""
        self.last_seen_time = 0
        self.last_status_update = 0

        # --- Load Known Faces ---
        self.known_face_encodings, self.known_face_names, self.known_face_access_levels = recognize_user.load_known_faces()

        # --- Widgets ---
        self.title_font = tkFont.Font(family="Helvetica", size=18, weight="bold")
        self.button_font = tkFont.Font(family="Helvetica", size=12)
        self.status_font = tkFont.Font(family="Helvetica", size=14, weight="bold")

        self.main_label = tk.Label(window, text="Sistema de Controle de Acesso", font=self.title_font, bg="#2c3e50", fg="#ecf0f1")
        self.main_label.pack(pady=20)

        self.video_canvas = tk.Canvas(window, width=640, height=480, bg="black")
        self.video_canvas.pack()

        self.status_label = tk.Label(window, text="", font=self.status_font, bg="#2c3e50", fg="#ecf0f1")
        self.status_label.pack(pady=10)

        self.btn_frame = tk.Frame(window, bg="#2c3e50")
        self.btn_frame.pack(pady=10)

        # On macOS, buttons with custom background might not render text correctly until clicked.
        # Using highlightbackground with the same color as bg is a common workaround.
        btn_access_bg = "#27ae60"
        btn_register_bg = "#3498db"

        self.btn_access = tk.Button(self.btn_frame, text="Acessar Sistema", command=self.toggle_recognition, font=self.button_font, bg=btn_access_bg, fg="white", relief=tk.FLAT, padx=10, highlightbackground=btn_access_bg)
        self.btn_access.grid(row=0, column=0, padx=10)

        self.btn_register = tk.Button(self.btn_frame, text="Cadastrar Usuário", command=self.open_registration_window, font=self.button_font, bg=btn_register_bg, fg="white", relief=tk.FLAT, padx=10, highlightbackground=btn_register_bg)
        self.btn_register.grid(row=0, column=1, padx=10)

        # --- Camera Setup ---
        self.vid = cv2.VideoCapture(0)

        self.update()
        self.window.mainloop()

    def toggle_recognition(self):
        self.is_recognition_running = not self.is_recognition_running
        if self.is_recognition_running:
            self.btn_access.config(text="Parar Reconhecimento", bg="#c0392b", highlightbackground="#c0392b")
            self.status_label.config(text="Iniciando reconhecimento...", fg="#ecf0f1")
            self.last_status_update = time.time()
        else:
            self.btn_access.config(text="Acessar Sistema", bg="#27ae60", highlightbackground="#27ae60")
            self.status_label.config(text="")

    def open_registration_window(self):
        # Pause recognition
        self.is_recognition_running = False
        self.btn_access.config(text="Acessar Sistema", bg="#27ae60", highlightbackground="#27ae60")

        # Create a new Toplevel window
        self.reg_window = tk.Toplevel(self.window)
        self.reg_window.title("Cadastrar Novo Usuário")

        # Center the registration window
        window_width = 400
        window_height = 250
        screen_width = self.reg_window.winfo_screenwidth()
        screen_height = self.reg_window.winfo_screenheight()
        center_x = int(screen_width/2 - window_width / 2)
        center_y = int(screen_height/2 - window_height / 2)
        self.reg_window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

        self.reg_window.configure(bg="#34495e")

        # Name
        tk.Label(self.reg_window, text="Nome:", font=self.button_font, bg="#34495e", fg="white").pack(pady=(10,0))
        self.name_entry = tk.Entry(self.reg_window, font=self.button_font)
        self.name_entry.pack(pady=5, padx=20, fill=tk.X)

        # Access Level
        tk.Label(self.reg_window, text="Nível de Acesso:", font=self.button_font, bg="#34495e", fg="white").pack()
        self.level_entry = tk.Entry(self.reg_window, font=self.button_font)
        self.level_entry.pack(pady=5, padx=20, fill=tk.X)

        # Submit Button
        btn_submit_bg = "#2980b9"
        submit_btn = tk.Button(self.reg_window, text="Salvar e Iniciar Captura", command=self.submit_registration, font=self.button_font, bg=btn_submit_bg, fg="white", relief=tk.FLAT, highlightbackground=btn_submit_bg)
        submit_btn.pack(pady=20)

        # Make the registration window modal
        self.reg_window.transient(self.window)
        self.reg_window.grab_set()
        self.window.wait_window(self.reg_window)

    def submit_registration(self):
        user_name = self.name_entry.get()
        access_level = self.level_entry.get()

        if not user_name or not access_level:
            # Simple validation
            print("[ERROR] Name and Access Level cannot be empty.")
            return

        # Close the registration form window
        self.reg_window.destroy()

        # 1. Create user folder
        user_dir = register_user.create_new_user(user_name, access_level)

        if user_dir and user_dir != "null":
            # Hide the main window for a better user experience during capture
            self.window.withdraw()
            # 2. Start face capture, passing the existing camera object
            register_user.auto_register_user_face(user_dir, self.vid)
            # Restore the main window
            self.window.deiconify()

            # 3. Reload known faces
            print("[GUI-INFO] Recarregando rostos conhecidos...")
            self.known_face_encodings, self.known_face_names, self.known_face_access_levels = recognize_user.load_known_faces()
            self.status_label.config(text=f"Usuário {user_name} cadastrado!", fg="#3498db")
            self.last_status_update = time.time()
        else:
            print(f"[ERROR] Could not create directory for user {user_name}.")
            self.status_label.config(text=f"Erro ao criar usuário {user_name}", fg="#e74c3c")
            self.last_status_update = time.time()

    def update(self):
        ret, frame = self.vid.read()

        if ret:
            if self.is_recognition_running:
                processed_frame, name, access_level = recognize_user.process_frame_for_recognition(
                    frame, self.known_face_encodings, self.known_face_names, self.known_face_access_levels
                )
                self.update_status(name, access_level)
            else:
                processed_frame = frame

            self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)))
            self.video_canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        
        # Clear status message after a delay
        if time.time() - self.last_status_update > 4:
            if self.is_recognition_running:
                self.status_label.config(text="Procurando...", fg="#ecf0f1")
            else:
                self.status_label.config(text="")

        self.window.after(15, self.update)

    def update_status(self, name, access_level):
        # Prevent flickering: only update if the name changes
        if name == self.recognized_name:
            if name != "Unknown":
                self.last_seen_time = time.time() # Keep updating last seen time for known faces
            return

        self.recognized_name = name
        
        if name != "Unknown":
            self.last_seen_time = time.time()
            try:
                user_level = int(access_level)
                required_level = int(REQUIRED_ACCESS_LEVEL)
                
                access_granted = False
                # Exclusive access logic for level 3
                if required_level == 3:
                    if user_level == 3:
                        access_granted = True
                # Hierarchical logic for other levels
                else:
                    if user_level >= required_level:
                        access_granted = True

                if access_granted:
                    self.status_label.config(text=f"Acesso Garantido: {name} (Nível {user_level})", fg="#2ecc71")
                else:
                    self.status_label.config(text=f"Acesso Negado: Nível Insuficiente", fg="#e74c3c")
                self.last_status_update = time.time()

            except (ValueError, TypeError):
                self.status_label.config(text="Erro: Nível de acesso inválido", fg="#e74c3c")
                self.last_status_update = time.time()
        
        # Only show 'Access Denied' if an unknown face is persistent and no known face was seen recently
        elif name == "Unknown":
            if time.time() - self.last_seen_time > 2:
                 self.status_label.config(text="Acesso Negado", fg="#e74c3c")
                 self.last_status_update = time.time()

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

if __name__ == "__main__":
    App(tk.Tk(), "Controle de Acesso Facial")