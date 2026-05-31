## 1. Taxonomy And Migration Matrix

- [x] 1.1 以 `stock` / `fund` / `bond` / `futures` 固化用户可见资产域，盘点并替换当前 `equity` 相关命令键、CLI 路径、帮助文案与测试基线。
- [x] 1.2 以 `.skill/efinance_cli/references/command-catalog.json` 为迁移矩阵，整理四个资产域与 `quote` / `market` / `resolve` / `search local` 的完整命令定义、参数和支持矩阵。
- [x] 1.3 明确 `search` / `watch` / `quote` / `market` / `resolve` 与四个资产域之间的边界，使 utility 入口与资产分类在帮助页中分离。

## 2. Command Catalog And CLI Tree

- [x] 2.1 重写 `efinance_cli/command_catalog.py`，用数据驱动方式补齐 `stock` 域全部目标命令，并把现有 `equity.*` 稳定键迁为 `stock.*`。
- [x] 2.2 扩展 `efinance_cli/command_catalog.py`，补齐 `fund` / `bond` / `futures` 域的完整命令面。
- [x] 2.3 扩展 `efinance_cli/command_catalog.py`，补齐 `quote` / `market` / `resolve` / `search local` 等 utility 入口。
- [x] 2.4 调整 `efinance_cli/commands.py` 的命令树装配与帮助页，确保完整命令面和新的 taxonomy 生效。

## 3. Provider Handlers And Support Matrix

- [x] 3.1 扩展 `efinance_cli/backends/providers.py`，为新增命令接入通用 efinance handler、参数映射和宽契约标准化。
- [x] 3.2 把现有双后端共享能力从 `equity.*` 迁移到 `stock.*`，并保留 `akshare` 的显式部分支持矩阵。
- [x] 3.3 调整 `efinance_cli/backends/factory.py` 与 `efinance_cli/backends/resolver.py`，确保新增命令和 provider-specific 扩展命令的 backend 语义一致。

## 4. Contracts, Observation And Execution

- [x] 4.1 扩展 `efinance_cli/contracts.py`，补齐通用记录、标量列表、标量值和 side-effect 状态等宽契约。
- [x] 4.2 调整 `efinance_cli/enrichment/service.py` 与 `efinance_cli/observation.py`，让 `stock.*` 命令键替代 `equity.*`，并让新增宽契约命令稳定落到 generic observation。
- [x] 4.3 复查统一执行骨架，确保批量命令、utility 命令和 side-effect 命令继续走同一主链。

## 5. Tests And Docs

- [x] 5.1 更新 CLI 回归测试，覆盖新的顶层命令树、帮助页、最小调用和 backend 冲突路径。
- [x] 5.2 更新 provider scaffold、contract、observation 与 enrichment 测试，验证 `stock.*` 命令键和新增命令族进入统一主链。
- [x] 5.3 更新架构文档、CLI 使用说明与相关设计文档，使其与完整命令面和新 taxonomy 保持一致。

## 6. Verification And Cleanup

- [x] 6.1 使用 `.venv\\Scripts\\python.exe -m pytest` 运行与命令迁移直接相关的测试集合，记录剩余风险。
- [x] 6.2 复查工作区与变更范围，确认本次迁移覆盖完整命令面而不是再次停留在局部共享命令。
