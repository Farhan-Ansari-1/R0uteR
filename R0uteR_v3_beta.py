import os
import warnings
import google.generativeai as genai
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
import functools

from modules.config import API_KEY, FARX_INSTRUCTION
from modules.audio import speak
from modules.automation import (
    execute_command, automate_typing, automate_keypress, 
    send_whatsapp_message, switch_window, close_window, 
    open_website, copy_to_clipboard, paste_from_clipboard, read_file_content
)
from modules.memory import init_db, save_interaction, load_history
from modules.listen import listen
from modules.vision import start_camera, stop_camera, get_vision_context, get_screen_context, set_vision_status
from modules.web import perform_search

warnings.filterwarnings("ignore")
console = Console()

# 0. Tool Wrapper for Logging
def log_tool_call(func):
    """Har tool call ko console par log karta hai taaki beta testing me dikhe Gemini kya kar raha hai."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        params = ", ".join([repr(a) for a in args] + [f"{k}={repr(v)}" for k, v in kwargs.items()])
        console.print(Panel(f"[bold blue]🔧 Tool Triggered:[/bold blue] [green]{func.__name__}[/green]\n[dim]Input: {params}[/dim]", border_style="blue"))
        return func(*args, **kwargs)
    return wrapper

# 1. Define Tools (Wrapped with logging)
tools_list = [log_tool_call(f) for f in [
    execute_command, automate_typing, automate_keypress, 
    send_whatsapp_message, switch_window, close_window, 
    open_website, copy_to_clipboard, paste_from_clipboard,
    perform_search, read_file_content
]]

def init_beta_brain(history_data=[]):
    genai.configure(api_key=API_KEY)
    # Create model with tools
    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        system_instruction=FARX_INSTRUCTION + "\n\nNOTE: Use tools directly instead of writing tags like [EXECUTE].",
        tools=tools_list
    )
    return model.start_chat(history=history_data, enable_automatic_function_calling=True)

def main():
    init_db()
    old_chat = load_history(limit=20)
    # Beta Brain uses tools!
    chat_session = init_beta_brain(history_data=old_chat)
    
    os.system("title R0uteR BETA - Function Calling Mode")
    start_camera()
    
    console.clear()
    console.print(Panel(Align.center("[bold cyan]🧪 R0uteR v3 BETA - Function Calling Enabled[/bold cyan]"), border_style="cyan"))
    speak("Beta system active. Function calling initialized.")
    
    IS_AWAKE = True

    while True:
        try:
            user_input = None
            
            if not IS_AWAKE:
                set_vision_status("STANDBY")
                user_input = listen(duration=3, quiet=True)
                if user_input and ("router" in user_input.lower()):
                    IS_AWAKE = True
                    speak("I am back.")
                continue

            set_vision_status("LISTENING...")
            user_input = listen(duration=20, quiet=False) # Increased duration
            
            if not user_input:
                continue

            # Basic Exit commands
            if any(word in user_input.lower() for word in ['exit', 'shutdown', 'terminate']):
                stop_camera()
                speak("Shutting down beta system.")
                break

            # Vision logic (Still manual keyword for context, but actions are tools)
            vision_image = None
            user_lower = user_input.lower()
            if any(word in user_lower for word in ['screen', 'window', 'display']):
                vision_image = get_screen_context()
            elif any(word in user_lower for word in ['camera', 'photo', 'vision']):
                vision_image = get_vision_context()

            # --- AI PROCESSING (The Magic happens here) ---
            set_vision_status("THINKING")
            with console.status("[bold green]🧠 Function Calling in progress...[/bold green]"):
                if vision_image:
                    response = chat_session.send_message([user_input, vision_image])
                else:
                    response = chat_session.send_message(user_input)

            # response.text contain clear reply, functions have already executed!
            response_text = response.text
            
            console.print(Panel(f"[bold purple]👾 R0uteR (BETA):[/bold purple] {response_text}", border_style="purple"))
            
            set_vision_status("SPEAKING")
            speak(response_text.replace("*", ""))
            save_interaction(user_input, response_text)

        except Exception as e:
            console.print(f"[red]Beta Error:[/red] {e}")
            # Fallback if chat session crashes
            chat_session = init_beta_brain()

if __name__ == "__main__":
    main()
