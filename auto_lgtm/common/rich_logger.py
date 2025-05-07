from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.text import Text
from rich.logging import RichHandler
import logging
from loguru import logger
import pyfiglet
import traceback
import sys
from contextlib import contextmanager

class RichLogger:
    def __init__(self):
        self.console = Console()
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        )
        
    def print_title(self, title: str, subtitle: str = None):
        """Print a fancy ASCII art title using Pyfiglet"""
        ascii_art = pyfiglet.figlet_format(title, font='shadow')
        
        panel = Panel(
            Text(ascii_art, style="bold blue") + 
            (Text(f"\n{subtitle}", style="cyan") if subtitle else Text("")),
            border_style="blue",
            expand=False
        )
        
        self.console.print(panel)
        self.console.print()

    def print_success(self, message: str):
        """Print a success message"""
        self.console.print(f"[green]✓[/green] {message}")

    def print_error(self, message: str):
        """Print an error message with traceback"""
        exc_type, exc_value, exc_traceback = sys.exc_info()
        if exc_traceback:
            frame = exc_traceback.tb_frame
            line_no = exc_traceback.tb_lineno
            file_name = frame.f_code.co_filename
            class_name = frame.f_locals.get('self', None).__class__.__name__ if 'self' in frame.f_locals else None
            
            error_details = f"[red]Error in {file_name}:{line_no}"
            if class_name:
                error_details += f" ({class_name})"
            error_details += f"\n{exc_type.__name__}: {str(exc_value)}[/red]"
            
            self.console.print(error_details)
            self.console.print("[yellow]Traceback:[/yellow]")
            for line in traceback.format_tb(exc_traceback):
                self.console.print(f"[yellow]{line}[/yellow]")
        else:
            self.console.print(f"[red]✗[/red] {message}")

    def print_warning(self, message: str):
        """Print a warning message"""
        self.console.print(f"[yellow]⚠[/yellow] {message}")

    def print_info(self, message: str):
        """Print an info message"""
        self.console.print(f"[blue]ℹ[/blue] {message}")

    @contextmanager
    def create_progress(self, description: str, total: int = 100):
        """Create a progress bar with a task"""
        task_id = self.progress.add_task(f"[cyan]{description}...", total=total)
        self.progress.start()
        try:
            yield self.progress, task_id
        finally:
            self.progress.stop()
            self.progress.remove_task(task_id)

    def print_table(self, title: str, columns: list, rows: list):
        """Print a table"""
        table = Table(title=title)
        for column in columns:
            table.add_column(column)
        for row in rows:
            table.add_row(*row)
        self.console.print(table) 