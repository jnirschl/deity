"""Module to rename an identifier in a filename with short hash."""
from pathlib import Path

import deity


def rename(filepath, dry_run=False, output_dir=None):
    """Accept filepath and return new filepath with encoded identifier."""
    filepath = Path(filepath).resolve()

    new_filename, _, _ = deity.encode_filename(filepath)

    # write to source directory if output_dir is not specified
    if output_dir is None:
        output_dir = filepath.parent

    new_filepath = output_dir.joinpath(new_filename)

    # rename file if dry_run is False
    if not dry_run:
        filepath.rename(new_filepath)

    return new_filepath
