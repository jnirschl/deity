"""DeITy: De Identification Toolkit."""
__version__ = "0.0.1"
__all__ = ["encode", "encode_single", "main"]

from .__main__ import main
from .encode import encode
from .encode import encode_single
