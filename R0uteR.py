#!/usr/bin/env python3
import warnings
warnings.filterwarnings("ignore")  # Faaltu ke warnings ko chup karao

import os
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
import time
import functools

from modules.brain import init_brain
from modules.audio import speak
from modules.automation import (
    execute_command, automate_typing, automate_keypress, 
    send_whatsapp_message, switch_window, copy_to_clipboard, 
    paste_from_clipboard, open_website, close_window, read_file_content, list_directory_files
)
from modules.memory import init_db, save_interaction, load_history, clear_history
from modules.listen import listen
from modules.vision import start_camera, stop_camera, get_vision_context, get_screen_context, set_vision_status
from modules.web import perform_search

console = Console()

# 0. Tool Wrapper for Logging (Live Visibility)
def log_tool_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        params = ", ".join([repr(a) for a in args] + [f"{k}={repr(v)}" for k, v in kwargs.items()])
        console.print(Panel(f"[bold blue]🔧 Tool Triggered:[/bold blue] [green]{func.__name__}[/green]\n[dim]Input: {params}[/dim]", border_style="blue"))
        return func(*args, **kwargs)
    return wrapper

# 1. Tool List Configuration
tools_list = [log_tool_call(f) for f in [
    execute_command, automate_typing, automate_keypress, 
    send_whatsapp_message, switch_window, close_window, 
    open_website, copy_to_clipboard, paste_from_clipboard,
    perform_search, read_file_content, list_directory_files
]]

def main():
    # 1. Init System
    init_db()
    old_chat = load_history(limit=50)
    chat_session = init_brain(history_data=old_chat, tools=tools_list)
    
    # 1.5 Console Setup (App feel dene ke liye)
    os.system("title R0uteR Console - Neural Link")
    os.system("mode con: cols=100 lines=35") # Window size fix (Windows Only)

    # 2. Start Camera immediately (Jaisa tune bola: Hamesha Open)
    start_camera()
    
    console.clear()
    console.print(Panel(Align.center("[bold green]👾 R0uteR AI - Neural Link Active[/bold green]"), border_style="green"))
    console.print("[dim cyan]👁️  JARVIS HUD Protocol: Loaded.[/dim cyan]")

    # --- ALWAYS ON MODE ---
    console.print("[bold green]🟢 System Online. Listening continuously...[/bold green]")
    console.print("[dim](Spacebar daba kar chup kara sakte ho)[/dim]")
    speak("System Online")
    
    IS_AWAKE = True
    SILENCE_COUNT = 0

    while True:
        try:
            user_input = None
            
            # --- 1. PASSIVE MODE (Wake Word Detection) ---
            if not IS_AWAKE:
                set_vision_status("STANDBY")
                # Chupchap suno (3 sec clips)
                user_input = listen(duration=3, quiet=True)
                
                if user_input and ("router" in user_input.lower() or "hey" in user_input.lower()):
                    IS_AWAKE = True
                    SILENCE_COUNT = 0
                    speak("I am online.")
                    set_vision_status("LISTENING")
                continue # Wapas loop mein jao (Active mode mein aane ke liye)

            # --- 2. ACTIVE MODE (Conversation) ---
            else:
                set_vision_status("LISTENING...") # HUD Update
                with console.status("[bold cyan]🎤 Listening... (Bol bhai)[/bold cyan]", spinner="dots12") as status:
                    try:
                        user_input = listen(duration=20, quiet=False) # Increased duration for longer commands
                    except KeyboardInterrupt:
                        status.update("[yellow]✋ Stopped.[/yellow]")
                        pass
            
            if not user_input:
                # Agar kuch nahi bola, to silence count badhao
                SILENCE_COUNT += 1
                if SILENCE_COUNT > 2: # Approx 15 sec silence
                    IS_AWAKE = False
                    speak("Going offline.")
                    set_vision_status("STANDBY")
                continue
            
            # Agar user ne kuch bola, to silence reset karo
            SILENCE_COUNT = 0

            # Sleep Logic (Agar break lena ho)
            if "sleep" in user_input.lower() or "so ja" in user_input.lower():
                set_vision_status("SLEEPING")
                speak("Going to sleep mode. Press Enter to wake me up.")
                console.input("\n[bold yellow]💤 System Sleeping. Press Enter to Wake Up...[/bold yellow]")
                console.print("[bold green]🟢 System Online.[/bold green]")
                IS_AWAKE = True # Uthne ke baad active raho
                speak("I am back.")
                continue

            # Exit Logic
            # "band ho ja" hata diya taaki galti se trigger na ho
            if any(word in user_input.lower() for word in ['exit', 'quit', 'bye', 'shutdown', 'terminate', 'system off']):
                stop_camera()
                speak("System shutting down.")
                break

            # Memory Reset Logic
            if "forget everything" in user_input.lower() or "memory clear" in user_input.lower() or "sab bhool ja" in user_input.lower():
                clear_history()
                chat_session = init_brain(history_data=[]) # Brain reset
                speak("Memory wiped. Starting fresh.")
                continue

            # --- CAMERA / SCREEN CONTROL ---
            vision_image = None
            
            # Toggle Camera (Voice Commands)
            if "camera band" in user_input.lower():
                stop_camera()
                speak("Camera disconnected.")
                continue
            elif "camera khol" in user_input.lower() or "camera on" in user_input.lower():
                start_camera()
                speak("Visual sensors activated.")
                continue
                
            # --- SMART VISION LOGIC ---
            vision_image = None
            user_lower = user_input.lower()
            
            screen_keywords = ['screen', 'window', 'monitor', 'display', 'desktop', 'kya khula hai', 'padho', 'read', 'message', 'whatsapp']
            # Generic words (kya hai, dekh, kaun) hata diye taaki galti se camera na khule
            camera_keywords = ['camera', 'photo', 'tasveer', 'pic', 'image', 'face', 'chehra', 'vision', 'selfie']

            if any(word in user_lower for word in screen_keywords):
                console.print("[dim]🖥️ Analyzing Screen Content...[/dim]")
                vision_image = get_screen_context()
            elif any(word in user_lower for word in camera_keywords):
                # Sirf tab camera frame lo jab user explicitly maange
                # Isse "Tasveer dekh li" wala issue fix ho jayega
                vision_image = get_vision_context()

            # --- AI PROCESSING ---
            # Thinking animation
            set_vision_status("PROCESSING")
            with console.status("[bold green]🧠 Thinking...[/bold green]", spinner="earth"):
                if vision_image:
                    # Text + Image bhejo
                    response = chat_session.send_message([user_input, vision_image])
                else:
                    # Sirf Text bhejo
                    response = chat_session.send_message(user_input)
            
            response_text = response.text
            
            # Print Response
            console.print(Panel(f"[bold purple]👾 R0uteR:[/bold purple] {response_text}", border_style="purple"))
            
            # Speak
            set_vision_status("SPEAKING")
            clean_text = response_text.replace("*", "").replace("#", "").replace("`", "")
            clean_text = clean_text.replace("R0uteR", "Router") # Fix pronunciation
            speak(clean_text)

            # Save
            save_interaction(user_input, response_text)

        except KeyboardInterrupt:
            stop_camera()
            break
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")

if __name__ == "__main__":
    main()