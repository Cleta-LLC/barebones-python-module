"""Tests for the recipes service CLI wiring."""

from click.testing import CliRunner

from myapp.cli.main import cli


class TestRecipesCLI:
    def test_svc_recipes_list(self) -> None:
        """``project svc recipes list`` runs without error."""
        runner = CliRunner()
        result = runner.invoke(cli, ["svc", "recipes", "list", "--backend", "json"])
        assert result.exit_code == 0

    def test_svc_recipes_seed_and_list(self, tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
        runner = CliRunner()
        result = runner.invoke(cli, ["svc", "recipes", "seed", "--backend", "json"])
        assert result.exit_code == 0
        assert "recipe(s)" in result.output

    def test_svc_recipes_add(self) -> None:
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "svc",
                "recipes",
                "add",
                "--name",
                "Test Muffin",
                "--category",
                "pastry",
                "--prep",
                "10",
                "--cook",
                "25",
                "--servings",
                "12",
                "--backend",
                "json",
            ],
        )
        assert result.exit_code == 0
        assert "Created:" in result.output

    def test_svc_recipes_schema(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["svc", "recipes", "schema"])
        assert result.exit_code == 0
        assert "properties" in result.output

    def test_svc_recipes_search(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["svc", "recipes", "search", "bread", "--backend", "json"])
        assert result.exit_code == 0

    def test_svc_discovered(self) -> None:
        """Recipes service is auto-discovered by the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli, ["svc", "--help"])
        assert "recipes" in result.output
