"""Module to encode an identifier in a filename with short hash."""
import hashlib
import re
from pathlib import Path

import pandas as pd


def encode(text, num_chars: int = 16):
    """Accept identifier as string and return SHA-256 hash of str identifier."""
    if type(text) is not str:
        raise TypeError(f"Requires 'str' input, but received {text}({type(text)})")

    # strip end chars and encode
    text = text.strip().encode()
    full_hash = hashlib.sha256(text).hexdigest()
    short_hash = full_hash[0:num_chars]

    return full_hash, short_hash


def encode_single(
    filepath: str,
    pattern: str = "[SL][HP][SDFNA]-\\d{2}-\\d{5}",
    ignore_case=re.IGNORECASE,
    num_chars: int = 16,
):
    """Accept filepath and return new filepath with encoded identifier."""
    filepath = Path(filepath).resolve()

    # compile regex to replace identifier
    pattern_regex = re.compile(pattern, ignore_case)

    # get identifier
    match = pattern_regex.search(filepath.name)
    if match:
        full_hash, short_hash = encode(match[0], num_chars=num_chars)
        new_filename = pattern_regex.sub(short_hash, filepath.name)
    else:
        new_filename = filepath
        full_hash, short_hash = None, None

    return new_filename, full_hash, short_hash


def encode_all(
    filepath_list: list,
    pattern: str = "[SL][HP][SDFNA]-\\d{2}-\\d{5}",
    ignore_case=re.IGNORECASE,
    num_chars: int = 16,
):
    """Accept filepath and return new filepath with encoded identifier."""
    new_filename_list = []
    full_hash_list = []
    short_hash_list = []
    for file in filepath_list:
        new_filename, full_hash, short_hash = encode_single(
            file, pattern, ignore_case, num_chars
        )
        new_filename_list.append(new_filename)
        full_hash_list.append(full_hash)
        short_hash_list.append(short_hash)

    return pd.DataFrame(
        {
            "filename": new_filename_list,
            "full_hash": full_hash_list,
            "short_hash": short_hash_list,
        }
    )
