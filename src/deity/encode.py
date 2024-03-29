#!/usr/bin/env python3
"""encde.py in src/deity.

Helper functions to encode identifiers in a filename with an MD5 hash of the identifier.
"""
import hashlib
import re
from pathlib import Path
from typing import Optional
from typing import Union

import pandas as pd
from tqdm import tqdm

from deity.utils import DEFAULT_PATTERNS


def encode(text: str, num_chars: int = 16) -> tuple:
    """Accept identifier as string and return md5 hash of str identifier."""
    if not isinstance(text, str):
        raise TypeError(f"Requires 'str' input, but received {text}({type(text)})")

    # strip end chars and encode
    text = text.strip().encode()
    full_hash = hashlib.md5(text, usedforsecurity=False).hexdigest()
    short_hash = full_hash[:num_chars]

    return full_hash, short_hash


def encode_single(
    filepath: Union[str, Path],
    pattern: Union[str] = None,
    output_dir: Optional[str] = None,
    ignore_case=re.IGNORECASE,
    num_chars: int = 16,
) -> tuple:
    """Accept filepath and return new filepath with encoded identifier."""
    # create Path object
    filepath = Path(filepath).resolve()

    pattern = [pattern] if pattern and isinstance(pattern, str) else DEFAULT_PATTERNS

    # set output_dir to source filepath if not specified
    if output_dir is None or not Path(output_dir).exists():
        output_dir = filepath.parent
    else:
        output_dir = Path(output_dir)

    # compile regex to replace identifier
    for elem in pattern:
        pattern_regex = re.compile(elem, flags=ignore_case)

        match = pattern_regex.search(filepath.name)
        # break on first match
        if match:
            break

    identifier = match[0] if match else None

    if match:
        full_hash, short_hash = encode(identifier, num_chars=num_chars)
        new_filename = pattern_regex.sub(short_hash, filepath.name)
    else:
        new_filename = filepath
        full_hash, short_hash = None, None

    # create new filepath
    new_filepath = output_dir.joinpath(new_filename)

    return identifier, new_filepath, full_hash, short_hash


def encode_all(
    filepath_list: list,
    pattern: Optional[str] = None,
    output_dir: str = None,
    ignore_case: bool = re.IGNORECASE,
    num_chars: int = 16,
) -> pd.DataFrame:
    """Accept filepath and return new filepath with encoded identifier."""
    if not isinstance(filepath_list, list):
        raise TypeError(
            f"Requires 'list' input, but received {filepath_list} ({type(filepath_list)})"
        )

    # create Path objects
    filepath_list = [Path(filepath) for filepath in filepath_list]

    # empty list to store results
    id_list = []
    new_filepath_list = []
    full_hash_list = []
    short_hash_list = []
    for file in tqdm(filepath_list):
        specimen_id, new_filename, full_hash, short_hash = encode_single(
            file,
            pattern=pattern,
            output_dir=output_dir,
            ignore_case=ignore_case,
            num_chars=num_chars,
        )
        id_list.append(specimen_id)
        new_filepath_list.append(str(new_filename))
        full_hash_list.append(str(full_hash))
        short_hash_list.append(str(short_hash))

    return pd.DataFrame(
        {
            "identifier": id_list,
            "short_hash": short_hash_list,
            "full_hash": full_hash_list,
            "old_filepath": filepath_list,
            "new_filepath": new_filepath_list,
        }
    )
