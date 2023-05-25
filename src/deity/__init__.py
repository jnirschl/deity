"""DeITy: De Identification Toolkit."""
__all__ = ["encode", "encode_single", "encode_single", "main"]
__version__ = "0.1.0"

from loguru import logger
from rich.console import Console
from rich.logging import RichHandler

from deity.__main__ import main
from deity.encode import encode
from deity.encode import encode_all
from deity.encode import encode_single


logger.configure(
    handlers=[
        {
            "sink": RichHandler(
                markup=True,
                level="INFO",
                console=Console(width=120, color_system="auto"),
            ),
            "format": "[blue]{function}[/blue]: {message}",
        }
    ]
)
