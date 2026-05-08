"""Tests for cli_env_vars expand command."""

import pytest
from click.testing import CliRunner

from stashenv.cli_env_vars import vars_group
from stashenv.store import save_profile


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def store(tmp_path):
    return tmp_path


def _invoke(runner, store, profile, password="secret", extra_args=()):
    return runner.invoke(
        vars_group,
        ["expand", profile, "--password", password, "--store", str(store), *extra_args],
    )


def test_expand_cmd_prints_key_values(runner, store):
    save_profile("dev", "HOST=localhost\nPORT=5432", "secret", store)
    result = _invoke(runner, store, "dev")
    assert result.exit_code == 0
    assert "HOST=localhost" in result.output
    assert "PORT=5432" in result.output


def test_expand_cmd_resolves_references(runner, store):
    save_profile("dev", "HOST=db\nURL=${HOST}/app", "secret", store)
    result = _invoke(runner, store, "dev")
    assert result.exit_code == 0
    assert "URL=db/app" in result.output


def test_expand_cmd_context_override(runner, store):
    save_profile("dev", "URL=${HOST}/app", "secret", store)
    result = _invoke(runner, store, "dev", extra_args=["--set", "HOST=override.com"])
    assert result.exit_code == 0
    assert "URL=override.com/app" in result.output


def test_expand_cmd_warns_on_unresolved(runner, store):
    save_profile("dev", "URL=${GHOST}", "secret", store)
    result = _invoke(runner, store, "dev")
    assert result.exit_code == 0
    assert "GHOST" in result.output


def test_expand_cmd_strict_exits_nonzero_on_unresolved(runner, store):
    save_profile("dev", "URL=${GHOST}", "secret", store)
    result = _invoke(runner, store, "dev", extra_args=["--strict"])
    assert result.exit_code != 0


def test_expand_cmd_missing_profile_exits_nonzero(runner, store):
    result = _invoke(runner, store, "nonexistent")
    assert result.exit_code != 0


def test_expand_cmd_wrong_password_exits_nonzero(runner, store):
    save_profile("dev", "KEY=val", "correct", store)
    result = _invoke(runner, store, "dev", password="wrong")
    assert result.exit_code != 0


def test_expand_cmd_bad_set_flag_exits_nonzero(runner, store):
    save_profile("dev", "KEY=val", "secret", store)
    result = _invoke(runner, store, "dev", extra_args=["--set", "NOEQUALS"])
    assert result.exit_code != 0
