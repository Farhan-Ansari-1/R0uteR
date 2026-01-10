import sqlite3
from modules.ui import console

DB_NAME = "r0uter_memory.db"

def init_db():
    """Database aur Table create karta hai agar nahi hai to."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT,
                message TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        console.print(f"[red]Memory Error:[/red] {e}")

def save_interaction(user_text, ai_text):
    """User aur AI ki baatein save karta hai."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO chat_history (role, message) VALUES (?, ?)", ("user", user_text))
        cursor.execute("INSERT INTO chat_history (role, message) VALUES (?, ?)", ("model", ai_text))
        conn.commit()
        conn.close()
    except Exception as e:
        console.print(f"[red]Failed to save memory:[/red] {e}")

def load_history(limit=10):
    """Pichli baatein load karta hai taaki AI ko context mile."""
    history = []
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        # Last 'limit' messages uthao
        cursor.execute("SELECT role, message FROM chat_history ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        # Reverse karke chronological order mein laao (Purana pehle, naya baad mein)
        for role, msg in reversed(rows):
            history.append({"role": role, "parts": [msg]})
            
        # Rule: Chat hamesha User se start honi chahiye (API requirement)
        if history and history[0]['role'] == 'model':
            history.pop(0)
            
    except Exception as e:
        console.print(f"[red]Failed to load memory:[/red] {e}")
    
    return history