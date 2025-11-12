import tkinter as tk
from tkinter import font as tkFont
import cv2
from PIL import Image, ImageTk
from controller import recognize_user, register_user
import time
import random
from config.config import REQUIRED_ACCESS_LEVEL

class App:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        # Center the window
        window_width = 800
        window_height = 750
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        center_x = int(screen_width/2 - window_width / 2)
        center_y = int(screen_height/2 - window_height / 2)
        self.window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.window.configure(bg="#2c3e50")

        # --- State Variables ---
        self.is_recognition_running = False
        self.is_camera_active = False
        self.recognized_name = ""
        self.last_seen_time = 0
        
        # --- Liveness Detection Variables ---
        self.ear_history = []
        self.mar_history = []
        self.blink_counter = 0
        self.smile_counter = 0
        self.smile_detected = False
        self.liveness_verified = False
        self.recognition_start_time = 0
        
        # Enhanced liveness validation
        self.liveness_phase = 0  # 0: face detection, 1: challenge phase, 2: completed
        self.current_challenge = None  # "blink" or "smile"
        self.challenge_start_time = 0
        self.challenges_completed = 0
        self.challenge_sequence = []  # List of challenges to complete
        self.current_challenge_index = 0
        self.challenge_timeout = 8  # seconds per challenge (more time for robust detection)
        
        # Security requirements (streamlined approach)
        self.min_challenges = 2  # Minimum number of challenges  
        self.max_challenges = 3  # Maximum number of challenges
        self.blink_required = True  # At least one blink is mandatory
        
        # Thresholds for liveness detection (balanced for reliability)
        self.EAR_THRESHOLD = 0.21  # More strict threshold for enhanced anti-spoofing
        self.MAR_THRESHOLD = 0.38  # Slightly more sensitive to compensate for resolution reduction  
        self.BLINK_FRAMES = 8  # Enhanced frames for robust blink detection with velocity
        self.SMILE_FRAMES = 4  # Sustained smile detection (more responsive)
        self.HISTORY_SIZE = 30
        self.RECOGNITION_TIMEOUT = 20  # Total time for all challenges

        # --- Load Known Faces ---
        self.known_face_encodings, self.known_face_names, self.known_face_access_levels = recognize_user.load_known_faces()

        # --- Widgets ---
        self.title_font = tkFont.Font(family="Helvetica", size=18, weight="bold")
        self.button_font = tkFont.Font(family="Helvetica", size=12)
        self.status_font = tkFont.Font(family="Helvetica", size=14, weight="bold")
        self.info_font = tkFont.Font(family="Helvetica", size=10)
        self.result_font = tkFont.Font(family="Helvetica", size=24, weight="bold")

        self.main_label = tk.Label(window, text="Sistema de Controle de Acesso", font=self.title_font, bg="#2c3e50", fg="#ecf0f1")
        self.main_label.pack(pady=20)

        self.video_canvas = tk.Canvas(window, width=640, height=480, bg="black")
        self.video_canvas.pack()

        # --- Status and Liveness Info Frame ---
        self.info_frame = tk.Frame(window, bg="#2c3e50")
        self.info_frame.pack(pady=10, fill=tk.X)

        self.status_label = tk.Label(self.info_frame, text="", font=self.status_font, bg="#2c3e50", fg="#ecf0f1")
        self.status_label.pack()

        # Liveness indicators
        self.liveness_frame = tk.Frame(self.info_frame, bg="#2c3e50")
        self.liveness_frame.pack(pady=5)

        self.ear_label = tk.Label(self.liveness_frame, text="EAR: --", font=self.info_font, bg="#2c3e50", fg="#bdc3c7")
        self.ear_label.grid(row=0, column=0, padx=10)

        self.mar_label = tk.Label(self.liveness_frame, text="MAR: --", font=self.info_font, bg="#2c3e50", fg="#bdc3c7")
        self.mar_label.grid(row=0, column=1, padx=10)

        self.blink_label = tk.Label(self.liveness_frame, text="Piscadas: 0", font=self.info_font, bg="#2c3e50", fg="#bdc3c7")
        self.blink_label.grid(row=0, column=2, padx=10)

        self.smile_label = tk.Label(self.liveness_frame, text="Sorrisos: 0", font=self.info_font, bg="#2c3e50", fg="#bdc3c7")
        self.smile_label.grid(row=0, column=3, padx=10)

        self.liveness_status = tk.Label(self.liveness_frame, text="Vivacidade: ⚪", font=self.info_font, bg="#2c3e50", fg="#bdc3c7")
        self.liveness_status.grid(row=0, column=4, padx=10)

        # Challenge indicator
        self.challenge_label = tk.Label(self.liveness_frame, text="", font=self.info_font, bg="#2c3e50", fg="#e67e22")
        self.challenge_label.grid(row=1, column=0, columnspan=3, padx=10, pady=5)

        # Timeout indicator
        self.timeout_label = tk.Label(self.liveness_frame, text="", font=self.info_font, bg="#2c3e50", fg="#f39c12")
        self.timeout_label.grid(row=1, column=4, padx=10)

        self.btn_frame = tk.Frame(window, bg="#2c3e50")
        self.btn_frame.pack(pady=10)

        self.btn_access = tk.Button(self.btn_frame, text="Iniciar Reconhecimento", command=self.start_recognition, font=self.button_font, bg="#27ae60", fg="white", relief=tk.FLAT, padx=10)
        self.btn_access.grid(row=0, column=0, padx=10)

        self.btn_register = tk.Button(self.btn_frame, text="Cadastrar Usuário", command=self.open_registration_window, font=self.button_font, bg="#3498db", fg="white", relief=tk.FLAT, padx=10)
        self.btn_register.grid(row=0, column=1, padx=10)

        self.btn_reset = tk.Button(self.btn_frame, text="Nova Tentativa", command=self.reset_system, font=self.button_font, bg="#f39c12", fg="white", relief=tk.FLAT, padx=10)
        self.btn_reset.grid(row=0, column=2, padx=10)

        # --- Camera Setup ---
        self.vid = None

        # Start with camera off
        self.show_standby_screen()
        self.update()
        self.window.mainloop()

    def start_camera(self):
        """Initialize and start the camera"""
        if self.vid is None or not self.vid.isOpened():
            self.vid = cv2.VideoCapture(2)
            if not self.vid.isOpened():
                self.show_error_screen("Erro: Não foi possível acessar a câmera")
                return False
        self.is_camera_active = True
        return True

    def stop_camera(self):
        """Stop and release the camera"""
        if self.vid is not None and self.vid.isOpened():
            self.vid.release()
        self.is_camera_active = False

    def show_standby_screen(self):
        """Show standby screen when camera is off"""
        standby_img = self.create_text_image("Sistema Pronto\n\nClique em 'Iniciar Reconhecimento'\npara começar", "#34495e", "#ecf0f1")
        self.video_canvas.create_image(320, 240, image=standby_img)
        self.video_canvas.image = standby_img

    def show_result_screen(self, access_granted, user_name, access_level):
        """Show final result screen after recognition"""
        if access_granted:
            message = f"✅ ACESSO CONCEDIDO\n\nBem-vindo, {user_name}!\nNível de Acesso: {access_level}"
            bg_color = "#2ecc71"
        else:
            if user_name != "Unknown":
                message = f"❌ ACESSO NEGADO\n\nUsuário: {user_name}\nNível Insuficiente"
            else:
                message = "❌ ACESSO NEGADO\n\nPessoa não reconhecida"
            bg_color = "#e74c3c"
        
        result_img = self.create_text_image(message, bg_color, "white")
        self.video_canvas.create_image(320, 240, image=result_img)
        self.video_canvas.image = result_img

    def show_timeout_screen(self):
        """Show timeout screen"""
        timeout_img = self.create_text_image("⏰ TEMPO ESGOTADO\n\nTentativa de reconhecimento\nexcedeu o limite de tempo\n\nClique em 'Nova Tentativa'", "#f39c12", "white")
        self.video_canvas.create_image(320, 240, image=timeout_img)
        self.video_canvas.image = timeout_img

    def show_error_screen(self, message):
        """Show error screen"""
        error_img = self.create_text_image(f"❌ ERRO\n\n{message}", "#e74c3c", "white")
        self.video_canvas.create_image(320, 240, image=error_img)
        self.video_canvas.image = error_img

    def create_text_image(self, text, bg_color, text_color):
        """Create an image with text for display on canvas"""
        from PIL import Image, ImageDraw, ImageFont
        
        img = Image.new('RGB', (640, 480), bg_color)
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        # Calculate text position for centering
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (640 - text_width) // 2
        y = (480 - text_height) // 2
        
        draw.multiline_text((x, y), text, font=font, fill=text_color, align='center')
        
        return ImageTk.PhotoImage(img)

    def start_recognition(self):
        """Start the recognition process"""
        if not self.start_camera():
            return
        
        self.is_recognition_running = True
        self.recognition_start_time = time.time()
        self.reset_liveness()
        
        self.btn_access.config(text="Reconhecendo...", bg="#c0392b", state="disabled")
        self.btn_register.config(state="disabled")
        self.status_label.config(text="Posicione-se em frente à câmera", fg="#f39c12")

    def reset_system(self):
        """Reset the entire system to standby"""
        self.stop_camera()
        self.is_recognition_running = False
        self.reset_liveness()
        
        self.btn_access.config(text="Iniciar Reconhecimento", bg="#27ae60", state="normal")
        self.btn_register.config(state="normal")
        self.status_label.config(text="", fg="#ecf0f1")
        self.timeout_label.config(text="")
        self.challenge_label.config(text="")
        
        self.show_standby_screen()

    def reset_liveness(self):
        """Reset liveness detection counters"""
        self.ear_history = []
        self.mar_history = []
        self.blink_counter = 0
        self.smile_counter = 0
        self.smile_detected = False
        self.liveness_verified = False
        self.liveness_phase = 0
        self.current_challenge = None
        self.challenge_start_time = 0
        self.challenges_completed = 0
        self.challenge_sequence = []
        self.current_challenge_index = 0
        self.generate_challenge_sequence()
        self.update_liveness_display(0.0, 0.0)

    def generate_challenge_sequence(self):
        """Generate a simple, effective challenge sequence"""
        # Simple approach: always alternate between blink and smile
        sequences = [
            ["blink"],                    # Just one blink (fastest)
            ["smile"],                    # Just one smile  
            ["blink", "smile"],          # Blink then smile
            ["smile", "blink"],          # Smile then blink
        ]
        
        # Choose random sequence
        self.challenge_sequence = random.choice(sequences)
        self.current_challenge_index = 0
        
        print(f"[DEBUG] Generated simple challenge sequence: {self.challenge_sequence}")

    def detect_liveness(self, ear, mar, user_name):
        """Enhanced liveness detection with random challenges"""
        self.ear_history.append(ear)
        self.mar_history.append(mar)
        
        # Keep sufficient history for enhanced blink detection
        if len(self.ear_history) > 25:
            self.ear_history.pop(0)
        if len(self.mar_history) > 25:
            self.mar_history.pop(0)

        current_time = time.time()

        # Phase 0: Initial face detection phase
        if self.liveness_phase == 0:
            self.liveness_phase = 1
            self.start_next_challenge()
            return False

        # Phase 1: Challenge phase
        elif self.liveness_phase == 1:
            # Check challenge timeout
            if current_time - self.challenge_start_time > self.challenge_timeout:
                # Challenge failed - restart entire sequence
                print("[DEBUG] Challenge timeout - restarting sequence")
                self.reset_challenge_counters()
                self.generate_challenge_sequence()
                self.start_next_challenge()
                return False

            # Check if current challenge is completed
            challenge_completed = False
            
            if self.current_challenge == "blink":
                challenge_completed = self.detect_blink_pattern()
            elif self.current_challenge == "smile":
                challenge_completed = self.detect_smile_pattern()

            if challenge_completed:
                self.challenges_completed += 1
                self.current_challenge_index += 1
                
                if self.current_challenge_index >= len(self.challenge_sequence):
                    # All challenges in sequence completed successfully
                    self.liveness_phase = 2
                    self.liveness_verified = True
                    self.challenge_label.config(text="✅ Validação de vivacidade completa!", fg="#2ecc71")
                    return True
                else:
                    # Start next challenge in sequence
                    self.reset_current_challenge_counters()
                    self.start_next_challenge()
                    return False

        return self.liveness_verified

    def start_next_challenge(self):
        """Start the next challenge in the sequence"""
        if self.current_challenge_index < len(self.challenge_sequence):
            self.current_challenge = self.challenge_sequence[self.current_challenge_index]
            self.challenge_start_time = time.time()
            
            progress = f"({self.current_challenge_index + 1}/{len(self.challenge_sequence)})"
            
            if self.current_challenge == "blink":
                self.challenge_label.config(text=f"👁️ Pisque uma vez {progress}", fg="#3498db")
            elif self.current_challenge == "smile":
                self.challenge_label.config(text=f"😊 Sorria por um momento {progress}", fg="#3498db")
                
            print(f"[DEBUG] Started challenge {self.current_challenge_index + 1}/{len(self.challenge_sequence)}: {self.current_challenge}")

    def reset_challenge_counters(self):
        """Reset counters for all challenges"""
        self.blink_counter = 0
        self.smile_counter = 0
        self.challenges_completed = 0
        self.current_challenge_index = 0

    def reset_current_challenge_counters(self):
        """Reset counters for the current challenge only"""
        # No need to reset individual counters since we only need one action
        pass

    def detect_blink_pattern(self):
        """Detect single blink with enhanced anti-spoofing - critical for security"""
        if len(self.ear_history) >= 5:  # Need more frames for robust detection
            current_ear = self.ear_history[-1]
            
            # Debug every 10 frames during blink challenge
            if len(self.ear_history) % 10 == 0:
                print(f"[DEBUG] Blink challenge - Current EAR: {current_ear:.3f}, Threshold: {self.EAR_THRESHOLD}")
                print(f"[DEBUG] Recent EARs: {[round(ear, 3) for ear in self.ear_history[-8:]]}")
            
            # Enhanced blink detection - look for complete blink cycle with velocity
            # Pattern: stable_open -> rapid_close -> stable_closed -> rapid_open -> stable_open
            
            # Check if we have enough history to detect a complete blink
            if len(self.ear_history) >= 8:
                # Look for blink pattern in recent frames
                for i in range(len(self.ear_history) - 7, max(0, len(self.ear_history) - 15), -1):
                    if i < 0:
                        continue
                    
                    window = self.ear_history[i:i+8]
                    if len(window) < 8:
                        continue
                    
                    # Enhanced pattern detection
                    open_start = window[0] > self.EAR_THRESHOLD and window[1] > self.EAR_THRESHOLD
                    close_middle = (window[2] < self.EAR_THRESHOLD or window[3] < self.EAR_THRESHOLD or 
                                  window[4] < self.EAR_THRESHOLD or window[5] < self.EAR_THRESHOLD)
                    open_end = window[6] > self.EAR_THRESHOLD and window[7] > self.EAR_THRESHOLD
                    
                    # Check for velocity - rapid change indicates real blink
                    closing_speed = abs(window[1] - window[3])  # Speed of closing
                    opening_speed = abs(window[5] - window[7])  # Speed of opening
                    
                    # Minimum velocity threshold to detect movement (anti-photo spoofing)
                    min_velocity = 0.08
                    
                    if (open_start and close_middle and open_end and 
                        closing_speed > min_velocity and opening_speed > min_velocity):
                        
                        # Additional check: ensure we had sustained closure
                        closed_frames = sum(1 for ear in window[2:6] if ear < self.EAR_THRESHOLD)
                        
                        if closed_frames >= 2:  # At least 2 frames with eyes closed
                            print(f"[DEBUG] Enhanced blink detected! Pattern: {[round(ear, 3) for ear in window]}")
                            print(f"[DEBUG] Closing speed: {closing_speed:.3f}, Opening speed: {opening_speed:.3f}")
                            print(f"[DEBUG] Closed frames: {closed_frames}")
                            return True
        
        return False

    def detect_smile_pattern(self):
        """Detect single smile - sustained for a few frames"""
        if len(self.mar_history) >= self.SMILE_FRAMES:
            recent_mars = self.mar_history[-self.SMILE_FRAMES:]
            current_mar = self.mar_history[-1]
            
            # Debug during smile challenge (balanced frequency)
            if len(self.mar_history) % 10 == 0:
                print(f"[DEBUG] Smile challenge - Current MAR: {current_mar:.3f}, Threshold: {self.MAR_THRESHOLD}")
            
            # Just need sustained smile for a few frames
            if all(mar > self.MAR_THRESHOLD for mar in recent_mars):
                print(f"[DEBUG] Smile pattern detected! MARs: {[round(mar, 3) for mar in recent_mars]}")
                print(f"[DEBUG] Smile challenge completed!")
                return True
        return False

    def update_liveness_display(self, ear, mar):
        """Update the liveness indicators in the GUI"""
        self.ear_label.config(text=f"EAR: {ear:.3f}")
        self.mar_label.config(text=f"MAR: {mar:.3f}")
        
        # Hide individual counters - not needed for single action approach
        self.blink_label.config(text="")
        self.smile_label.config(text="")
        
        if self.liveness_verified:
            self.liveness_status.config(text="Vivacidade: ✅", fg="#2ecc71")
        elif len(self.challenge_sequence) > 0 and self.challenges_completed > 0:
            self.liveness_status.config(text=f"Progresso: {self.challenges_completed}/{len(self.challenge_sequence)}", fg="#f39c12")
        else:
            self.liveness_status.config(text="Vivacidade: ⚪", fg="#bdc3c7")

    def check_access_permission(self, user_level):
        """Check if user has permission to access"""
        try:
            user_level = int(user_level)
            required_level = int(REQUIRED_ACCESS_LEVEL)
            
            # Lógica de acesso exclusivo para o nível 3
            if required_level == 3:
                return user_level == 3
            # Lógica hierárquica para os outros níveis
            else:
                return user_level >= required_level
        except (ValueError, TypeError):
            return False

    def complete_recognition(self, name, access_level, access_granted):
        """Complete the recognition process and show results"""
        self.stop_camera()
        self.is_recognition_running = False
        
        self.btn_access.config(text="Iniciar Reconhecimento", bg="#27ae60", state="normal")
        self.btn_register.config(state="normal")
        
        self.show_result_screen(access_granted, name, access_level)
        
        # Reset liveness display
        self.update_liveness_display(0.0, 0.0)
        self.timeout_label.config(text="")
        self.challenge_label.config(text="")

    def open_registration_window(self):
        """Open registration window"""
        # Stop any ongoing recognition
        self.reset_system()

        self.reg_window = tk.Toplevel(self.window)
        self.reg_window.title("Cadastrar Novo Usuário")

        window_width = 400
        window_height = 250
        screen_width = self.reg_window.winfo_screenwidth()
        screen_height = self.reg_window.winfo_screenheight()
        center_x = int(screen_width/2 - window_width / 2)
        center_y = int(screen_height/2 - window_height / 2)
        self.reg_window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.reg_window.configure(bg="#34495e")

        tk.Label(self.reg_window, text="Nome:", font=self.button_font, bg="#34495e", fg="white").pack(pady=(10,0))
        self.name_entry = tk.Entry(self.reg_window, font=self.button_font)
        self.name_entry.pack(pady=5, padx=20, fill=tk.X)

        tk.Label(self.reg_window, text="Nível de Acesso:", font=self.button_font, bg="#34495e", fg="white").pack()
        self.level_entry = tk.Entry(self.reg_window, font=self.button_font)
        self.level_entry.pack(pady=5, padx=20, fill=tk.X)

        submit_btn = tk.Button(self.reg_window, text="Salvar e Iniciar Captura", command=self.submit_registration, font=self.button_font, bg="#2980b9", fg="white", relief=tk.FLAT)
        submit_btn.pack(pady=20)

        self.reg_window.transient(self.window)
        self.reg_window.grab_set()
        self.window.wait_window(self.reg_window)

    def submit_registration(self):
        """Submit registration form"""
        user_name = self.name_entry.get()
        access_level = self.level_entry.get()

        if not user_name or not access_level:
            print("[ERROR] Name and Access Level cannot be empty.")
            return

        self.reg_window.destroy()

        user_dir = register_user.create_new_user(user_name, access_level)

        if user_dir and user_dir != "null":
            self.window.withdraw()
            if not self.start_camera():
                self.window.deiconify()
                return
            
            register_user.auto_register_user_face(user_dir, self.vid)
            self.stop_camera()
            self.window.deiconify()

            print("[GUI-INFO] Recarregando rostos conhecidos...")
            self.known_face_encodings, self.known_face_names, self.known_face_access_levels = recognize_user.load_known_faces()
            self.status_label.config(text=f"Usuário {user_name} cadastrado com sucesso!", fg="#3498db")
        else:
            print(f"[ERROR] Could not create directory for user {user_name}.")
            self.status_label.config(text=f"Erro ao criar usuário {user_name}", fg="#e74c3c")

    def update(self):
        """Main update loop"""
        if self.is_camera_active and self.vid is not None:
            ret, frame = self.vid.read()

            if ret and self.is_recognition_running:
                # Check for timeout
                elapsed_time = time.time() - self.recognition_start_time
                remaining_time = self.RECOGNITION_TIMEOUT - elapsed_time
                
                if remaining_time <= 0:
                    self.timeout_label.config(text="")
                    self.complete_recognition("Unknown", "", False)
                    self.show_timeout_screen()
                    self.window.after(15, self.update)
                    return
                else:
                    self.timeout_label.config(text=f"⏱️ {int(remaining_time)}s")
                
                # Process frame for recognition - balanced optimization
                processed_frame, name, access_level, ear, mar = recognize_user.process_frame_for_recognition(
                    frame, self.known_face_encodings, self.known_face_names, self.known_face_access_levels, draw_annotations=False
                )
                
                if name != "Unknown":
                    liveness_ok = self.detect_liveness(ear, mar, name)
                    self.update_liveness_display(ear, mar)
                    
                    if liveness_ok:
                        access_granted = self.check_access_permission(access_level)
                        self.complete_recognition(name, access_level, access_granted)
                        self.window.after(15, self.update)
                        return
                    else:
                        # Don't show the user's name during liveness validation
                        if self.liveness_phase == 1:
                            remaining_time = self.challenge_timeout - (time.time() - self.challenge_start_time)
                            if remaining_time > 0:
                                self.status_label.config(text=f"Complete o desafio - {int(remaining_time)}s restante", fg="#f39c12")
                            else:
                                self.status_label.config(text="Tempo esgotado - novo desafio", fg="#e74c3c")
                        else:
                            self.status_label.config(text="Pessoa reconhecida - Validando vivacidade...", fg="#f39c12")
                else:
                    self.update_liveness_display(0.0, 0.0)
                    self.status_label.config(text="Posicione-se em frente à câmera", fg="#f39c12")
                    self.challenge_label.config(text="")

                # Always display the original clean frame (without identification boxes)
                self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
                self.video_canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        
        self.window.after(15, self.update)

    def __del__(self):
        """Cleanup"""
        self.stop_camera()

if __name__ == "__main__":
    App(tk.Tk(), "Controle de Acesso Facial")
