import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from stashenv.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_save_reads_env_file_and_saves_profile(runner, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_bytes(b"KEY=value\nFOO=bar\n")

    with patch("stashenv.cli.save_profile") as mock_save:
        result = runner.invoke(
            cli,
            ["save", "dev", "--password", "secret", "--env-file", str(env_file)],
        )
        assert result.exit_code == 0
        assert "Profile 'dev' saved" in result.output
        mock_save.assert_called_once_with("dev", b"KEY=value\nFOO=bar\n", "secret")


def test_save_missing_env_file_exits_nonzero(runner, tmp_path):
    result = runner.invoke(
        cli,
        ["save", "dev", "--password", "secret", "--env-file", str(tmp_path / "missing.env")],
    )
    assert result.exit_code != 0
    assert "not found" in result.output


def test_load_writes_env_file(runner, tmp_path):
    out_file = tmp_path / ".env"

    with patch("stashenv.cli.load_profile", return_value=b"KEY=value\n") as mock_load:
        result = runner.invoke(
            cli,
            ["load", "dev", "--password", "secret", "--env-file", str(out_file)],
        )
        assert result.exit_code == 0
        assert "loaded" in result.output
        mock_load.assert_called_once_with("dev", "secret")
        assert out_file.read_bytes() == b"KEY=value\n"


def test_load_wrong_password_exits_nonzero(runner, tmp_path):
    with patch("stashenv.cli.load_profile", side_effect=ValueError("bad password")):
        result = runner.invoke(
            cli,
            ["load", "dev", "--password", "wrong", "--env-file", str(tmp_path / ".env")],
        )
        assert result.exit_code != 0
        assert "wrong password" in result.output


def test_load_missing_profile_exits_nonzero(runner, tmp_path):
    with patch("stashenv.cli.load_profile", side_effect=FileNotFoundError):
        result = runner.invoke(
            cli,
            ["load", "ghost", "--password", "x", "--env-file", str(tmp_path / ".env")],
        )
        assert result.exit_code != 0
        assert "does not exist" in result.output


def test_list_shows_profiles(runner):
    with patch("stashenv.cli.list_profiles", return_value=["dev", "prod"]):
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "dev" in result.output
        assert "prod" in result.output


def test_list_empty(runner):
    with patch("stashenv.cli.list_profiles", return_value=[]):
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "No profiles" in result.output


def test_delete_profile(runner):
    with patch("stashenv.cli.delete_profile") as mock_del:
        result = runner.invoke(cli, ["delete", "dev", "--yes"])
        assert result.exit_code == 0
        assert "deleted" in result.output
        mock_del.assert_called_once_with("dev")
