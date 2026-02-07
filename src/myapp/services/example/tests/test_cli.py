"""Tests for the example service CLI wiring."""

from click.testing import CliRunner

from myapp.cli.main import cli


class TestExampleCLI:
    def test_svc_example_list(self, tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
        """``project svc example list`` should run without error."""
        monkeypatch.setenv("MYAPP_DB_DIR", str(tmp_path))
        runner = CliRunner()
        result = runner.invoke(cli, ["svc", "example", "list", "--backend", "json"])
        assert result.exit_code == 0

    def test_svc_example_add_and_list(self, tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
        monkeypatch.setenv("MYAPP_DB_DIR", str(tmp_path))
        runner = CliRunner()
        # add an item
        result = runner.invoke(
            cli, ["svc", "example", "add", "--name", "CliTest", "--backend", "json"]
        )
        assert result.exit_code == 0
        assert "Created:" in result.output

    def test_svc_example_schema(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["svc", "example", "schema"])
        assert result.exit_code == 0
        assert "properties" in result.output

    def test_doctor_runs(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["doctor"])
        assert "Environment check" in result.output

    def test_version_flag(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert "0.1.0" in result.output
