import os
import sys
import platform
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("\n❌ Error: API Key nahi mili!")
    print("👉 Solution: '.env' file bana aur usme GEMINI_API_KEY daal.")
    sys.exit()

CURRENT_OS = platform.system()

# Secure Persona Import
try:
    from modules.persona import get_persona
    FARX_INSTRUCTION = get_persona(CURRENT_OS)
except ImportError:
    # Fallback agar file na mile (Security ke liye)
    print("⚠️ Warning: 'modules/persona.py' not found. Using default identity.")
    FARX_INSTRUCTION = f"""
    IDENTITY:
    Tera naam Router hai. Tu ek AI based jarvis Assistant hai.
    SYSTEM CONTEXT:
    - **Operating System:** {CURRENT_OS}
    """