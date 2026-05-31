## Why

`migrate-stock-fund-bond-futures-command-surface` 已经把完整命令面迁入当前 CLI，但很多命令仍然只是“可路由”，还不是“完整支持”：多资产 `history` 命令虽然存在，却没有与 `stock` 同等级的结果契约、enrichment / observation 支持、真实 backend 能力闭环与残留 `equity` 清理。现在必须补这一步，否则新命令目录仍然只是表面完整，运行时语义和用户预期会持续失配。

## What Changes

- 把“完整支持”的判定从“命令存在”升级为“命令在声明支持的 backend 上端到端可用”，尤其覆盖 `stock` / `fund` / `bond` / `futures` / `quote` 的 `history`、`live`、`profile` 与关键记录类命令。
- 为多资产 `history` 家族补齐真正稳定的标准化结果契约、enrichment 规则和 observation 输出，而不是继续让多数资产落在 generic 兜底路径。
- 清理 runtime、observation、测试和文档中残留的 `equity.*` 术语与键名，收口到 `stock.*`。
- 收紧 backend 支持矩阵语义：只有真正实现并验证通过的 backend 才能被声明为 supported；不完整实现不得靠“命令可路由”伪装成完整支持。
- 扩展定向回归，覆盖多资产 history/live/profile 主链、provider-specific 扩展命令、以及声明支持矩阵与真实实现的一致性。

## Capabilities

### New Capabilities
- `cross-asset-history-runtime-support`: 定义迁移后各资产 `history` 命令的完整运行时支持要求，包括标准化、增强、观察与真实 backend 调用闭环。
- `cross-asset-observation-parity`: 定义 `stock` / `fund` / `bond` / `futures` / `quote` 关键命令族的 observation / enrichment 一致性要求，避免只有股票主链拥有一等支持。
- `legacy-equity-runtime-removal`: 定义运行时、测试与文档中不得继续把 `equity.*` 作为现行稳定命令键或现行用户语义。

### Modified Capabilities
- `full-asset-domain-command-coverage`: 从“命令面完整”提升为“命令面完整且关键命令真正可用”。
- `backend-provider-architecture`: 修改支持矩阵要求，使 provider 只能为真实完整实现的 capability 声明支持。
- `backend-agnostic-execution-pipeline`: 修改统一执行骨架要求，使多资产 history/live/profile 命令进入专门主链，而不是长期停留在 generic 结果路径。
- `unified-result-contracts`: 扩展多资产 history、flow、trades、catalog、profile 与 side-effect 命令的契约要求。

## Impact

- 主要影响代码：
  - `efinance_cli/backends/providers.py`
  - `efinance_cli/contracts.py`
  - `efinance_cli/enrichment/service.py`
  - `efinance_cli/observation.py`
  - `efinance_cli/rendering.py`
  - `efinance_cli/command_catalog.py`
  - `tests/`
  - `docs/`
- 这次变更原则上不再引入新的用户可见命令路径，但可能会收紧不真实的支持矩阵声明，并修正文档与测试对“已完整支持”的定义。
