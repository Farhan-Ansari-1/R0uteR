from rich.console import Console
from rich.panel import Panel
import random

console = Console()

def get_startup_message():
    messages = [
        "System Breach Detected... Welcome Boss.",
        "Neural Link Established. Ready to Hack.",
        "Establishing Secure Connection... Done.",
        "Protocol 0x99 Initiated. Waiting for Command.",
        "Mainframe Access Granted. Bolo kya karna hai?",
        "Security Shields Down. R0uteR is Online.",
        "Knowledge Database Loaded. Let's Learn.",
        "Connecting to the Matrix... Success."
    ]
    subtitles = [
        "[red]Red Team Mode[/red]",
        "[cyan]Learning Protocol[/cyan]",
        "[green]System: Online[/green]",
        "[yellow]Root Access: Granted[/yellow]"
    ]
    return random.choice(messages), random.choice(subtitles)

def print_banner():
    msg, sub = get_startup_message()
    console.print(Panel.fit(f"[bold green]👾 {msg}[/bold green]", border_style="green", subtitle=sub))