#!/usr/bin/env python3
import warnings
warnings.filterwarnings("ignore")  # Faaltu ke warnings ko chup karao

import os
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
import time

from modules.brain import init_brain
from modules.audio import speak
from modules.automation import execute_command, automate_typing, automate_keypress, send_whatsapp_message, switch_window, copy_to_clipboard, paste_from_clipboard
from modules.memory import init_db, save_interaction, load_history, clear_history
from modules.listen import listen
from modules.vision import start_camera, stop_camera, get_vision_context, get_screen_context, set_vision_status
from modules.web import perform_search

console = Console()

def main():
    # 1. Init System
    init_db()
    old_chat = load_history(limit=50)
    chat_session = init_brain(history_data=old_chat)
    
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
                        user_input = listen(duration=5, quiet=False) # Normal listening
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
            
            # --- WEB SEARCH LOGIC ---
            if "[SEARCH]:" in response_text:
                # 1. Query nikalo
                search_query = response_text.split("[SEARCH]:")[1].strip()
                
                # 2. Search karo
                set_vision_status("SEARCHING WEB")
                search_results = perform_search(search_query)
                
                # 3. Results wapas Brain ko bhejo
                with console.status("[bold green]🧠 Analyzing Search Results...[/bold green]", spinner="earth"):
                    final_response = chat_session.send_message(f"Here are the search results:\n{search_results}\n\nNow give a final answer to the user based on this.")
                    response_text = final_response.text

            # --- WHATSAPP LOGIC ---
            if "[WHATSAPP]:" in response_text:
                parts = response_text.split("[WHATSAPP]:")[1].strip()
                
                # Cleanup: Agar AI ne galti se koi aur tag append kar diya hai to usse hatao
                for tag in ["[EXECUTE]:", "[TYPE]:", "[PRESS]:", "[SWITCH]:", "[COPY]:", "[PASTE]", "[SEARCH]:"]:
                    if tag in parts:
                        parts = parts.split(tag)[0].strip()

                if "|" in parts:
                    target, msg = parts.split("|", 1)
                    send_whatsapp_message(target.strip(), msg.strip())
                else:
                    # Sirf chat kholna hai
                    send_whatsapp_message(parts.strip(), "")
                
                # Response text ko clean kar do taaki wo bole nahi "WHATSAPP..."
                response_text = response_text.split("[WHATSAPP]:")[0].strip()
                if not response_text:
                    response_text = "Opening WhatsApp..."

            # --- WINDOW SWITCH LOGIC ---
            if "[SWITCH]:" in response_text:
                parts = response_text.split("[SWITCH]:")
                response_text = parts[0].strip()
                window_name = parts[1].strip()
                if window_name:
                    window_name = window_name.replace("`", "").strip()
                    switch_window(window_name)

            # --- CLIPBOARD LOGIC ---
            copy_text = None
            do_paste = False

            if "[COPY]:" in response_text:
                parts = response_text.split("[COPY]:")
                response_text = parts[0].strip()
                copy_text = parts[1].strip().replace("`", "")
            
            if "[PASTE]" in response_text:
                response_text = response_text.replace("[PASTE]", "").strip()
                do_paste = True

            # --- GUI AUTOMATION LOGIC ---
            type_text = None
            press_key = None
            
            if "[TYPE]:" in response_text:
                parts = response_text.split("[TYPE]:")
                response_text = parts[0].strip()
                # Agar TYPE ke baad PRESS bhi hai to usse alag karo
                raw_type = parts[1].strip()
                if "[PRESS]:" in raw_type:
                    type_parts = raw_type.split("[PRESS]:")
                    type_text = type_parts[0].strip()
                    press_key = type_parts[1].strip()
                else:
                    type_text = raw_type
                
                # Cleanup backticks/quotes (Typing fix)
                if type_text: type_text = type_text.replace("`", "").strip()
                if press_key: press_key = press_key.replace("`", "").strip()
            
            elif "[PRESS]:" in response_text:
                parts = response_text.split("[PRESS]:")
                response_text = parts[0].strip()
                press_key = parts[1].strip()
                if press_key: press_key = press_key.replace("`", "").strip()

            # --- EXECUTION LOGIC ---
            cmd = None
            # Fallback: Agar AI ne tag ko backticks me daal diya ho
            if "`[EXECUTE]:" in response_text:
                response_text = response_text.replace("`[EXECUTE]:", "[EXECUTE]:")
            
            if "[EXECUTE]:" in response_text:
                parts = response_text.split("[EXECUTE]:")
                response_text = parts[0].strip()  # Ye bolne wala text hai
                cmd = parts[1].strip()
                cmd = cmd.replace("```", "").replace("`", "")  # Markdown hatao
                if (cmd.startswith("'") and cmd.endswith("'")) or (cmd.startswith('"') and cmd.endswith('"')):
                    cmd = cmd[1:-1]
                cmd = cmd.strip()

            # Print Response
            console.print(Panel(f"[bold purple]👾 R0uteR:[/bold purple] {response_text}", border_style="purple"))
            
            # Speak
            set_vision_status("SPEAKING")
            clean_text = response_text.replace("*", "").replace("#", "").replace("`", "")
            clean_text = clean_text.replace("R0uteR", "Router") # Fix pronunciation
            speak(clean_text)

            # Save
            save_interaction(user_input, response_text)
            
            # Execute
            if cmd:
                execute_command(cmd)
            
            if copy_text:
                copy_to_clipboard(copy_text)
            
            if do_paste:
                paste_from_clipboard()
            
            if type_text:
                automate_typing(type_text)
            
            if press_key:
                automate_keypress(press_key)

        except KeyboardInterrupt:
            stop_camera()
            break
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")

if __name__ == "__main__":
    main()