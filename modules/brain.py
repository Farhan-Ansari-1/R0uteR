from google import genai
from google.genai import types
from .config import AI_PROVIDER, API_KEY, FARX_INSTRUCTION, GEMINI_MODEL

_client = None

def get_client():
    """Returns a singleton instance of the GenAI client."""
    global _client
    if AI_PROVIDER != "gemini":
        raise ValueError(
            f"Provider '{AI_PROVIDER}' is not installed yet. Set ROUTER_AI_PROVIDER=gemini "
            "until the local-model adapter is added."
        )
    if _client is None:
        if not API_KEY:
            raise ValueError("GEMINI_API_KEY is not configured in .env")
        _client = genai.Client(api_key=API_KEY)
    return _client

def init_brain(history_data=None, tools=None):
    """
    Initializes the configured Gemini chat session with system persona and tools.
    """
    try:
        client = get_client()
        
        # Convert dictionary history from SQLite to types.Content
        formatted_history = []
        if history_data:
            for item in history_data:
                role = item.get("role")
                # google-genai expects "user" or "model"
                if role == "assistant":
                    role = "model"
                parts_text = item.get("parts", [""])[0] if isinstance(item.get("parts"), list) else str(item.get("parts", ""))
                if parts_text:
                    formatted_history.append(
                        types.Content(
                            role=role,
                            parts=[types.Part.from_text(text=parts_text)]
                        )
                    )

        # Generate config
        config = types.GenerateContentConfig(
            system_instruction=FARX_INSTRUCTION,
            temperature=0.7,
            tools=tools if tools else None,
        )

        chat = client.chats.create(
            model=GEMINI_MODEL,
            config=config,
            history=formatted_history if formatted_history else None,
        )
        return chat
    except Exception as e:
        print(f"❌ JARVIS Core Brain Initialization Error: {e}")
        raise e

def analyze_multimodal(image_input, prompt="Analyze this image in detail and answer any questions."):
    """
    Direct multimodal image analysis for camera snapshots and screen analysis.
    """
    try:
        client = get_client()
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[image_input, prompt],
            config=types.GenerateContentConfig(
                system_instruction=FARX_INSTRUCTION,
                temperature=0.4
            )
        )
        return response.text if response and response.text else "Unable to interpret visual data."
    except Exception as e:
        return f"Visual Analysis Error: {e}"
