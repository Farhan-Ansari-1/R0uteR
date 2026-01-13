import os
from rich.panel import Panel
from modules.ui import console
import pyautogui
import time

def execute_command(command):
    console.print(Panel(f"[bold yellow]⚙️ Executing Command:[/bold yellow] {command}", border_style="yellow"))
    try:
        # Security Check
        if "rm -rf" in command or "format" in command or "del /" in command or "rd /" in command:
            console.print("[bold red]⚠️ Command Blocked (Safety Protocol).[/bold red]")
            return
        os.system(command)
    except KeyboardInterrupt:
        console.print("\n[bold red]⚠️ Command Stopped by User (R0uteR is still alive).[/bold red]")
    except Exception as e:
        console.print(f"[bold red]❌ Execution Error:[/bold red] {e}")

def automate_typing(text):
    """Keyboard se text type karta hai."""
    try:
        console.print(f"[cyan]⌨️ Typing:[/cyan] {text}")
        pyautogui.write(text, interval=0.05) # Thoda delay taaki natural lage
    except Exception as e:
        console.print(f"[red]Typing Error:[/red] {e}")

def automate_keypress(key):
    """Koi specific button dabata hai (Enter, Tab, etc)."""
    try:
        console.print(f"[cyan]🎹 Pressing:[/cyan] {key}")
        pyautogui.press(key)
    except Exception as e:
        console.print(f"[red]Key Error:[/red] {e}")

def send_whatsapp_message(target, message):
    """WhatsApp pe message bhejta hai (Name search ya Number se)."""
    try:
        console.print(f"[green]📱 WhatsApp Action: {target} -> {message}[/green]")
        
        # 1. Open WhatsApp
        os.system("start whatsapp:")
        time.sleep(1.5) # App khulne ka wait
        
        # 2. Target Selection
        if target.isdigit() and len(target) >= 10:
            # Agar number hai to direct link
            os.system(f"start whatsapp://send?phone={target}")
            time.sleep(2)
        else:
            # Agar naam hai to Search karo
            pyautogui.hotkey('ctrl', 'f') # Search bar
            time.sleep(0.5)
            pyautogui.write(target) # Naam likho
            time.sleep(1.0)
            pyautogui.press('enter') # Chat kholo
            time.sleep(0.5)
            
        # 3. Message Send (Agar message hai to)
        if message:
            pyautogui.write(message)
            time.sleep(0.5)
            pyautogui.press('enter')
            
    except Exception as e:
        console.print(f"[red]WhatsApp Error:[/red] {e}")