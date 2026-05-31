from __future__ import annotations

import unittest
from unittest.mock import patch

import click
from click.testing import CliRunner

from efinance_cli.backends.factory import list_provider_extension_commands
from efinance_cli.command_catalog import SHARED_COMMANDS
from efinance_cli.commands import create_root_command


def collect_leaf_paths(command: click.Command, prefix: tuple[str, ...] = ()) -> list[tuple[str, ...]]:
    if isinstance(command, click.Group):
        paths: list[tuple[str, ...]] = []
        for name, child in command.commands.items():
            paths.extend(collect_leaf_paths(child, prefix + (name,)))
        return paths
    return [prefix]


class CliFullRegressionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.cli = create_root_command()

    def test_root_help_exposes_new_taxonomy(self) -> None:
        result = self.runner.invoke(self.cli, ["--help"])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        for token in ("stock", "fund", "bond", "futures", "quote", "market", "resolve", "search", "watch"):
            self.assertIn(token, result.output)
        for token in ("equity", "akshare", "instrument"):
            self.assertNotIn(token, result.output)

    def test_leaf_inventory_matches_catalog_plus_extension_and_watch(self) -> None:
        actual = sorted(" ".join(path) for path in collect_leaf_paths(self.cli))
        expected = sorted(
            {
                "watch",
                *(
                    " ".join(command.cli_path)
                    for command in SHARED_COMMANDS
                    if command.command_key != "instrument.search"
                ),
                *(" ".join(command.cli_path) for command in list_provider_extension_commands()),
            }
        )
        self.assertEqual(actual, expected)
        self.assertGreater(len(actual), 40)

    def test_default_search_routes_to_instrument_search(self) -> None:
        captured: list[dict[str, object]] = []

        def fake_run(self, request):  # noqa: ANN001
            captured.append(
                {
                    "path": request.spec.cli_path,
                    "command_key": request.command_definition.command_key,
                    "kwargs": dict(request.kwargs),
                }
            )

        with patch("efinance_cli.executor.CommandExecutor.run", new=fake_run):
            result = self.runner.invoke(self.cli, ["search", "--query", "AAPL"])

        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertEqual(captured[0]["path"], ("search",))
        self.assertEqual(captured[0]["command_key"], "instrument.search")
        self.assertEqual(captured[0]["kwargs"]["keyword"], "AAPL")

    def test_representative_commands_route_through_executor(self) -> None:
        captured: list[dict[str, object]] = []
        commands = [
            (["stock", "price", "history", "--symbols", "000001"], "stock.price.history", "efinance"),
            (["fund", "nav", "history", "--symbol", "161725"], "fund.nav.history", "efinance"),
            (["fund", "nav", "history-batch", "--symbols", "161725", "--symbols", "110022"], "fund.nav.history-batch", "efinance"),
            (["bond", "catalog"], "bond.catalog", "efinance"),
            (["futures", "price", "live"], "futures.price.live", "efinance"),
            (["quote", "price", "latest", "--quote-ids", "1.000001"], "quote.price.latest", "efinance"),
            (["market", "price", "live", "--market", "m:105+t:3"], "market.price.live", "efinance"),
            (["resolve", "quote-id", "--symbol", "000001"], "resolve.quote-id", "efinance"),
            (["search", "local", "--query", "AAPL"], "search.local", "efinance"),
        ]

        def fake_run(self, request):  # noqa: ANN001
            captured.append(
                {
                    "path": request.spec.cli_path,
                    "command_key": request.command_definition.command_key,
                    "backend": request.backend_selection.resolved.value,
                    "kwargs": dict(request.kwargs),
                }
            )

        with patch("efinance_cli.executor.CommandExecutor.run", new=fake_run):
            for args, _, _ in commands:
                result = self.runner.invoke(self.cli, args)
                self.assertEqual(result.exit_code, 0, msg=f"{args}: {result.output}")

        self.assertEqual(len(captured), len(commands))
        for item, (_, command_key, backend) in zip(captured, commands, strict=False):
            self.assertEqual(item["command_key"], command_key)
            self.assertEqual(item["backend"], backend)

    def test_provider_extension_routes_to_default_backend(self) -> None:
        captured: list[dict[str, object]] = []

        def fake_run(self, request):  # noqa: ANN001
            captured.append(
                {
                    "path": request.spec.cli_path,
                    "command_key": request.command_definition.command_key,
                    "backend": request.backend_selection.resolved.value,
                }
            )

        with patch("efinance_cli.executor.CommandExecutor.run", new=fake_run):
            result = self.runner.invoke(self.cli, ["stock", "industry", "boards"])

        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertEqual(captured[0]["path"], ("stock", "industry", "boards"))
        self.assertEqual(captured[0]["command_key"], "akshare.industry.boards")
        self.assertEqual(captured[0]["backend"], "akshare")

    def test_provider_extension_rejects_wrong_backend(self) -> None:
        result = self.runner.invoke(
            self.cli,
            ["stock", "industry", "boards", "--backend", "efinance"],
        )
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("仅支持 backend: akshare", result.output)
        self.assertIn("默认会路由到 'akshare'", result.output)

    def test_required_schema_fields_fail_readably(self) -> None:
        result = self.runner.invoke(self.cli, ["stock", "price", "history"])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Missing option '--symbols'", result.output)

        result = self.runner.invoke(self.cli, ["fund", "nav", "history"])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Missing required option '--symbol'", result.output)


if __name__ == "__main__":
    unittest.main()
