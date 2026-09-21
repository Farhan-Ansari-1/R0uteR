"""Laptop tools. Risky tools deliberately fail closed while Safe Mode is active."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import time
from urllib.parse import quote
import webbrowser

import psutil
import pyautogui
import pygetwindow as gw
import pyperclip

from .security import (
    is_protected_path,
    is_safe_command,
    require_safe_path,
    require_user_approval,
    safe_delete_path,
)

# Physical emergency stop: move the pointer to a screen corner.
pyautogui.FAILSAFE = True


def _clean_input(text: str) -> str:
    if not text:
        return ""
    text = str(text).strip()
    while len(text) > 1 and text[0] == text[-1] and text[0] in "'\"`":
        text = text[1:-1].strip()
    return text[3:-3].strip() if text.startswith("```") and text.endswith("```") else text


def read_system_file(file_path: str, max_lines: int = 300) -> str:
    file_path = _clean_input(file_path)
    permitted, message = require_safe_path("read_file", file_path)
    if not permitted:
        return message
    if not os.path.isfile(file_path):
        return f"File does not exist or is not a file: {file_path}"
    try:
        max_lines = max(1, min(int(max_lines), 300))
        with open(file_path, "r", encoding="utf-8", errors="replace") as source:
            content = "".join(source.readline() for _ in range(max_lines))
        return f"FILE CONTENT ({file_path}):\n```\n{content}\n```"
    except OSError as error:
        return f"Failed to read file: {error}"


def write_system_file(file_path: str, content: str) -> str:
    file_path = _clean_input(file_path)
    permitted, message = require_safe_path("write_file", file_path)
    if not permitted:
        return message
    approved, message = require_user_approval("write_file", file_path)
    if not approved:
        return message
    try:
        parent = os.path.dirname(file_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as destination:
            destination.write(content)
        return f"Wrote {len(content)} characters to '{file_path}'."
    except OSError as error:
        return f"Failed to write file: {error}"


def list_system_directory(directory_path: str = ".") -> str:
    directory_path = _clean_input(directory_path)
    permitted, message = require_safe_path("list_directory", directory_path)
    if not permitted:
        return message
    if not os.path.isdir(directory_path):
        return f"Directory does not exist: {directory_path}"
    try:
        entries = sorted(os.listdir(directory_path))[:60]
        result = []
        for entry in entries:
            full_path = os.path.join(directory_path, entry)
            if is_protected_path(full_path):
                result.append(f"[protected] {entry}")
            elif os.path.isdir(full_path):
                result.append(f"[folder] {entry}/")
            else:
                result.append(f"[file] {entry} ({round(os.path.getsize(full_path) / 1024, 1)} KB)")
        return f"DIRECTORY LISTING for '{directory_path}':\n" + "\n".join(result)
    except OSError as error:
        return f"Error listing directory: {error}"


def search_laptop_files(filename_pattern: str, search_directory: str = "D:\\Projects") -> str:
    filename_pattern = _clean_input(filename_pattern).lower()
    search_directory = _clean_input(search_directory)
    permitted, message = require_safe_path("search_files", search_directory)
    if not permitted:
        return message
    if not filename_pattern or not os.path.isdir(search_directory):
        return "Provide a valid search term and directory."
    matches: list[str] = []
    try:
        for root, dirs, files in os.walk(search_directory):
            dirs[:] = [name for name in dirs if not is_protected_path(os.path.join(root, name))]
            for name in files:
                full_path = os.path.join(root, name)
                if filename_pattern in name.lower() and not is_protected_path(full_path):
                    matches.append(full_path)
                    if len(matches) == 20:
                        return "FOUND 20 MATCHES (limit):\n" + "\n".join(matches)
        return "FOUND MATCHES:\n" + "\n".join(matches) if matches else f"No files matching '{filename_pattern}'."
    except OSError as error:
        return f"File search error: {error}"


def delete_file_safely(file_path: str) -> str:
    return safe_delete_path(_clean_input(file_path))[1]


def run_python_code(code: str) -> str:
    code = _clean_input(code)
    if not code:
        return "Provide Python code to execute."

    approved, message = require_user_approval("run_python_code", "Python snippet")
    if not approved:
        return message

    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=20,
            shell=False,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return "Python execution timed out after 20 seconds."
    except OSError as error:
        return f"Could not start Python execution: {error}"

    output = (result.stdout + result.stderr).strip()
    if not output:
        output = "No output."
    status = "SUCCESS" if result.returncode == 0 else f"FAILED (exit {result.returncode})"
    return f"PYTHON EXECUTION: {status}\n\n{output}"


def execute_terminal_command(command: str) -> str:
    _, message = is_safe_command(_clean_input(command))
    return message


def open_application(app_name: str) -> str:
    app_name = _clean_input(app_name).lower()
    approved, message = require_user_approval("open_application", app_name)
    if not approved:
        return message
    app_map = {
        "vs code": "code", "vscode": "code", "notepad": "notepad", "calculator": "calc",
        "calc": "calc", "explorer": "explorer", "task manager": "taskmgr", "terminal": "wt",
        "chrome": "chrome", "google chrome": "chrome",
    }
    command = app_map.get(app_name)
    if not command:
        return "That app is not in the approved launcher list yet."
    try:
        executable = shutil.which(command)
        if not executable and command == "chrome" and os.name == "nt":
            candidates = [
                os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
            ]
            executable = next((path for path in candidates if os.path.isfile(path)), None)
        if not executable:
            return f"Could not find {app_name} on this computer."
        subprocess.Popen([executable], shell=False)
        return f"Opened {app_name}."
    except OSError as error:
        return f"Could not open {app_name}: {error}"


def automate_typing(text: str) -> str:
    text = _clean_input(text)
    if not text:
        return "No text provided to type."
    approved, message = require_user_approval("automate_typing", text[:80])
    if not approved:
        return message
    try:
        pyautogui.write(text, interval=0.01)
        return f"Typed {len(text)} characters."
    except pyautogui.FailSafeException:
        return "Typing stopped by the mouse-corner fail-safe."
    except Exception as error:
        return f"Automate typing error: {error}"


def automate_keypress(key: str) -> str:
    key = _clean_input(key).lower()
    if not key:
        return "No key provided to press."
    approved, message = require_user_approval("automate_keypress", key)
    if not approved:
        return message
    try:
        pyautogui.press(key)
        return f"Pressed key '{key}'."
    except pyautogui.FailSafeException:
        return "Keypress stopped by the mouse-corner fail-safe."
    except Exception as error:
        return f"Keypress error: {error}"


def switch_window(window_title: str) -> str:
    window_title = _clean_input(window_title)
    if not window_title:
        return "Provide a window title to switch to."
    approved, message = require_user_approval("switch_window", window_title)
    if not approved:
        return message
    try:
        windows = gw.getWindowsWithTitle(window_title)
        if not windows:
            return f"No open window found matching '{window_title}'."
        target_win = windows[0]
        if target_win.isMinimized:
            target_win.restore()
        target_win.activate()
        return f"Switched to window: {target_win.title}"
    except Exception as error:
        return f"Could not switch window: {error}"


def close_window(window_title: str) -> str:
    window_title = _clean_input(window_title)
    if not window_title:
        return "Provide a window title to close."
    approved, message = require_user_approval("close_window", window_title)
    if not approved:
        return message
    try:
        windows = gw.getWindowsWithTitle(window_title)
        if not windows:
            return f"No open window found matching '{window_title}'."
        title = windows[0].title
        windows[0].close()
        return f"Closed window: {title}"
    except Exception as error:
        return f"Could not close window: {error}"


def open_website(url: str) -> str:
    url = _clean_input(url)
    if not url.startswith(("https://", "http://")):
        url = "https://" + url
    approved, message = require_user_approval("open_website", url)
    if not approved:
        return message
    webbrowser.open(url)
    return f"Opened {url}."


def copy_to_clipboard(text: str) -> str:
    approved, message = require_user_approval("copy_to_clipboard", "generated text")
    if not approved:
        return message
    pyperclip.copy(text)
    return "Copied generated text to clipboard."


def paste_from_clipboard() -> str:
    approved, message = require_user_approval("read_clipboard", "clipboard content")
    if not approved:
        return message
    try:
        content = pyperclip.paste()
        return f"CLIPBOARD CONTENT:\n{content}"
    except Exception as error:
        return f"Could not read clipboard: {error}"


def parse_whatsapp_command(text: str) -> tuple[str, str]:
    """Parse natural text like 'Farhan ko WhatsApp pe bro kya haal hai message kar'."""
    text = _clean_input(text)
    if not text:
        return "", ""

    lower_text = text.lower()
    if not any(token in lower_text for token in ("whatsapp", "wa ", "msg", "message")):
        return "", ""

    target_match = re.search(
        r"(?i)(?:^|\s)([A-Za-z][A-Za-z0-9_.-]{1,20})\s*(?:ko|to)?\s*(?:whatsapp|wa|msg|message)\b",
        text,
    )
    if not target_match:
        return "", ""

    target = target_match.group(1).strip(" -_")
    if not target:
        return "", ""

    remainder = text[target_match.end():]
    remainder = re.sub(r"(?i)\b(?:whatsapp|wa|msg|message|send|text|karo|kar|bhejo|ko|to|pe|par|for|bro|hey|hi|hello|sir|please)\b", " ", remainder)
    remainder = re.sub(r"\s+", " ", remainder).strip(" -_:")
    if not remainder:
        remainder = "hello"

    return target, remainder


def send_whatsapp_message(target: str, message: str) -> str:
    target = _clean_input(target)
    message = _clean_input(message)
    if not message:
        return "Provide the WhatsApp message text."
    phone = re.sub(r"[^0-9]", "", target)
    numeric_target = bool(re.search(r"\d", target))
    if numeric_target and (len(phone) < 8 or len(phone) > 15):
        return "Provide a valid phone number with country code, for example +91 9876543210."
    if not numeric_target and len(target) < 2:
        return "Provide the WhatsApp contact name."
    mode = f"direct phone +{phone}" if numeric_target else f"search contact '{target}'"
    preview = f"WhatsApp {mode}: {message[:120]}"
    approved, approval_message = require_user_approval("send_whatsapp_message", preview)
    if not approved:
        return approval_message
    try:
        if numeric_target:
            url = f"https://web.whatsapp.com/send?phone={phone}&text={quote(message)}"
            webbrowser.open(url)
            time.sleep(5)
        else:
            webbrowser.open("https://web.whatsapp.com")
            time.sleep(7)
            pyautogui.hotkey("ctrl", "alt", "/")
            time.sleep(1)
            pyautogui.write(target, interval=0.03)
            time.sleep(2)
            pyautogui.press("enter")
            time.sleep(2)
            pyautogui.write(message, interval=0.01)
        pyautogui.press("enter")
        return f"WhatsApp message sent to {target} after your one-time approval."
    except pyautogui.FailSafeException:
        return "WhatsApp send stopped by the mouse-corner fail-safe."
    except OSError as error:
        return f"Could not open WhatsApp: {error}"


def get_battery_and_hardware_status() -> str:
    try:
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage("C:\\")
        battery = psutil.sensors_battery()
        battery_text = "No battery detected" if not battery else f"{battery.percent}% ({'charging' if battery.power_plugged else 'discharging'})"
        return (
            f"SYSTEM TELEMETRY:\n- Battery: {battery_text}\n- CPU: {cpu}%\n"
            f"- RAM: {ram.percent}%\n- C: disk: {disk.percent}% used"
        )
    except OSError as error:
        return f"Hardware status error: {error}"


def control_media(action: str) -> str:
    action = _clean_input(action).lower()
    mapping = {
        "volume_up": "volumeup", "volume_down": "volumedown", "mute": "volumemute",
        "play_pause": "playpause", "next_track": "nexttrack", "prev_track": "prevtrack",
    }
    key = mapping.get(action)
    if not key:
        return f"Unknown media action: {action}"
    try:
        pyautogui.press(key, presses=5 if action.startswith("volume_") else 1)
        return f"Media action completed: {action}"
    except pyautogui.FailSafeException:
        return "Media action stopped by the mouse-corner fail-safe."
    except Exception as error:
        return f"Media control error: {error}"
