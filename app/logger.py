import os
import sys
import logging
from io import StringIO
from rich.console import Console
from rich.logging import RichHandler

from app.config import AppConfig
from app.helper import Helper

class AppLogger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.config = AppConfig()
            self.logger = logging.getLogger(__name__)
            self.shell_console = Console()
            self.file_console = Console(file=StringIO(), force_terminal=True, record=True)

            self._initialized = True

    def text(self, text):
        self.shell_console.print(text)

        self.file_console.print(Helper.add_timestamp(text))
    
    def table(self, table):
        self.shell_console.print("\n")
        self.shell_console.print(table)
        self.shell_console.print("\n")

        self.file_console.print("\n")
        self.file_console.print(table)
        self.file_console.print("\n")
    
    def status(self, status, content):
        status_rich = status.replace("OK", "[bold green]OK[/bold green]").replace("ERR", "[bold red]ERR[/bold red]").replace("WARN", "[bold yellow]WARN[/bold yellow]")
        content_rich = "[white dim]" + content + "[/white dim]"
        text = status_rich + " " + content_rich
        
        sys.stdout.write("\033[F")
        sys.stdout.write("\033[50G")
        self.shell_console.print(text)

        self.file_console.print(Helper.add_timestamp(text) + "\n")
    
    def exception(self, text, e):
        self.shell_console.print(text)

        self.file_console.print(Helper.add_timestamp(text))
        self.file_console.print({str(e)})
    
    def save_log(self):

        log_file_name = f"log_{self.config.CORE_DATETIME}.ansi"
        log_file_path = os.path.join(self.config.APP_LOG_PATH, log_file_name)

        with open(log_file_path, "w") as f:
            f.write(self.file_console.export_text(styles=True))
