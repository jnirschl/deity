from pathlib import Path

from deity import encode_filename


def rename(filepath, output_dir=None):
    filepath = Path(filepath).resolve()

    new_filename, _, _ = encode_filename(filepath)

    if output_dir:
        new_filepath = filepath.parents[0].joinpath(new_filename)
        filepath.rename(new_filepath)
    else:
        new_filepath = filepath.parents[0].joinpath(new_filename)
        filepath.rename(new_filepath)
