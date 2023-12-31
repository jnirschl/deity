"""DeITy: De Identification Toolkit."""
from importlib import metadata

from loguru import logger
from rich.console import Console
from rich.logging import RichHandler

from deity.encode import encode
from deity.encode import encode_all
from deity.encode import encode_single


__version__ = metadata.version(__package__)

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
del metadata  # optional, avoids polluting the results of dir(__package__)
