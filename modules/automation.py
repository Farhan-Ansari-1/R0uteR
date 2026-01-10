import os
from rich.panel import Panel
from modules.ui import console

def execute_command(command):
    console.print(Panel(f"[bold yellow]⚙️ Executing Command:[/bold yellow] {command}", border_style="yellow"))
    try:
        # Security Check
        if "rm -rf" in command or "format" in command or "del /" in command or "rd /" in command:
            console.print("[bold red]⚠️ Command Blocked (Safety Protocol).[/bold red]")
            return
        os.system(command)
    except KeyboardInterrupt:
        console.print("\n[bold red]⚠️ Command Stopped by User (R0uteR is still alive).[/bold red]")
    except Exception as e:
        console.print(f"[bold red]❌ Execution Error:[/bold red] {e}")