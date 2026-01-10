import sys
import os
import time
import msvcrt
from modules.ui import console
import speech_recognition as sr

# --- ALTERNATIVE AUDIO LIBRARY (SoundDevice) ---
try:
    import sounddevice as sd
    import numpy as np
    import scipy.io.wavfile as wav
except ImportError:
    console.print("[bold red]❌ Error: Nayi libraries missing hain![/bold red]")
    console.print("👉 Ye command chala: [green]pip install sounddevice numpy scipy[/green]")
    sys.exit()

def listen():
    seconds = 5  # Kitni der sunega (Fixed time taaki crash na ho)

    try:
        # 1. Hardware se pucho ki wo kya support karta hai (Crash fix)
        device_info = sd.query_devices(kind='input')
        device_name = device_info.get('name', 'Unknown Device')
        fs = int(device_info['default_samplerate'])
        channels = int(device_info.get('max_input_channels', 1)) # Auto-detect channels
        
        console.print(f"[dim]🎧 Using Mic: {device_name} ({fs}Hz, {channels}ch)[/dim]")
        console.print(f"\n[dim green]🎤 Sun raha hoon... (Spacebar to stop early)[/dim green]")
        
        # 2. Record Audio (Dynamic Sample Rate ke saath)
        # channels=channels (Jo mic support kare wahi use karo)
        myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=channels, dtype='int16')
        
        # Wait loop with Interrupt (Spacebar)
        for _ in range(int((seconds + 0.5) * 10)):
            if msvcrt.kbhit():
                if msvcrt.getch() == b' ':
                    sd.stop()
                    console.print("[yellow]✋ Recording Stopped Early.[/yellow]")
                    break
            time.sleep(0.1)
            
        sd.stop() # Force stop recording
        
        # 3. Save to Temp File
        wav.write('temp_mic.wav', fs, myrecording)
        
        # 4. Transcribe (Google API)
        r = sr.Recognizer()
        with sr.AudioFile('temp_mic.wav') as source:
            audio_data = r.record(source)
            
        # Cleanup: File close hone ke baad hi delete karo (Windows Rule)
        if os.path.exists("temp_mic.wav"):
            os.remove("temp_mic.wav")

        console.print("[dim]🔄 Decoding...[/dim]")
        query = r.recognize_google(audio_data, language='en-in')
        console.print(f"[bold cyan]🗣️ You said:[/bold cyan] {query}")
        
        return query

    except sr.UnknownValueError:
        return None # Samajh nahi aaya ya shor tha
    except KeyboardInterrupt:
        console.print("\n[yellow]✋ Voice skipped.[/yellow]")
        return None
    except Exception as e:
        if "9999" in str(e):
            console.print("[bold red]❌ Privacy Error:[/bold red] Windows Settings > Privacy > Microphone check kar.")
            console.print("👉 'Allow desktop apps to access your microphone' ON hona chahiye.")
        else:
            console.print(f"[red]Mic Error:[/red] {e}")
        return None