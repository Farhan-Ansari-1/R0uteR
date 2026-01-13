import cv2
import threading
import time
import random
import numpy as np
import PIL.Image
import PIL.ImageGrab
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
    
    # Face Detector Load (Standard OpenCV Path)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    if not cap.isOpened():
        console.print("[bold red]❌ Error: Camera open nahi ho raha![/bold red]")
        _is_active = False
        return

    # Window setup (Bada size for JARVIS feel)
    window_name = "R0uteR Vision [JARVIS HUD]"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 640, 480)
    _is_active = True
    
    while not _stop_event.is_set():
        ret, frame = cap.read()
        if ret:
            # 1. Frame ko update karo taaki AI dekh sake
            with _frame_lock:
                _current_frame = frame.copy()
            
            # 2. JARVIS HUD (Holographic Overlay)
            # Resize & Flip (Mirror Effect)
            hud_frame = cv2.resize(frame, (640, 480))
            hud_frame = cv2.flip(hud_frame, 1)
            
            h, w, _ = hud_frame.shape
            cx, cy = w // 2, h // 2
            
            # Colors (BGR Format)
            cyan = (255, 255, 0)   # Cyan
            blue = (255, 100, 0)   # Deep Blue
            white = (255, 255, 255)
            red = (0, 0, 255)
            green = (0, 255, 0)
            
            # --- A. FACE DETECTION (Target Lock) ---
            gray = cv2.cvtColor(hud_frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, fw, fh) in faces:
                # Futuristic Corners
                cv2.line(hud_frame, (x, y), (x + 20, y), cyan, 2)
                cv2.line(hud_frame, (x, y), (x, y + 20), cyan, 2)
                cv2.line(hud_frame, (x + fw, y), (x + fw - 20, y), cyan, 2)
                cv2.line(hud_frame, (x + fw, y), (x + fw, y + 20), cyan, 2)
                cv2.line(hud_frame, (x, y + fh), (x + 20, y + fh), cyan, 2)
                cv2.line(hud_frame, (x, y + fh), (x, y + fh - 20), cyan, 2)
                cv2.line(hud_frame, (x + fw, y + fh), (x + fw - 20, y + fh), cyan, 2)
                cv2.line(hud_frame, (x + fw, y + fh), (x + fw, y + fh - 20), cyan, 2)
                cv2.putText(hud_frame, "IDENTITY: USER", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, cyan, 1)
            
            # --- B. ROTATING ARC REACTOR (Center) ---
            _rotation_angle = (_rotation_angle + 4) % 360
            
            # Outer Ring
            cv2.ellipse(hud_frame, (cx, cy), (50, 50), _rotation_angle, 0, 90, blue, 1)
            cv2.ellipse(hud_frame, (cx, cy), (50, 50), _rotation_angle + 180, 0, 90, blue, 1)
            
            # Inner Ring (Counter Rotate)
            cv2.ellipse(hud_frame, (cx, cy), (35, 35), -_rotation_angle * 2, 0, 60, cyan, 2)
            cv2.ellipse(hud_frame, (cx, cy), (35, 35), -_rotation_angle * 2 + 120, 0, 60, cyan, 2)
            cv2.ellipse(hud_frame, (cx, cy), (35, 35), -_rotation_angle * 2 + 240, 0, 60, cyan, 2)
            
            # Center Dot (Status Indicator)
            status_color = red if "REC" in _hud_status else cyan
            cv2.circle(hud_frame, (cx, cy), 5, status_color, -1)

            # --- C. DATA COLUMNS (Left Side) ---
            y_offset = 100
            for i in range(5):
                val = random.randint(1000, 9999)
                cv2.putText(hud_frame, f"HEX: 0x{val}", (20, y_offset + (i * 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, blue, 1)

            # --- D. SYSTEM STATUS (Top Right) ---
            cv2.putText(hud_frame, f"SYS: {_hud_status}", (w - 200, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
            cv2.putText(hud_frame, f"TIME: {time.strftime('%H:%M:%S')}", (w - 200, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, white, 1)
            
            # --- E. GRID LINES (Subtle) ---
            cv2.line(hud_frame, (0, h//2), (w, h//2), (0, 50, 0), 1)
            cv2.line(hud_frame, (w//2, 0), (w//2, h), (0, 50, 0), 1)
            
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