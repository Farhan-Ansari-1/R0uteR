import os
from rich.panel import Panel
from modules.ui import console
import pyautogui
import time
import pygetwindow as gw
import pyperclip
import webbrowser

pyautogui.FAILSAFE = False # Mouse corner me jaane se crash nahi hoga

def _clean_input(text):
    """AI dwara add kiye gaye extra quotes aur backticks ko hatata hai."""
    if not text:
        return ""
    text = text.strip()
    # Remove surrounding quotes/backticks
    while len(text) > 1 and ((text.startswith('"') and text.endswith('"')) or 
                             (text.startswith("'") and text.endswith("'")) or 
                             (text.startswith('`') and text.endswith('`'))):
        text = text[1:-1].strip()
    return text

def execute_command(command):
    """
    Executes a system shell command. Use this to run terminal commands or open system apps.
    Args:
        command (str): The command to execute (e.g., 'start notepad', 'ipconfig').
    """
    command = _clean_input(command)
    console.print(Panel(f"[bold yellow]⚙️ Executing Command:[/bold yellow] {command}", border_style="yellow"))
    try:
        # Security Check
        if "rm -rf" in command or "format" in command or "del /" in command or "rd /" in command:
            console.print("[bold red]⚠️ Command Blocked (Safety Protocol).[/bold red]")
            return

        # Special-case: Windows 'start <url>' sometimes fails when the URL is quoted
        # (start treats a quoted first arg as the window title). Detect URL targets and
        # open them via the system's webbrowser module which is more reliable.
        cmd_strip = command.strip()
        if cmd_strip.lower().startswith('start '):
            target = cmd_strip[6:].strip()
            # Remove surrounding quotes/backticks if any (single/double/backticks)
            if (target.startswith('"') and target.endswith('"')) or (target.startswith("'") and target.endswith("'")) or (target.startswith('`') and target.endswith('`')):
                target = target[1:-1].strip()
            # If it looks like a URL, open it using webbrowser rather than `start`
            if target.startswith('http') or ('.' in target and ' ' not in target):
                webbrowser.open(target)
                return

        os.system(command)
    except KeyboardInterrupt:
        console.print("\n[bold red]⚠️ Command Stopped by User (R0uteR is still alive).[/bold red]")
    except Exception as e:
        console.print(f"[bold red]❌ Execution Error:[/bold red] {e}")

def automate_typing(text):
    """
    Types the given text using the keyboard. Useful for writing messages or filling forms.
    Args:
        text (str): The text content to be typed.
    """
    try:
        console.print(f"[cyan]⌨️ Typing:[/cyan] {text}")
        time.sleep(0.5) # Focus lene ka time
        pyautogui.write(text, interval=0.05) # Thoda delay taaki natural lage
    except Exception as e:
        console.print(f"[red]Typing Error:[/red] {e}")

def automate_keypress(key):
    """
    Simulates a single key press on the keyboard.
    Args:
        key (str): The name of the key to press (e.g., 'enter', 'tab', 'esc').
    """
    try:
        console.print(f"[cyan]🎹 Pressing:[/cyan] {key}")
        pyautogui.press(key)
    except Exception as e:
        console.print(f"[red]Key Error:[/red] {e}")

def send_whatsapp_message(target, message):
    """
    Opens WhatsApp and sends a message to a specific contact or phone number.
    Args:
        target (str): Name of the contact or a phone number (with country code).
        message (str): The message content to send.
    """
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
    """
    Switches focus to an open application window by its title.
    Args:
        window_name (str): The title of the window to switch to.
    """
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

def close_window(window_name):
    """
    Closes an open window by its title.
    Args:
        window_name (str): The title of the window to close.
    """
    try:
        console.print(f"[bold red]❌ Closing Window:[/bold red] {window_name}")
        windows = gw.getWindowsWithTitle(window_name)
        if windows:
            for window in windows:
                if window_name.lower() in window.title.lower():
                    window.close()
                    console.print(f"[dim]Closed: {window.title}[/dim]")
                    time.sleep(0.5)
        else:
            console.print(f"[red]Window not found to close:[/red] {window_name}")
    except Exception as e:
        console.print(f"[red]Close Error:[/red] {e}")

def open_website(url):
    """
    Opens a specified website URL in the default web browser.
    Args:
        url (str): The URL of the website to open.
    """
    url = _clean_input(url)
    try:
        if not url.startswith('http'):
            url = 'https://' + url
        console.print(f"[cyan]🌐 Opening Website:[/cyan] {url}")
        webbrowser.open(url)
    except Exception as e:
        console.print(f"[red]Web Error:[/red] {e}")

def copy_to_clipboard(text):
    """
    Copies the provided text to the system clipboard.
    Args:
        text (str): The text to copy.
    """
    try:
        console.print(f"[cyan]📋 Copying to Clipboard:[/cyan] {text}")
        pyperclip.copy(text)
    except Exception as e:
        console.print(f"[red]Clipboard Copy Error:[/red] {e}")

def paste_from_clipboard():
    """
    Simulates a 'Ctrl+V' keyboard shortcut to paste text content from the system clipboard 
    into the currently focused application.
    """
    try:
        console.print("[cyan]📋 Pasting from Clipboard[/cyan]")
        pyautogui.hotkey('ctrl', 'v')
    except Exception as e:
        console.print(f"[red]Clipboard Paste Error:[/red] {e}")

def read_file_content(file_path):
    """
    Reads and returns the content of a text-based file from the system. 
    Useful for analyzing code or documents.
    Args:
        file_path (str): The absolute or relative path to the file.
    """
    try:
        # Basic safety: check file size (don't read huge binaries)
        if os.path.getsize(file_path) > 1024 * 500: # 500KB limit
            return "Error: File is too large to read."
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            console.print(f"[cyan]📖 Reading File:[/cyan] {file_path}")
            return content
    except Exception as e:
        return f"Error reading file: {str(e)}"

def list_directory_files(directory_path="."):
    """
    Lists all files and subdirectories in a given path. 
    Use this to understand the project structure before reading files.
    Args:
        directory_path (str): The path to explore (default is current folder).
    """
    try:
        items = os.listdir(directory_path)
        console.print(f"[cyan]📂 Exploring Folder:[/cyan] {directory_path}")
        return "\n".join(items)
    except Exception as e:
        return f"Error listing files: {str(e)}"