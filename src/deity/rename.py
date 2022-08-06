from pathlib import Path

import deity


def rename(filepath, dry_run=False, output_dir=None):
    filepath = Path(filepath).resolve()

    new_filename, _, _ = deity.encode_filename(filepath)

    if output_dir:
        new_filepath = filepath.parents[0].joinpath(new_filename)
        filepath.rename(new_filepath)
    else:
        new_filepath = filepath.parents[0].joinpath(new_filename)
        filepath.rename(new_filepath)

    return new_filepath
