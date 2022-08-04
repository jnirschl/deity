import pytest
from click.testing import CliRunner

import deity
from deity import main, encode


@pytest.fixture()
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


@pytest.fixture()
def test_filename():
    return "SHS-00-012345_part-A_cancer_40x_001.jpg"


@pytest.fixture()  # scope="session"
def tmp_file(tmpdir_factory, test_filename):
    test_filename = "SHS-00-012345_part-A_cancer_40x_001.jpg"
    fn = tmpdir_factory.mktemp("data").join(test_filename)
    fn.write("")
    return fn


# @pytest.mark.skipif(
#     deity.__version__ < "0.2.0", reason="not supported until version 0.2.0"
# )
@pytest.mark.smoke
class TestMain:
    def test_success(self, runner: CliRunner, tmp_file) -> None:
        """It exits with a status code of zero."""
        result = runner.invoke(main, ["./"])
        assert tmp_file.exists()
        assert result.exit_code == 0

    def test_fail(self, runner: CliRunner) -> None:
        """It exits with a status code of zero."""
        result = runner.invoke(main, [""])
        assert result.exit_code == 2
