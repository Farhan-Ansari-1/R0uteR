# 👾 R0uteR - Advanced AI System Agent

**R0uteR** is an advanced AI Assistant powered by **Google Gemini**. Far beyond a simple chatbot, R0uteR serves as an intelligent **Coding Partner** and **Hacking Mentor** capable of voice interaction, visual perception, and autonomous system command execution.

---

## 🚀 Key Features

### 🧠 **Cognitive Engine (Gemini Flash)**
- Powered by Google's latest **Gemini Flash** model.
- Specialized in software engineering, ethical hacking concepts, and technical dialogue.

### 👀 **Advanced Vision System**
- **Live Camera Feed:** Continuous background video processing providing real-time visual context.
- **Hacker HUD:** Iron Man-inspired "Heads-Up Display" overlay featuring face tracking, real-time system metrics (CPU/RAM), and status indicators.
- **Screen Awareness:** Capable of analyzing screen content on command (e.g., "Look at the screen", "Read this message").

### 🗣️ **Robust Voice Interface**
- **Listening:** Built on `SoundDevice` and `SpeechRecognition` for stability and crash resistance.
  - Features auto-detection for microphones and input channels.
- **Speaking:** Utilizes `Edge-TTS` to generate natural, human-like speech.

### 💾 **Persistent Memory**
- **SQLite Database** integration for long-term conversation retention.
- Maintains context of previous interactions (currently set to retain the last 50 exchanges).
- Database file: `r0uter_memory.db` (Auto-generated).

### ⚙️ **System Automation & Control**
- **Application Control:** Launch standard apps (Notepad, Calculator) and UWP apps (WhatsApp, Spotify).
- **Web Automation:** Open websites and perform web searches.
- **Terminal Operations:** Execute network commands (Ping, Scan) and system diagnostics.
- **Input Simulation:** Autonomous keyboard typing and key press simulation.

### 🎨 **Immersive UI**
- Cyberpunk-styled terminal interface utilizing the `Rich` library for a professional hacker aesthetic.

---

## 🛠️ Installation & Setup

### 1. Install Dependencies
Run the following command in your terminal to install the required libraries:

```bash
pip install google-generativeai python-dotenv rich edge-tts pygame speechrecognition sounddevice numpy scipy opencv-python pillow duckduckgo-search pyautogui psutil
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