import cv2
import threading
import time
import random
import numpy as np
import PIL.Image
import PIL.ImageGrab
import psutil
from modules.ui import console

# Global Variables
_camera_thread = None
_stop_event = threading.Event()
_current_frame = None
_frame_lock = threading.Lock()
_is_active = False
_hud_status = "STANDBY" # Ye screen pe likha aayega
_rotation_angle = 0 # Animation ke liye

def _camera_worker():
    """Background mein camera chalata hai"""
    global _current_frame, _is_active, _rotation_angle
    cap = cv2.VideoCapture(0)
    
    # 1. HD Resolution Set karo (Taaki face clear dikhe)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # Face Detector Load (Standard OpenCV Path)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    if not cap.isOpened():
        console.print("[bold red]❌ Error: Camera open nahi ho raha![/bold red]")
        _is_active = False
        return

    # Window setup (Bada size for JARVIS feel)
    window_name = "R0uteR Vision [JARVIS HUD]"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1024, 576) # 16:9 Aspect Ratio
    _is_active = True
    
    while not _stop_event.is_set():
        ret, frame = cap.read()
        if ret:
            # 1. Frame ko update karo taaki AI dekh sake
            with _frame_lock:
                _current_frame = frame.copy()
            
            # 2. JARVIS HUD (Holographic Overlay)
            # Flip (Mirror Effect) - No Resize (Full Quality)
            hud_frame = cv2.flip(frame, 1)
            
            h, w, _ = hud_frame.shape
            cx, cy = w // 2, h // 2
            
            # Colors (BGR Format)
            cyan = (255, 255, 0)   # Cyan
            blue = (255, 100, 0)   # Deep Blue
            white = (255, 255, 255)
            red = (0, 0, 255)
            green = (0, 255, 0)
            grey = (50, 50, 50)
            
            # --- A. FACE DETECTION (Target Lock) ---
            gray = cv2.cvtColor(hud_frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, fw, fh) in faces:
                # Futuristic Corners
                l = 30 # Line length
                t = 2  # Thickness
                # Top-Left
                cv2.line(hud_frame, (x, y), (x + l, y), cyan, t, cv2.LINE_AA)
                cv2.line(hud_frame, (x, y), (x, y + l), cyan, t, cv2.LINE_AA)
                # Top-Right
                cv2.line(hud_frame, (x + fw, y), (x + fw - l, y), cyan, t, cv2.LINE_AA)
                cv2.line(hud_frame, (x + fw, y), (x + fw, y + l), cyan, t, cv2.LINE_AA)
                # Bottom-Left
                cv2.line(hud_frame, (x, y + fh), (x + l, y + fh), cyan, t, cv2.LINE_AA)
                cv2.line(hud_frame, (x, y + fh), (x, y + fh - l), cyan, t, cv2.LINE_AA)
                # Bottom-Right
                cv2.line(hud_frame, (x + fw, y + fh), (x + fw - l, y + fh), cyan, t, cv2.LINE_AA)
                cv2.line(hud_frame, (x + fw, y + fh), (x + fw, y + fh - l), cyan, t, cv2.LINE_AA)
                
                cv2.putText(hud_frame, "TARGET: USER", (x, y - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, cyan, 1, cv2.LINE_AA)
                cv2.putText(hud_frame, "CONFIDENCE: 99%", (x, y + fh + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, green, 1, cv2.LINE_AA)
            
            # --- B. ROTATING ARC REACTOR (Center) ---
            _rotation_angle = (_rotation_angle + 4) % 360
            
            # Outer Ring
            cv2.ellipse(hud_frame, (cx, cy), (60, 60), _rotation_angle, 0, 90, blue, 1, cv2.LINE_AA)
            cv2.ellipse(hud_frame, (cx, cy), (60, 60), _rotation_angle + 180, 0, 90, blue, 1, cv2.LINE_AA)
            
            # Inner Ring (Counter Rotate)
            cv2.ellipse(hud_frame, (cx, cy), (40, 40), -_rotation_angle * 2, 0, 60, cyan, 1, cv2.LINE_AA)
            cv2.ellipse(hud_frame, (cx, cy), (40, 40), -_rotation_angle * 2 + 120, 0, 60, cyan, 1, cv2.LINE_AA)
            cv2.ellipse(hud_frame, (cx, cy), (40, 40), -_rotation_angle * 2 + 240, 0, 60, cyan, 1, cv2.LINE_AA)
            
            # Center Dot (Status Indicator)
            status_color = red if "REC" in _hud_status else cyan
            cv2.circle(hud_frame, (cx, cy), 3, status_color, -1, cv2.LINE_AA)

            # --- C. REAL SYSTEM STATS (Left Side) ---
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            
            # CPU Bar
            cv2.putText(hud_frame, f"CPU: {cpu}%", (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, cyan, 1, cv2.LINE_AA)
            cv2.rectangle(hud_frame, (30, 110), (30 + int(cpu * 1.5), 120), blue, -1)
            cv2.rectangle(hud_frame, (30, 110), (30 + 150, 120), cyan, 1)
            
            # RAM Bar
            cv2.putText(hud_frame, f"RAM: {ram}%", (30, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.5, cyan, 1, cv2.LINE_AA)
            cv2.rectangle(hud_frame, (30, 150), (30 + int(ram * 1.5), 160), blue, -1)
            cv2.rectangle(hud_frame, (30, 150), (30 + 150, 160), cyan, 1)
            
            # Battery (Agar laptop hai)
            battery = psutil.sensors_battery()
            if battery:
                bat_percent = battery.percent
                plugged = " [CHG]" if battery.power_plugged else ""
                cv2.putText(hud_frame, f"PWR: {bat_percent}%{plugged}", (30, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.5, green if bat_percent > 20 else red, 1, cv2.LINE_AA)

            # --- D. SYSTEM STATUS (Top Right) ---
            cv2.putText(hud_frame, f"SYS: {_hud_status}", (w - 250, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2, cv2.LINE_AA)
            cv2.putText(hud_frame, f"TIME: {time.strftime('%H:%M:%S')}", (w - 250, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, white, 1, cv2.LINE_AA)
            cv2.putText(hud_frame, f"DATE: {time.strftime('%Y-%m-%d')}", (w - 250, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.5, white, 1, cv2.LINE_AA)
            
            # --- E. GRID LINES (Subtle) ---
            # Horizontal
            cv2.line(hud_frame, (0, h//3), (w, h//3), grey, 1)
            cv2.line(hud_frame, (0, 2*h//3), (w, 2*h//3), grey, 1)
            # Vertical
            cv2.line(hud_frame, (w//3, 0), (w//3, h), grey, 1)
            cv2.line(hud_frame, (2*w//3, 0), (2*w//3, h), grey, 1)
            
            # Crosshair (Center)
            cv2.line(hud_frame, (cx - 20, cy), (cx + 20, cy), cyan, 1)
            cv2.line(hud_frame, (cx, cy - 20), (cx, cy + 20), cyan, 1)
            
            cv2.imshow(window_name, hud_frame)
            
            # 'q' dabane se window band ho sakti hai
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            time.sleep(0.1)
            
    cap.release()
    cv2.destroyAllWindows()
    _is_active = False

def start_camera():
    """Camera ko background mein start karta hai"""
    global _camera_thread
    if _is_active:
        console.print("[yellow]⚠️ Camera pehle se ON hai.[/yellow]")
        return

    _stop_event.clear()
    _camera_thread = threading.Thread(target=_camera_worker, daemon=True)
    _camera_thread.start()
    console.print("[green]👁️ Vision System: ONLINE[/green]")

def stop_camera():
    """Camera band karta hai"""
    global _camera_thread
    if not _is_active:
        console.print("[yellow]⚠️ Camera pehle se OFF hai.[/yellow]")
        return
        
    _stop_event.set()
    if _camera_thread:
        _camera_thread.join(timeout=2)
    console.print("[red]👁️ Vision System: OFFLINE[/red]")

def set_vision_status(status_text):
    """HUD pe status update karta hai"""
    global _hud_status
    _hud_status = status_text

def get_vision_context():
    """AI ke liye latest frame return karta hai"""
    global _current_frame
    if not _is_active:
        return None
        
    with _frame_lock:
        if _current_frame is not None:
            # OpenCV (BGR) se PIL (RGB) convert karo
            color_converted = cv2.cvtColor(_current_frame, cv2.COLOR_BGR2RGB)
            return PIL.Image.fromarray(color_converted)
    return None

def get_screen_context():
    """Screen ka screenshot leta hai"""
    return PIL.ImageGrab.grab()