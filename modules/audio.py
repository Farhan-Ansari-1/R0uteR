import edge_tts
import asyncio
import os
import platform
try:
    import msvcrt # Keyboard check karne ke liye (Windows)
except ImportError:
    msvcrt = None

from modules.ui import console

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

async def generate_audio(text):
    communicate = edge_tts.Communicate(text, "en-IN-PrabhatNeural", rate="+25%")
    await communicate.save("voice.mp3")

def speak(text):
    try:
        asyncio.run(generate_audio(text))
        if platform.system() == "Windows":
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load("voice.mp3")
            pygame.mixer.music.play()
            
            try:
                while pygame.mixer.music.get_busy():
                    # Agar user Spacebar dabaye, to bolna band karo
                    if msvcrt and msvcrt.kbhit():
                        if msvcrt.getch() == b' ':
                            pygame.mixer.music.stop()
                            console.print("\n[yellow]✋ Speech Interrupted (Spacebar).[/yellow]")
                            break
                    pygame.time.Clock().tick(10)
            except KeyboardInterrupt:
                pygame.mixer.music.stop()
                console.print("\n[yellow]✋ Speech Stopped.[/yellow]")
                
            pygame.mixer.quit()
        else:
            os.system("mpg123 -q voice.mp3 > /dev/null 2>&1")
    except Exception as e:
        console.print(f"[red]Voice Error: {e}[/red]")