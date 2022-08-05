import hashlib
import re
from pathlib import Path


def encode(text, num_chars: int = 16):
    """accept identifier as string and return SHA-256 hash of str identifier"""
    if type(text) is not str:
        raise TypeError(
            f"Requires 'str' input, but received {text}({type(text)})"
        )

    # strip end chars and encode
    text = text.strip().encode()
    full_hash = hashlib.sha256(text).hexdigest()
    short_hash = full_hash[0:num_chars]

    return full_hash, short_hash


def encode_filename(
    filepath: str,
    pattern: str = "[SL][HP][SDFNA]-\d{2}-\d{5}",
    ignore_case=re.IGNORECASE,
):
    """ """
    filepath = Path(filepath).resolve()

    # compile regex to replace identifier
    pattern_regex = re.compile(pattern, ignore_case)

    # get identifier
    match = pattern_regex.search(filepath.name)
    if match:
        full_hash, short_hash = encode(match[0])
        new_filename = pattern_regex.sub(short_hash, filepath.name)
    else:
        new_filename = filepath
        full_hash, short_hash = None, None

    return new_filename, full_hash, short_hash
