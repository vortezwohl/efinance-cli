## Why

当前多后端 CLI 只迁移了少量共享命令，用户可见命令面仍停留在半成品状态：股票入口还叫 `equity`，`bond` 与 `futures` 在现行命令树中缺席，`stock/fund/bond/futures` 之外的 `quote/market/resolve/search` 也没有按既定目录统一落到新骨架。现在必须一次性把命令目录迁完整，因为仓库里已经有明确的目标矩阵 [`.skill/efinance_cli/references/command-catalog.json`](D:/Projects/PythonProjects/efinance-cli/.skill/efinance_cli/references/command-catalog.json)，继续局部迁移只会让新架构长期处于“双语义、半覆盖、难维护”的状态。

## What Changes

- **BREAKING**：移除用户可见的 `equity` 资产分类，用 `stock` / `fund` / `bond` / `futures` 固化四个稳定资产域。
- **BREAKING**：按 `command-catalog.json` 的完整矩阵迁移四个资产域命令面，而不是只保留当前少量共享命令。
- 补齐 `quote` / `market` / `resolve` / `search local` 等 utility 入口，使其进入现有 command catalog 与统一执行骨架，但不把它们定义为资产分类。
- 扩展 `command_catalog.py`、request schema、backend 支持矩阵与帮助文案，使所有现行目标命令都通过显式命令定义暴露，而不再依赖旧函数驱动命名。
- 扩展 `efinance` provider handler 覆盖面，并保留 `akshare` 的显式部分支持矩阵；对不支持的后端返回明确冲突错误，而不是通过“命令不存在”掩盖差异。
- 扩展标准结果契约、标准化、observation / enrichment / rendering 接入，保证历史行情、实时行情、资料、目录、资金流、成交、配置、披露、报告与 side-effect 命令都能进入统一主链。
- 同步更新 CLI 回归测试、provider scaffold 测试、架构文档与使用说明，删除 `equity` 现行语义并恢复完整命令面。

## Capabilities

### New Capabilities
- `asset-domain-command-taxonomy`: 定义当前 CLI 的稳定资产域只能是 `stock` / `fund` / `bond` / `futures`，用户可见命令树不得再把 `equity` 作为正式资产分类。
- `full-asset-domain-command-coverage`: 定义四个资产域在当前多后端命令目录中的完整首批命令面，来源以 `command-catalog.json` 为准。
- `utility-entry-command-coverage`: 定义 `quote` / `market` / `resolve` / `search local` 等 utility 入口在新命令目录中的位置与边界。

### Modified Capabilities
- `command-capability-catalog`: 从当前局部共享命令目录扩展为覆盖资产域与 utility 入口的完整显式命令目录。
- `backend-provider-architecture`: 修改 provider 支持矩阵要求，使 provider 必须显式声明新增命令族的支持与不支持，而不是依赖命令缺席。
- `backend-agnostic-execution-pipeline`: 扩展统一执行骨架，使批量命令、side-effect 命令与 utility 命令继续走同一请求校验、backend 路由、标准化、增强与渲染主链。
- `provider-extension-commands`: 调整 provider-specific 扩展命令在迁移后命令树中的挂载语义，确保额外命令也进入稳定业务路径而不是退回 provider 根组。
- `unified-result-contracts`: 扩展结果契约覆盖面，使新增命令族可以按行情、资料、目录、记录列表、标量列表与 side-effect 状态稳定表达。

## Impact

- 主要影响代码：
  - `efinance_cli/command_catalog.py`
  - `efinance_cli/commands.py`
  - `efinance_cli/backends/providers.py`
  - `efinance_cli/backends/factory.py`
  - `efinance_cli/backends/resolver.py`
  - `efinance_cli/contracts.py`
  - `efinance_cli/enrichment/service.py`
  - `efinance_cli/observation.py`
  - `tests/`
  - `docs/`
- 这是一次显式 CLI 命令面迁移；旧的 `equity ...` 路径会失效并由 `stock ...` 取代。
- 不要求所有 backend 在所有命令上达到完全 parity，但要求现行 CLI 具备完整命令面，并通过支持矩阵诚实表达差异。
