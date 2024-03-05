#!/usr/bin/env python3
"""test_utils.py in tests."""
# sourcery skip: no-loop-in-tests
import random
from pathlib import Path
from typing import List

import pandas as pd

from deity.utils import find_existing_file
from deity.utils import get_file_list
from deity.utils import rename_files


def test_get_file_list(temp_dir: str, test_files: str, suffix_list: str):  # temp_dir_with_files
    input_dir = Path(temp_dir)
    extension = ",".join(suffix_list)
    suffix_list = [f".{ext}" for ext in suffix_list]

    # Test for extensions (randomly selected)
    result = get_file_list(input_dir, extension=extension)
    expected = [
        input_dir.joinpath(f).as_posix() for f in test_files if Path(f).suffix in suffix_list
    ]
    assert result is not None
    assert sorted(result) == sorted(expected)


def test_rename_files(temp_dir: str, test_files: str):
    input_dir = Path(temp_dir)

    # Prepare a sample DataFrame for renaming
    df_file_rename = pd.DataFrame(
        {
            "old_filepath": [
                input_dir.joinpath(test_files[0]),
                input_dir.joinpath(test_files[1]),
                input_dir.joinpath(test_files[2]),
            ],
            "new_filepath": [
                input_dir.joinpath(test_files[0] + "_renamed"),
                input_dir.joinpath(test_files[1] + "_renamed"),
                input_dir.joinpath(test_files[2] + "_renamed"),
            ],
        }
    )

    # Rename the files
    rename_files(df_file_rename)

    # Check if the renamed files exist and original files are removed
    for _index, row in df_file_rename.iterrows():
        assert not row["old_filepath"].exists()
        assert row["new_filepath"].exists()


def test_find_existing_file(temp_dir: str, suffix_list: List[str], test_files: List[str]):
    """Test find_existing_file function."""
    # Use temp_dir and test_files fixtures to create a test environment
    base_path = Path(temp_dir)
    image_suffix_list = {"bmp", "gif", "jp2", "webp", "psd", "raw", "eps", "wmb"}
    different_suffix = list(set(suffix_list).symmetric_difference(image_suffix_list))

    # Test cases
    for file_name in test_files:
        input_file = base_path.joinpath(file_name)
        target_suffix = file_name.split(".")[-1]

        # Change the file extension to one that is not in the suffix_list
        while target_suffix in suffix_list:
            target_suffix = random.choice(different_suffix)

        input_file_with_diff_extension = input_file.with_suffix(f".{target_suffix}")

        # Check if the function can find the correct file with the existing extension
        found_file = find_existing_file(input_file_with_diff_extension, ",".join(suffix_list))
        assert found_file == input_file

        # Check if the function returns the input file unchanged if it doesn't exist
        non_existent_file = base_path.joinpath(
            f"non_existent_file.{random.choice(different_suffix)}"
        )
        assert find_existing_file(non_existent_file, ",".join(suffix_list)) == non_existent_file
