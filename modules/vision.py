import cv2
import threading
import time
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

def _camera_worker():
    """Background mein camera chalata hai"""
    global _current_frame, _is_active
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        console.print("[bold red]❌ Error: Camera open nahi ho raha![/bold red]")
        _is_active = False
        return

    # Window setup (Chota size)
    window_name = "R0uteR Vision [LIVE]"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 320, 240)
    _is_active = True
    
    while not _stop_event.is_set():
        ret, frame = cap.read()
        if ret:
            # 1. Frame ko update karo taaki AI dekh sake
            with _frame_lock:
                _current_frame = frame.copy()
            
            # 2. Live Window dikhao (Video Call style)
            # --- JARVIS HUD (Holographic Overlay) ---
            small_frame = cv2.resize(frame, (320, 240))
            
            # Colors (Hacker Green)
            green = (0, 255, 0)
            cyan = (255, 255, 0)
            
            h, w, _ = small_frame.shape
            cx, cy = w // 2, h // 2
            
            # 1. Central Reticle (Nishana)
            cv2.circle(small_frame, (cx, cy), 30, green, 1)
            cv2.line(small_frame, (cx - 10, cy), (cx + 10, cy), green, 1)
            cv2.line(small_frame, (cx, cy - 10), (cx, cy + 10), green, 1)
            
            # 2. System Info
            cv2.putText(small_frame, "SYS: ONLINE", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, green, 1)
            cv2.putText(small_frame, f"T: {time.strftime('%H:%M:%S')}", (10, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, cyan, 1)
            cv2.rectangle(small_frame, (5, 5), (w-5, h-5), green, 1)
            
            # 3. Dynamic Status (Listening/Speaking)
            cv2.putText(small_frame, f"STATUS: {_hud_status}", (w - 120, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255) if "REC" in _hud_status else cyan, 1)
            
            cv2.imshow(window_name, small_frame)
            
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