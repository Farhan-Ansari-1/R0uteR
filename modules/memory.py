import sqlite3
import os
from pathlib import Path

DB_NAME = str(Path(__file__).resolve().parents[1] / "r0uter_memory.db")

def init_db():
    """Initializes the SQLite database and interaction table if not existing."""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT,
                    message TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contacts (
                    name TEXT PRIMARY KEY COLLATE NOCASE,
                    phone TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
    except Exception as e:
        print(f"Memory Init Error: {e}")

def save_interaction(user_text: str, ai_text: str):
    """Saves user query and AI response into persistent SQLite database."""
    if not user_text or not ai_text:
        return
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO chat_history (role, message) VALUES (?, ?)", ("user", user_text))
            cursor.execute("INSERT INTO chat_history (role, message) VALUES (?, ?)", ("model", ai_text))
            conn.commit()
    except Exception as e:
        print(f"Failed to save memory: {e}")

def load_history(limit: int = 14) -> list:
    """Loads recent conversation history for continuous context across sessions."""
    history = []
    try:
        if not os.path.exists(DB_NAME):
            init_db()
            return []

        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT role, message FROM chat_history ORDER BY id DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()

        for role, msg in reversed(rows):
            history.append({"role": role, "parts": [msg]})

        # Ensure history begins with user turn for Gemini API compliance
        if history and history[0]['role'] == 'model':
            history.pop(0)

    except Exception as e:
        print(f"Failed to load memory: {e}")

    return history

def clear_history() -> str:
    """Clears all stored conversation history."""
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chat_history")
            conn.commit()
        return "🧹 Memory records cleared successfully, Sir."
    except Exception as e:
        return f"Failed to clear memory: {e}"


def save_contact(name: str, phone: str) -> str:
    """Store a user-provided contact locally without syncing it anywhere."""
    name = (name or "").strip()[:80]
    phone = (phone or "").strip()
    if not name or not phone:
        return "Provide both a contact name and phone number."

    from .security import require_user_approval

    approved, message = require_user_approval("save_contact", f"{name}: {phone}")
    if not approved:
        return message

    try:
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO contacts (name, phone, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
                (name, phone),
            )
            conn.commit()
        return f"Contact '{name}' saved locally."
    except sqlite3.Error as error:
        return f"Could not save contact: {error}"


def resolve_contact(name: str) -> str | None:
    """Resolve a local contact name to its stored phone number."""
    name = (name or "").strip()
    if not name:
        return None
    try:
        with sqlite3.connect(DB_NAME) as conn:
            row = conn.execute("SELECT phone FROM contacts WHERE name = ? COLLATE NOCASE", (name,)).fetchone()
        return row[0] if row else None
    except sqlite3.Error:
        return None
