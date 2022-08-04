import pytest
from deity import rename


@pytest.fixture()  # scope="session"
def filepath(tmpdir_factory):
    test_filename = "SHS-00-012345_part-A_cancer_40x_001.jpg"
    fn = tmpdir_factory.mktemp("data").join(test_filename)
    fn.write("")
    return fn


def test_rename(filepath):
    new_filename = rename(filepath)
    assert new_filename != filepath, AssertionError(
        f"New filename {filepath }is identical to input filename"
    )
