import os
from rich.panel import Panel
from modules.ui import console
import pyautogui
import time
import pygetwindow as gw
import pyperclip

pyautogui.FAILSAFE = False # Mouse corner me jaane se crash nahi hoga

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
        time.sleep(0.5) # Focus lene ka time
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

def switch_window(window_name):
    """Specific window pe focus karta hai."""
    try:
        console.print(f"[cyan]🔀 Switching Focus to:[/cyan] {window_name}")
        windows = gw.getWindowsWithTitle(window_name)
        if windows:
            window = windows[0]
            if window.isMinimized:
                window.restore()
            window.activate()
            time.sleep(0.5) # Thoda wait taaki focus set ho jaye
        else:
            console.print(f"[red]Window not found:[/red] {window_name}")
    except Exception as e:
        console.print(f"[red]Focus Error:[/red] {e}")

def copy_to_clipboard(text):
    """Text ko clipboard mein copy karta hai."""
    try:
        console.print(f"[cyan]📋 Copying to Clipboard:[/cyan] {text}")
        pyperclip.copy(text)
    except Exception as e:
        console.print(f"[red]Clipboard Copy Error:[/red] {e}")

def paste_from_clipboard():
    """Clipboard se paste karta hai (Ctrl+V)."""
    try:
        console.print("[cyan]📋 Pasting from Clipboard[/cyan]")
        pyautogui.hotkey('ctrl', 'v')
    except Exception as e:
        console.print(f"[red]Clipboard Paste Error:[/red] {e}")