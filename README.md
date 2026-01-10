# 👾 R0uteR - The Hacker's AI Assistant

**R0uteR** ek advanced AI Assistant hai jo **Google Gemini** se powered hai. Ye sirf ek chatbot nahi, balki ek **Coding Partner** aur **Hacking Mentor** hai jo tumhari awaaz sun sakta hai, bol sakta hai, aur system commands execute kar sakta hai.

---

## 🚀 Features (Abhi tak ka update)

### 🧠 **Super Brain (Gemini 2.5)**
- Google ka latest **Gemini 2.5 Flash** model use karta hai.
- Coding, Hacking concepts, aur General talks mein expert.

### 👀 **Advanced Vision System (Aankhein)**
- **Live Camera Feed:** Background mein camera chalta hai jo AI ko real-time vision deta hai.
- **Hacker HUD:** Iron Man style "Heads-Up Display" overlay (Green Reticle, System Info, Status) jo screen par dikhta hai.
- **Screen Awareness:** Agar tum "Screen dekho" ya "kya khula hai" bologe, to ye screenshot lekar analyze karega.

### ️ **Robust Voice System (No Crashes)**
- **Sunna (Listen):** `SoundDevice` + `SpeechRecognition` ka use karke banaya gaya hai.
  - *Faayda:* Purane `PyAudio` errors (mic freeze/crash) fix ho gaye hain.
  - Auto-detects Mic & Channels.
- **Bolna (Speak):** `Edge-TTS` ka use karta hai jo ekdum insaan jaisi awaaz (Natural Voice) nikalta hai.

### 💾 **Long-Term Memory**
- **SQLite Database** ka use karke purani baatein yaad rakhta hai.
- Abhi pichli **50 baatein** yaad rakhne ki shamta hai (Free & Local).
- Database file: `R0uteR_memory.db` (Auto-created).

### ⚙️ **System Automation**
- **Apps Open:** Notepad, Calculator, Chrome, etc.
- **Store Apps:** WhatsApp, Spotify (`start whatsapp:` support).
- **Websites:** Youtube, Google, etc.
- **Terminal:** Ping, Scan, aur basic commands run kar sakta hai.

### 🎨 **Hacker UI**
- `Rich` library ka use karke Matrix/Cyberpunk style terminal interface.

---

## 🛠️ Installation & Setup

### 1. Requirements Install karo
Terminal mein ye command chalao taaki saari libraries aa jayein:

```bash
pip install google-generativeai python-dotenv rich edge-tts pygame speechrecognition sounddevice numpy scipy opencv-python pillow
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