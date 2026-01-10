#!/usr/bin/env python3
import warnings
warnings.filterwarnings("ignore")  # Faaltu ke warnings ko chup karao

from rich.console import Console
from rich.panel import Panel
from rich.align import Align
import time

from modules.brain import init_brain
from modules.audio import speak
from modules.automation import execute_command
from modules.memory import init_db, save_interaction, load_history
from modules.listen import listen
from modules.vision import start_camera, stop_camera, get_vision_context, get_screen_context, set_vision_status

console = Console()

def main():
    # 1. Init System
    init_db()
    old_chat = load_history(limit=50)
    chat_session = init_brain(history_data=old_chat)
    
    # 2. Start Camera immediately (Jaisa tune bola: Hamesha Open)
    start_camera()
    
    console.clear()
    console.print(Panel(Align.center("[bold green]👾 R0uteR AI - Neural Link Active[/bold green]"), border_style="green"))

    # 3. One-Time Trigger (Bas shuru mein type karo)
    console.input("\n[bold cyan]⌨️  Press Enter to Initialize Jarvis Protocol...[/bold cyan]")

    # --- ALWAYS ON MODE ---
    console.print("[bold green]🟢 System Online. Listening continuously...[/bold green]")
    console.print("[dim](Spacebar daba kar chup kara sakte ho)[/dim]")
    
    while True:
        try:
            user_input = None
            
            # --- ANIMATED LISTENING UI (Circle wala GUI) ---
            set_vision_status("LISTENING...") # HUD Update
            with console.status("[bold cyan]🎤 Listening... (Bol bhai)[/bold cyan]", spinner="dots12") as status:
                try:
                    user_input = listen() # 5 sec sunega
                except KeyboardInterrupt:
                    status.update("[yellow]✋ Stopped.[/yellow]")
                    pass
            
            if not user_input:
                # Agar kuch nahi bola, to wapas sunne lago (Loop)
                continue

            # Sleep Logic (Agar break lena ho)
            if "sleep" in user_input.lower() or "so ja" in user_input.lower():
                set_vision_status("SLEEPING")
                speak("Going to sleep mode. Press Enter to wake me up.")
                console.input("\n[bold yellow]💤 System Sleeping. Press Enter to Wake Up...[/bold yellow]")
                console.print("[bold green]🟢 System Online.[/bold green]")
                speak("I am back.")
                continue

            # Exit Logic
            if any(word in user_input.lower() for word in ['exit', 'quit', 'bye', 'bhaag', 'band ho ja', 'so ja', 'shutdown']):
                stop_camera()
                speak("System shutting down.")
                break

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
            # Agar user 'Screen', 'Window', 'Monitor' bole, to Screen dekho
            screen_keywords = ['screen', 'window', 'monitor', 'display', 'desktop', 'kya khula hai']
            if any(word in user_input.lower() for word in screen_keywords):
                console.print("[dim]🖥️ Analyzing Screen Content...[/dim]")
                vision_image = get_screen_context()
            else:
                # Default: Hamesha Camera dekho (Agar ON hai)
                vision_image = get_vision_context()
                # Note: Agar camera off hai to vision_image None hoga, jo sahi hai

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
            
            # --- EXECUTION LOGIC ---
            cmd = None
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
            speak(clean_text)

            # Save
            save_interaction(user_input, response_text)
            
            # Execute
            if cmd:
                execute_command(cmd)

        except KeyboardInterrupt:
            stop_camera()
            break
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")

if __name__ == "__main__":
    main()