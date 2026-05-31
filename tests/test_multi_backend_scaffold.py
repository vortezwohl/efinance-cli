from __future__ import annotations

import unittest
from unittest.mock import patch

import pandas as pd

from efinance_cli.backends.factory import get_backend_provider, list_backend_providers
from efinance_cli.command_catalog import (
    SHARED_COMMANDS,
    get_capability_descriptor,
    get_command_definition,
    get_shared_command_definition,
    get_single_backend_command_definitions,
)
from efinance_cli.facade import CommandFacade
from efinance_cli.models import BackendName, BackendSelection


class MultiBackendScaffoldTest(unittest.TestCase):
    def test_shared_catalog_only_contains_multi_backend_commands(self) -> None:
        self.assertTrue(SHARED_COMMANDS)
        for definition in SHARED_COMMANDS:
            self.assertEqual(definition.kind.value, "shared")
            self.assertGreaterEqual(len(definition.supported_backends), 2)

    def test_single_backend_commands_are_provider_extensions(self) -> None:
        definitions = get_single_backend_command_definitions()
        self.assertTrue(definitions)
        for definition in definitions:
            self.assertEqual(definition.kind.value, "provider-extension")
            self.assertEqual(len(definition.supported_backends), 1)
            self.assertEqual(definition.provider_name, definition.supported_backends[0])

    def test_stock_capabilities_replace_equity_in_shared_catalog(self) -> None:
        history = get_shared_command_definition("stock.price.history")
        live = get_shared_command_definition("stock.price.live")
        profile = get_shared_command_definition("stock.profile")

        self.assertEqual(history.cli_path, ("stock", "price", "history"))
        self.assertEqual(live.cli_path, ("stock", "price", "live"))
        self.assertEqual(profile.cli_path, ("stock", "profile"))
        self.assertEqual(
            tuple(item.value for item in history.supported_backends),
            ("efinance", "akshare"),
        )

    def test_capability_descriptor_exposes_contracts(self) -> None:
        descriptor = get_capability_descriptor("stock.price.history")
        self.assertEqual(descriptor.result_contract, "history-bars")
        self.assertEqual(get_capability_descriptor("fund.nav.history").result_contract, "fund-nav-history")
        self.assertEqual(get_capability_descriptor("resolve.quote-id").result_contract, "scalar-value")

    def test_provider_registry_exposes_full_command_surface(self) -> None:
        registry = list_backend_providers()
        self.assertEqual(set(registry), {BackendName.EFINANCE, BackendName.AKSHARE})
        self.assertTrue(get_backend_provider(BackendName.EFINANCE).supports("stock.price.live"))
        self.assertTrue(get_backend_provider(BackendName.EFINANCE).supports("bond.catalog"))
        self.assertTrue(get_backend_provider(BackendName.EFINANCE).supports("resolve.quote-id"))
        self.assertTrue(get_backend_provider(BackendName.AKSHARE).supports("stock.price.history"))
        self.assertTrue(get_backend_provider(BackendName.AKSHARE).supports("akshare.industry.boards"))

    def test_provider_support_matrix_matches_declared_backends(self) -> None:
        efinance_provider = get_backend_provider(BackendName.EFINANCE)
        akshare_provider = get_backend_provider(BackendName.AKSHARE)

        for definition in (
            get_shared_command_definition("stock.price.history"),
            get_shared_command_definition("stock.price.live"),
            get_shared_command_definition("stock.profile"),
            get_shared_command_definition("fund.nav.history"),
        ):
            self.assertEqual(
                efinance_provider.supports(definition.command_key),
                BackendName.EFINANCE in definition.supported_backends,
            )
            self.assertEqual(
                akshare_provider.supports(definition.command_key),
                BackendName.AKSHARE in definition.supported_backends,
            )

        for definition in get_single_backend_command_definitions():
            self.assertEqual(
                efinance_provider.supports(definition.command_key),
                definition.provider_name == BackendName.EFINANCE,
            )
            self.assertEqual(
                akshare_provider.supports(definition.command_key),
                definition.provider_name == BackendName.AKSHARE,
            )

    def test_efinance_search_handler_returns_standard_result(self) -> None:
        quote = type("Quote", (), {"_asdict": lambda self: {"code": "AAPL", "name": "苹果", "quote_id": "AAPL", "classify": "US_stock"}})()
        definition = get_shared_command_definition("instrument.search")
        facade = CommandFacade()
        with patch("efinance.utils.search_quote", return_value=[quote]):
            result = facade.invoke(
                definition,
                BackendSelection(requested=None, resolved=BackendName.EFINANCE, source="default"),
                {"keyword": "AAPL", "market_type": None, "count": 5, "use_local": True},
            )
        self.assertEqual(result.contract_name, "search-results")
        self.assertEqual(result.data[0]["code"], "AAPL")

    def test_efinance_stock_history_handler_returns_standard_result(self) -> None:
        frame = pd.DataFrame(
            [
                {
                    "date": "2026-05-28",
                    "symbol": "000001",
                    "open": 10.0,
                    "close": 10.5,
                    "high": 10.6,
                    "low": 9.9,
                    "volume": 1000,
                }
            ]
        )
        definition = get_shared_command_definition("stock.price.history")
        facade = CommandFacade()
        with patch("efinance.stock.get_quote_history", return_value=frame):
            result = facade.invoke(
                definition,
                BackendSelection(requested=None, resolved=BackendName.EFINANCE, source="default"),
                {
                    "stock_codes": ["000001"],
                    "beg": "19000101",
                    "end": "20500101",
                    "klt": 101,
                    "fqt": 1,
                    "market_type": None,
                    "suppress_error": False,
                    "use_id_cache": True,
                },
            )
        self.assertEqual(result.contract_name, "history-bars")
        self.assertEqual(result.data[0]["symbol"], "000001")

    def test_efinance_stock_profile_handler_returns_standard_result(self) -> None:
        profile = pd.Series({"code": "000001", "name": "平安银行", "industry": "银行"})
        definition = get_shared_command_definition("stock.profile")
        facade = CommandFacade()
        with patch("efinance.stock.get_base_info", return_value=profile):
            result = facade.invoke(
                definition,
                BackendSelection(requested=None, resolved=BackendName.EFINANCE, source="default"),
                {"stock_codes": ["000001"]},
            )
        self.assertEqual(result.contract_name, "profile-info")
        self.assertEqual(result.data["code"], "000001")

    def test_efinance_fund_nav_history_handler_returns_standard_result(self) -> None:
        frame = pd.DataFrame(
            [
                {
                    "date": "2026-05-28",
                    "symbol": "161725",
                    "unit_nav": 1.23,
                    "accumulated_nav": 2.34,
                    "change_pct": 1.1,
                }
            ]
        )
        definition = get_shared_command_definition("fund.nav.history")
        facade = CommandFacade()
        with patch("efinance.fund.get_quote_history", return_value=frame):
            result = facade.invoke(
                definition,
                BackendSelection(requested=None, resolved=BackendName.EFINANCE, source="default"),
                {"fund_code": "161725", "pz": 40000},
            )
        self.assertEqual(result.contract_name, "fund-nav-history")
        self.assertEqual(result.data[0]["symbol"], "161725")

    def test_efinance_fund_nav_history_batch_handler_returns_standard_result(self) -> None:
        payload = {
            "161725": pd.DataFrame(
                [
                    {
                        "date": "2026-05-28",
                        "symbol": "161725",
                        "unit_nav": 1.23,
                        "accumulated_nav": 2.34,
                    }
                ]
            ),
            "110022": pd.DataFrame(
                [
                    {
                        "date": "2026-05-28",
                        "symbol": "110022",
                        "unit_nav": 2.23,
                        "accumulated_nav": 3.34,
                    }
                ]
            ),
        }
        definition = get_command_definition("fund.nav.history-batch")
        facade = CommandFacade()
        with patch("efinance.fund.get_quote_history_multi", return_value=payload):
            result = facade.invoke(
                definition,
                BackendSelection(requested=None, resolved=BackendName.EFINANCE, source="default"),
                {"fund_codes": ["161725", "110022"], "pz": 40000},
            )
        self.assertEqual(result.contract_name, "fund-nav-history")
        self.assertEqual(sorted(result.data), ["110022", "161725"])
        self.assertEqual(result.data["161725"][0]["symbol"], "161725")

    def test_efinance_bond_history_handler_returns_standard_result(self) -> None:
        frame = pd.DataFrame(
            [
                {
                    "债券代码": "113519",
                    "日期": "2026-05-28",
                    "开盘": 101.0,
                    "收盘": 101.5,
                    "最高": 102.0,
                    "最低": 100.8,
                }
            ]
        )
        definition = get_command_definition("bond.price.history")
        facade = CommandFacade()
        with patch("efinance.bond.get_quote_history", return_value=frame):
            result = facade.invoke(
                definition,
                BackendSelection(requested=None, resolved=BackendName.EFINANCE, source="default"),
                {
                    "bond_codes": ["113519"],
                    "beg": "19000101",
                    "end": "20500101",
                    "klt": 101,
                    "fqt": 1,
                },
            )
        self.assertEqual(result.contract_name, "history-bars")
        self.assertEqual(result.data[0]["symbol"], "113519")

    def test_efinance_quote_profile_handler_returns_standard_result(self) -> None:
        profile = pd.Series({"quote_id": "1.000001", "name": "平安银行", "market": "A_stock"})
        definition = get_command_definition("quote.profile")
        facade = CommandFacade()
        with patch("efinance.common.get_base_info", return_value=profile):
            result = facade.invoke(
                definition,
                BackendSelection(requested=None, resolved=BackendName.EFINANCE, source="default"),
                {"quote_id": "1.000001"},
            )
        self.assertEqual(result.contract_name, "profile-info")
        self.assertEqual(result.data["code"], "1.000001")

    def test_efinance_quote_latest_handler_uses_quote_market_default(self) -> None:
        frame = pd.DataFrame(
            [
                {
                    "代码": "1.000001",
                    "名称": "平安银行",
                    "最新价": 10.5,
                }
            ]
        )
        definition = get_command_definition("quote.price.latest")
        facade = CommandFacade()
        with patch("efinance.common.get_latest_quote", return_value=frame):
            result = facade.invoke(
                definition,
                BackendSelection(requested=None, resolved=BackendName.EFINANCE, source="default"),
                {"quote_id_list": ["1.000001"]},
            )
        self.assertEqual(result.contract_name, "realtime-quotes")
        self.assertEqual(result.data[0]["market"], "quote")

    def test_efinance_stock_live_handler_returns_standard_result(self) -> None:
        frame = pd.DataFrame(
            [
                {
                    "symbol": "000001",
                    "name": "平安银行",
                    "close": 10.5,
                    "open": 10.2,
                    "high": 10.6,
                    "low": 10.1,
                    "volume": 12345,
                    "turnover": 67890.0,
                    "change_pct": 1.2,
                }
            ]
        )
        definition = get_shared_command_definition("stock.price.live")
        facade = CommandFacade()
        with patch("efinance.stock.get_realtime_quotes", return_value=frame):
            result = facade.invoke(
                definition,
                BackendSelection(requested=None, resolved=BackendName.EFINANCE, source="default"),
                {"fs": ()},
            )
        self.assertEqual(result.contract_name, "realtime-quotes")
        self.assertEqual(result.data[0]["symbol"], "000001")

    def test_akshare_extension_path_moves_under_stock_root(self) -> None:
        provider = get_backend_provider(BackendName.AKSHARE)
        definition = provider.extension_commands[0]
        self.assertEqual(definition.command_key, "akshare.industry.boards")
        self.assertEqual(definition.cli_path, ("stock", "industry", "boards"))
        self.assertEqual(definition.kind.value, "provider-extension")
        self.assertEqual(definition.provider_name, BackendName.AKSHARE)


if __name__ == "__main__":
    unittest.main()
