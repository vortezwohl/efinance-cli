## Context

当前仓库已经具备新的 command definition、request schema、backend resolver、provider handler、标准结果契约和统一执行骨架，但只验证了极少量共享命令。与此同时，项目内部已经有一份更完整、更接近最终产品面的参考目录 [`.skill/efinance_cli/references/command-catalog.json`](D:/Projects/PythonProjects/efinance-cli/.skill/efinance_cli/references/command-catalog.json)，其中明确了：

- 四个正式资产域：`stock` / `fund` / `bond` / `futures`
- utility 入口：`quote` / `market` / `resolve` / `search` / `watch`
- 每个命令的 CLI 路径、上游函数、参数名和帮助语义

这意味着本次工作不应继续“按感觉加几个命令”，而应把参考矩阵真正吸收到现有多后端骨架里。另一个现实约束是：本机 `.venv` 中可直接验证的是 `efinance`，`akshare` 包当前未安装，所以新增命令必须允许“完整命令面 + 部分 backend 支持矩阵”这一实现模型。

## Goals / Non-Goals

**Goals:**

- 让 `stock` / `fund` / `bond` / `futures` 成为唯一正式资产域，并移除 `equity` 的现行命令语义。
- 以 `command-catalog.json` 为迁移矩阵，把四个资产域和相关 utility 入口整体接入新 command catalog。
- 用数据驱动方式定义命令目录、请求 schema 和 provider handler 映射，避免为几十个命令编写分散的样板代码。
- 保持统一执行骨架不分叉，让批量命令、list 命令、profile 命令和带副作用命令都复用同一调用路径。
- 对 `akshare` 维持显式部分支持，其余命令通过支持矩阵和错误提示表达缺失，而不是让命令消失。

**Non-Goals:**

- 不要求本次把所有新增命令都做成双后端共享能力。
- 不把 `.skill/.../command-catalog.json` 作为运行时依赖文件直接读取；它只作为设计与实现参考矩阵。
- 不恢复旧的函数驱动注册层，也不重新引入 `common` / `utils` 这类旧顶层主入口。
- 不为每个命令发明完全独立的结果契约，优先复用一组可维护的契约族。

## Decisions

### 决策一：用户可见资产域与内部稳定命令键一起切换到 `stock.*`

这次不只修改 CLI 路径，而是同步把 `equity.price.history`、`equity.profile`、`equity.price.live` 等稳定命令键切换为 `stock.*`。原因很直接：如果用户看到的是 `stock`，而内部 key、observation 元信息、测试基线仍然长期写 `equity`，后续文档、调试与回归会持续泄漏旧语义。

替代方案：
- 只改 CLI 路径，不改命令键。
- 放弃原因：会制造长期双语义层，系统内部与用户表面持续分裂。

### 决策二：命令目录与 efinance handler 都采用数据驱动元数据表生成

`command-catalog.json` 已经把大量命令的路径、参数和上游函数映射整理好了。本次实现将把这些信息固化为仓库内的 Python 元数据表，再由辅助函数生成 `CommandDefinition`、`RequestSchema` 和对应的 efinance handler 注册，而不是在多个模块中手工散落几十份样板定义。

替代方案：
- 每个命令单独写一段 `CommandDefinition` 和一段 handler 类。
- 放弃原因：重复度高、易失配、维护成本过大，不适合一次性迁入几十个命令。

### 决策三：结果契约分层复用，通用列表命令使用宽契约兜底

不是所有命令都需要强结构化契约。本次按三层处理：

- 强契约：`stock.price.history`、`stock.price.live`、`stock.profile`、`fund.nav.history` 等继续走历史、实时、资料等标准契约，以支持 enrichment / observation。
- 通用记录契约：目录、资金流、成交、配置、龙虎榜、板块等 DataFrame 型结果统一标准化为 `list[dict]`，用宽记录契约承载，交给 generic observation/rendering。
- 标量与副作用契约：`resolve quote-id`、`fund reports download`、`market add`、`fund disclosure dates` 等使用标量列表、标量值或 side-effect 状态契约表达。

替代方案：
- 为所有命令新造专属契约。
- 放弃原因：契约数量会迅速失控，测试和渲染负担也会不成比例膨胀。

### 决策四：utility 入口进入命令目录，但不参与资产域 taxonomy

`quote` / `market` / `resolve` / `search` / `watch` 仍然保留，但它们是 utility 入口，不是资产域。命令树、帮助文本和提案文档必须把这点写清楚，否则用户会把 utility 与资产分类混为一谈。

替代方案：
- 为了减少范围，只迁四个资产域，utility 留待以后。
- 放弃原因：`command-catalog.json` 已明确给出这些入口的现行位置；若继续留空，目录仍然不完整。

### 决策五：`akshare` 保持显式部分支持，新增命令默认先落 efinance

在 `.venv` 里当前可验证的完整上游是 `efinance`。因此新增命令默认先作为 `efinance` 支持命令落地；只有现有已经接好的 `akshare` 能力继续保留双后端支持。对于不支持的新增命令，`--backend akshare` 必须给出明确冲突错误。

替代方案：
- 因为 `akshare` 未安装，所以延后整轮迁移。
- 放弃原因：命令面完整性不能被单个本地环境依赖阻塞，支持矩阵就是为这种差异设计的。

## Risks / Trade-offs

- [风险] 一次性迁入几十个命令，改动面会明显大于前几轮共享能力试点。  
  缓解：采用数据驱动元数据表和宽契约策略，减少分散样板与重复逻辑。

- [风险] `efinance` 某些返回形态并不统一，泛化标准化可能漏掉边缘类型。  
  缓解：保留强契约命令的专用标准化路径，其余命令使用 generic observation/rendering 兜底。

- [风险] `akshare` 本机未安装，无法对新增命令做真实双后端回归。  
  缓解：保留现有双后端命令测试，新增命令的 `akshare` 行为只通过支持矩阵与 resolver 错误路径覆盖。

- [风险] `search` 顶层默认调用与 `search local` 子命令并存，命令装配可能冲突。  
  缓解：保留现有顶层默认搜索逻辑，同时把 `search local` 作为子命令显式挂载。

## Migration Plan

1. 先补齐 OpenSpec proposal/design/specs/tasks，并把 `command-catalog.json` 固化为迁移矩阵来源。
2. 重写 `command_catalog.py`，以元数据表生成完整命令目录与新的 `stock.*` 稳定命令键。
3. 扩展 `providers.py`，把 efinance 通用 handler、宽契约标准化与现有 akshare handler 一起接入新命令目录。
4. 调整 `commands.py`、`resolver.py`、`contracts.py`、`observation.py`、`enrichment/service.py`，让新命令树与旧的增强/观测主链对齐。
5. 更新测试和文档，覆盖帮助页、命令存在性、最小调用、backend 冲突和 provider extension 迁移。
6. 运行定向测试集合，记录仍然只有部分 backend 支持的命令矩阵和剩余风险。

## Open Questions

- `stock.industry.boards` 这类 provider-specific 扩展是否要在命名上继续保留 “industry boards”，还是后续并入 `stock sector` 体系？当前实现先保留扩展路径，但统一到 `stock` 根组下。
- `quote` 入口是否最终要覆盖全部 `common` 历史能力，还是只保留高频查询子集？本次按 `command-catalog.json` 中现有条目先补齐已定义命令面。
