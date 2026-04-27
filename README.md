# 👾 R0uteR — Your Personal AI System Agent

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![Platform](https://img.shields.io/badge/platform-Windows-0078D6.svg?style=flat-square)]()
[![AI](https://img.shields.io/badge/AI-Native%20Function%20Calling-blueviolet)]()
[![Mode](https://img.shields.io/badge/Mode-Voice%20%7C%20Vision%20%7C%20Execution-black)]()

---

## 🧠 Overview

**R0uteR** is a **voice-activated, multimodal AI system agent** powered by **Google Gemini**.

It’s not just a chatbot — it’s an **intelligent system layer** that can:

* 🎤 Listen (voice commands)
* 👁️ See (camera + screen analysis)
* 🧠 Think (AI reasoning + memory)
* ⚙️ Act (real system execution)

With deep system integration and a hacker-style HUD, R0uteR acts as your:

* 💻 Coding partner
* ⚙️ Automation engine
* 🧠 Thinking assistant

---

# ✨ Key Features

## 🧠 Cognitive & Core Engine

* ⚡ Powered by **Gemini 2.5 Flash**
* 🧩 **Native Function Calling** (REAL execution, not fake parsing)
* 🧠 Context-aware responses
* 💾 Persistent memory (SQLite)
* 🎧 Always-on listening (wake word: *Router*)

---

## 👁️ Advanced Vision System

* 🕶️ Live **Hacker HUD**

  * Camera feed
  * Face detection & tracking
  * System stats (CPU, RAM, Battery)
  * AI state (Listening / Processing / Speaking)

* 🖥️ Screen awareness
  → *"Router, what's on my screen?"*

* 📸 Camera capture & analysis

---

## ⚙️ System Automation (The Real Power)

* 🖥️ Execute OS commands
* ⌨️ Control keyboard & mouse
* 📂 File system interaction
* 📋 Clipboard automation
* 📱 WhatsApp automation
* 🌐 Smart web search

---

## 🗣️ Voice & Audio System

* 🎤 Stable mic input (`sounddevice`)
* 🧠 Smart silence detection
* 🔊 Natural voice output (`edge-tts`)

---

# 🧠 Live Example

```bash
User: "Router, list the files in the modules folder and read brain.py"

🔧 Tool Triggered: list_directory_files
🔧 Tool Triggered: read_file_content

👾 R0uteR: "I've scanned the modules. brain.py is using Gemini 2.5 with 
            automatic function calling enabled. Should I optimize the history limit?"
```

---

# 🛠️ Installation & Setup

## 1. Requirements

* Python 3.8+
* Windows OS (recommended)

---

## 2. Clone Repository

```bash
git clone https://github.com/your-username/R0uteR.git
cd R0uteR
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. API Key Setup

Create `.env` file:

```env
GEMINI_API_KEY=your_api_key_here
```

Get your key from:
https://aistudio.google.com/app/apikey

---

# 💀 How to Run

```bash
python R0uteR.py
```

---

## 🎮 Controls

| Action    | Trigger                 |
| --------- | ----------------------- |
| Wake      | "Router" / "Hey Router" |
| Interrupt | Ctrl + C                |
| Exit      | "Exit", "Bye"           |

---

# 📂 Project Structure

```bash
R0uteR/
│
├── R0uteR.py              # Main entry
│
├── modules/
│   ├── brain.py           # Gemini + Function Calling
│   ├── automation.py      # OS control
│   ├── vision.py          # HUD + camera
│   └── audio.py           # voice system
│
├── assets/                # GIF demos
├── .env                   # API key
├── r0uter_memory.db       # memory database
├── requirements.txt
└── README.md
```

---

# 🧩 Why R0uteR

* Not just chat → **real system execution**
* Voice + Vision + Action combined
* Persistent memory
* Function-calling based intelligence
* Feels like a **real AI system, not a script**

---

# ⚠️ Ethical Use

## ✅ Allowed

* Learning
* Automation
* Development

## ❌ Not Allowed

* Unauthorized access
* Malicious hacking
* Privacy violation

---

# 💀 Final Line

> R0uteR is not your assistant.
> It’s your second brain connected to your system.

---

⭐ Star it. Fork it. Break it. Rebuild it.
