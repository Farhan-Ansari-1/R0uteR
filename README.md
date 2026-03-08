# 👾 R0uteR - Your Personal AI System Agent

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![Platform](https://img.shields.io/badge/platform-Windows-0078D6.svg?style=flat-square)]()

**R0uteR** is a sophisticated, voice-activated AI assistant powered by **Google Gemini**. It's designed to be more than just a chatbot; it's an intelligent agent that can see, hear, speak, and interact with your computer's operating system. With a JARVIS-inspired vision HUD and deep system control, R0uteR acts as your personal coding partner, automation tool, and hacking mentor.

---

## ✨ Key Features

R0uteR is packed with features that give it a deep level of awareness and control over your system.

### 🧠 Cognitive & Core Engine
- **Google Gemini Power:** Utilizes the powerful `gemini-flash` model for fast, intelligent, and context-aware responses.
- **Always-On Mode:** Listens continuously in the background for a wake word ("Router" or "Hey").
- **Smart Silence Detection:** Automatically detects when you've stopped speaking to process your command, and goes into standby after a period of silence to save resources.
- **Persistent Memory:** Uses an SQLite database (`r0uter_memory.db`) to remember past conversations, providing long-term context for more natural interactions.

###  Advanced Vision System
- **Live Hacker HUD:** A real-time, Iron Man-inspired "Heads-Up Display" that shows:
    - A live camera feed.
    - Face detection and tracking.
    - Real-time system metrics (CPU, RAM, Battery).
    - Current AI status (Listening, Processing, Speaking, etc.).
- **Screen Awareness:** Can take a screenshot of your current screen and analyze its content. Just ask, *"Router, what's on my screen?"* or *"Read this message."*
- **Camera Vision:** Can capture images from your webcam to identify objects or people in front of you.

### ⚙️ Deep System Automation & Control
- **Command Execution:** Safely executes terminal commands. It can run diagnostics (`ping`, `ipconfig`), open applications, and manage files.
- **GUI Automation:** Can control your mouse and keyboard to type text, press keys, and perform complex sequences of actions.
- **Application Management:** Can open, switch to, and close specific application windows. For example, *"Switch to Visual Studio Code"* or *"Close Notepad"*.
- **Clipboard Control:** Can copy text to the clipboard and paste it wherever you need.

### 🌐 Web & Connectivity
- **Autonomous Web Search:** If it needs more information, R0uteR can automatically search the web using DuckDuckGo and summarize the results for you.
- **Website Opener:** Can open any URL in your default browser.
- **WhatsApp Integration:** Can open WhatsApp and send messages to your contacts or any phone number. Example: *"Send a WhatsApp to Mom saying I'll be home for dinner."*

### 🗣️ Voice & Audio Interface
- **Robust Listening:** Built with `sounddevice` for stable microphone input, automatically detecting the correct device and channels to prevent crashes.
- **Natural Text-to-Speech:** Uses `edge-tts` to generate clear and natural-sounding voice responses.

---

## 🛠️ Installation & Setup

Follow these steps to get R0uteR running on your Windows machine.

### 1. Prerequisites
- **Python 3.8+**
- **Windows Operating System** (some features like window management are OS-specific).

### 2. Clone the Repository
Open your terminal (Command Prompt or PowerShell) and run this command:
```bash
git clone https://github.com/your-username/R0uteR.git
cd R0uteR
```
*(Note: Replace `your-username` with the actual repository URL.)*

### 3. Install Dependencies
This project has several dependencies. You can install them all with a single command.

```bash
pip install -r requirements.txt
```

### 2. API Key Setup
Project folder mein ek nayi file banao jiska naam ho: `.env`
Uske andar apni Gemini API Key daalo:

```env
GEMINI_API_KEY=yahan_teri_api_key_daal
```
*(Key lene ke liye: https://aistudio.google.com/app/apikey)*

---

## 💀 How to Run

Bas ye command chala:

```bash
python R0uteR.py
```

### Controls:
- **Bolne ke liye:** Tool run hote hi mic active hoga (5 sec tak sunega).
- **Skip Voice:** Agar mic atke ya nahi bolna, to `Ctrl+C` daba, wo **Typing Mode** pe aa jayega.
- **Exit:** "Bye", "Exit", ya "Bhaag" bol/likh kar band kar sakte ho.

---

## 📂 Project Structure
- `R0uteR.py` - Main Brain (Entry Point).
- `modules/` - Saare body parts (Brain, Kaan, Mooh, Memory).