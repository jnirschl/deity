#!/usr/bin/env python3
"""test_utils.py in tests."""
from pathlib import Path

import pandas as pd

from deity.__main__ import get_file_list
from deity.__main__ import rename_files


def test_get_file_list(
    temp_dir: str, test_files: str, suffix_list: str
):  # temp_dir_with_files
    input_dir = Path(temp_dir)
    extension = ",".join(suffix_list)
    suffix_list = [f".{ext}" for ext in suffix_list]

    # Test for extensions (randomly selected)
    result = get_file_list(input_dir, extension=extension)
    expected = [
        input_dir.joinpath(f).as_posix()
        for f in test_files
        if Path(f).suffix in suffix_list
    ]
    assert result is not None
    assert sorted(result) == sorted(expected)


def test_rename_files(temp_dir: str, test_files: str):
    input_dir = Path(temp_dir)

    # Prepare a sample DataFrame for renaming
    df_file_rename = pd.DataFrame(
        {
            "old_filepath": [
                input_dir / test_files[0],
                input_dir / test_files[1],
                input_dir / test_files[2],
            ],
            "new_filepath": [
                input_dir / (test_files[0] + "_renamed"),
                input_dir / (test_files[1] + "_renamed"),
                input_dir / (test_files[2] + "_renamed"),
            ],
        }
    )

    # Rename the files
    rename_files(df_file_rename)

    # Check if the renamed files exist and original files are removed
    for _index, row in df_file_rename.iterrows():
        assert not row["old_filepath"].exists()
        assert row["new_filepath"].exists()
