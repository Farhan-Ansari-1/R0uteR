import google.generativeai as genai
from modules.config import API_KEY, FARX_INSTRUCTION
from modules.ui import console
import sys

def init_brain(history_data=[], tools=None):
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash', 
            system_instruction=FARX_INSTRUCTION + "\n\nNOTE: Use tools directly. DO NOT write tags like [EXECUTE].",
            tools=tools
        )
        return model.start_chat(history=history_data, enable_automatic_function_calling=True)
    except Exception as e:
        console.print(f"[bold red]❌ API Error bhai:[/bold red] {e}")
        sys.exit()