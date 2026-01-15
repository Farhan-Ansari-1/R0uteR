import sys
import os
import time
try:
    import msvcrt
except ImportError:
    msvcrt = None

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

def listen(duration=5, quiet=False):
    # VAD Parameters (Smart Listening)
    SILENCE_THRESHOLD = 300  # Sensitivity badha di (Ab dheemi awaaz bhi sunega)
    SILENCE_LIMIT = 3.0      # Ab 3 second tak wait karega (Sochne ka time milega)
    MAX_DURATION = 30        # Max time badha diya (Lambi baat ke liye)

    try:
        # 1. Hardware se pucho ki wo kya support karta hai (Crash fix)
        device_info = sd.query_devices(kind='input')
        device_name = device_info.get('name', 'Unknown Device')
        fs = int(device_info['default_samplerate'])
        channels = int(device_info.get('max_input_channels', 1)) # Auto-detect channels
        
        if not quiet:
            console.print(f"[dim]🎧 Using Mic: {device_name} ({fs}Hz, {channels}ch)[/dim]")
            console.print(f"\n[dim green]🎤 Sun raha hoon... (Bolna shuru kar)[/dim green]")
        
        # 2. VAD Recording Loop
        audio_frames = []
        speech_started = False
        silence_start_time = None
        start_time = time.time()
        
        with sd.InputStream(samplerate=fs, channels=channels, dtype='int16') as stream:
            while True:
                # Read chunk (approx 0.1s)
                chunk_size = int(fs * 0.1)
                data, overflowed = stream.read(chunk_size)
                audio_frames.append(data)
                
                # Calculate RMS (Volume)
                rms = np.sqrt(np.mean(data**2))
                current_time = time.time()
                
                # --- VAD LOGIC ---
                if rms > SILENCE_THRESHOLD:
                    # Shor ho raha hai (Speech?)
                    if not speech_started:
                        speech_started = True
                        if not quiet:
                            console.print("[green]🗣️  Detecting Speech...[/green]", end="\r")
                    silence_start_time = None # Reset silence timer
                else:
                    # Khamoshi hai
                    if speech_started:
                        if silence_start_time is None:
                            silence_start_time = current_time
                        elif (current_time - silence_start_time) > SILENCE_LIMIT:
                            # 2 second se shant hai -> Baat khatam
                            if not quiet:
                                console.print("\n[yellow]✋ Silence Detected. Processing...[/yellow]")
                            break
                
                # --- TIMEOUTS ---
                # 1. Wait Timeout: Agar user ne bolna shuru hi nahi kiya
                if not speech_started and (current_time - start_time) > duration:
                    break
                
                # 2. Max Limit: Agar user bas bole ja raha hai (15s max)
                if (current_time - start_time) > MAX_DURATION:
                    if not quiet:
                        console.print("\n[yellow]✋ Max Limit Reached.[/yellow]")
                    break
                
                # Spacebar to stop manually
                if msvcrt and msvcrt.kbhit():
                    if msvcrt.getch() == b' ':
                        if not quiet:
                            console.print("\n[yellow]✋ Stopped manually.[/yellow]")
                        break
        
        if not audio_frames:
            return None

        # Convert list to numpy array
        myrecording = np.concatenate(audio_frames, axis=0)
        
        # 3. Save to Temp File
        wav.write('temp_mic.wav', fs, myrecording)
        
        # 4. Transcribe (Google API)
        r = sr.Recognizer()
        with sr.AudioFile('temp_mic.wav') as source:
            audio_data = r.record(source)
            
        # Cleanup: File close hone ke baad hi delete karo (Windows Rule)
        if os.path.exists("temp_mic.wav"):
            os.remove("temp_mic.wav")

        if not quiet:
            console.print("[dim]🔄 Decoding...[/dim]")
        query = r.recognize_google(audio_data, language='en-in')
        if not quiet:
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