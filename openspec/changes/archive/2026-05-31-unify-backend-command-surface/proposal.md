## Why

当前多后端架构已经把共享命令与 provider handler 解耦，但 CLI 表面仍然暴露了顶层 `akshare` 命令组。这让“命令语义”和“后端来源”同时出现在命令树里，违背了 `--backend` 作为统一后端入口的设计目标，也会让用户误以为 provider 名称本身是一级业务命令。

现在收敛这层语义是必要的，因为仓库已经具备统一 backend 解析、支持矩阵校验和 provider-specific 默认路由能力；继续保留顶层 provider 根组，只会把已经完成一半的抽象重新泄漏到用户入口层。

## What Changes

- **BREAKING**：移除顶层 provider 根命令组，不再把 `akshare` 这类 backend 名称直接暴露为一级 CLI 命令。
- 调整 provider-specific 扩展命令的挂载方式，使其进入稳定的业务语义命令树，而不是进入 provider 自身命令树。
- 保留 provider-specific 扩展命令的专属 backend 约束，但统一通过 `--backend` 表达后端选择语义。
- 明确 provider-specific 扩展命令的默认 backend 路由规则：命令支持矩阵仅包含一个 backend 时，用户可以省略 `--backend`，系统自动解析到该 backend。
- 调整 backend 冲突报错文案，使其不仅拒绝错误 backend，还明确提示该命令已默认路由到哪个 backend，以及用户不应如何调用。
- 同步更新帮助文本、CLI 回归测试和架构文档，删除把 provider 根组描述为现行命令面的内容。

## Capabilities

### New Capabilities

无。

### Modified Capabilities

- `provider-extension-commands`: 修改 provider-specific 扩展命令的可见性规则，不再要求以 provider 顶层命令组暴露。
- `backend-provider-architecture`: 修改运行时 backend 解析要求，补充“单 backend 扩展命令的默认路由”和“错误 backend 的指导式报错”语义。
- `backend-agnostic-execution-pipeline`: 修改扩展命令挂载后的统一执行要求，确保命令树收敛后仍走同一执行骨架与 watch 路径。

## Impact

- 主要影响代码：
  - `efinance_cli/commands.py`
  - `efinance_cli/backends/resolver.py`
  - `efinance_cli/backends/providers.py`
  - `efinance_cli/backends/factory.py`
  - `tests/test_cli_full_regression.py`
  - `docs/cli-设计与使用说明.md`
  - `docs/架构设计说明.md`
- 这是一次显式 CLI 语义收敛，属于破坏性命令面调整；现有 `efinance akshare ...` 用法会失效并迁移到新的业务语义路径。
- 不引入新的运行时依赖，也不改变现有 provider handler、结果契约和执行器主链。
