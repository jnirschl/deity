"""DeITy: De Identification Toolkit."""
__all__ = ["encode", "encode_single", "encode_single", "main"]
__version__ = "0.1.0"

from deity.__main__ import main
from deity.encode import encode
from deity.encode import encode_all
from deity.encode import encode_single
