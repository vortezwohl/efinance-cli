## Context

当前仓库已经具备多后端命令目录、provider 注册表、统一 backend 解析和统一执行骨架，但 provider-specific 扩展命令仍然以顶层 provider 根组挂载。例如 `akshare.industry.boards` 当前通过 `efinance akshare industry boards` 暴露，这让 CLI 同时表达了两层不同语义：

1. 顶层命令树表达业务动作，例如 `search`、`watch`、`equity`、`fund`。
2. 顶层命令树又表达 backend 来源，例如 `akshare`。

这种混排会直接破坏“命令面只暴露稳定业务语义，backend 统一由 `--backend` 控制”的设计目标。另一方面，现有 runtime 已经具备本次收敛所需的关键能力：

- shared 命令与 provider-extension 命令都走同一执行骨架；
- backend 支持矩阵校验已经存在；
- provider-extension 命令在未显式传入 `--backend` 时，已经可以默认解析到所属 provider。

因此这次设计不需要再引入新抽象，而是把现有能力真正收口到用户入口层。

## Goals / Non-Goals

**Goals:**

- 移除顶层 provider 根命令组，让 CLI 顶层只保留稳定业务语义命令。
- 让 provider-specific 扩展命令挂载到业务语义路径下，但仍保留其 provider 归属和 backend 约束。
- 保持 provider-specific 扩展命令“不传 `--backend` 也可执行”的默认路由能力。
- 把错误 backend 的失败文案改成带纠错提示的指导式报错。
- 同步更新测试和文档，使其与新的命令面一致。

**Non-Goals:**

- 不在本次 change 中重命名 capability 名称或 `command_key`。
- 不把 provider-specific 扩展命令强行改造成 shared 命令。
- 不新增新的 provider-specific 命令，也不扩展新的 backend。
- 不修改 handler 实现、标准结果契约或 enrichment / observation 主链。

## Decisions

### 决策一：收敛命令面，只改 CLI 路径，不改 capability 标识

本次最小实现选择只收敛命令可见路径，而不重写内部 capability / command key 命名。

具体做法：

- 顶层不再创建 `akshare` 这类 provider 根组；
- provider-specific 扩展命令改为声明业务语义 CLI 路径，例如把 `("akshare", "industry", "boards")` 改成 `("equity", "industry", "boards")`；
- `command_key` 和 capability 仍可保持 `akshare.industry.boards`，以避免本次提案扩散到执行器、观测结构和测试基线之外的内部标识重命名。

这样做的原因：

- 用户可见问题在于命令面泄漏 provider，而不是内部标识名本身；
- 改 CLI 路径已经能满足“顶层只有命令本身”的目标；
- 内部标识保留 provider 前缀，可继续清晰表达“这是 provider-specific 能力，而不是 shared capability”。

替代方案：

- 同时把 `command_key`/capability 改成完全业务化命名，例如 `equity.industry.boards`。
- 放弃原因：会扩大到 provider handler 注册、观测元数据、测试断言和文档语义，不符合本次最小闭环目标。

### 决策二：provider 扩展命令直接挂入业务树，而不是再保留独立装配层

当前实现通过 `list_provider_extension_commands()` 返回 `{backend_name: definitions}`，再在根命令上逐个创建 provider 根组。这个装配模型天然会把 backend 名称暴露到顶层。

本次将其改为：

- 仍允许 provider 在注册表中声明 `extension_commands`；
- 但 `commands.py` 不再按 provider 分组创建根命令；
- 而是直接按每个 `CommandDefinition.cli_path` 的首段挂入已有业务树，必要时创建共享式 group 节点。

这样做的原因：

- provider-specific 与 shared 的差异应体现在 definition 元数据和支持矩阵上，而不是顶层命令分区上；
- 统一的树挂载方式更符合当前 `attach_definition_to_tree()` 的能力边界；
- 后续再接入其它 provider-specific 命令时，也不需要新增新的顶层 provider 面。

替代方案：

- 保留 provider 根组，但额外再提供一份业务别名路径。
- 放弃原因：会造成双入口并存，继续放大 discoverability 和兼容维护成本。

### 决策三：单 backend 扩展命令继续使用“命令默认路由”，但错误提示改成指导式

现有 `resolve_backend_selection()` 已经支持 provider-extension 命令在未传 `--backend` 时使用 `command-default`。这条规则与目标一致，应保留。

本次只调整两点：

- 在规范上明确：当命令支持矩阵只有一个 backend 时，用户可以省略 `--backend`；
- 当用户显式传入错误 backend 时，报错除了列出支持矩阵，还要说明该命令会默认路由到哪个 backend，以及无需如何调用。

这样做的原因：

- provider-specific 扩展命令本质上是“超集命令默认路由到自己支持的 backend”；
- 仅返回 `does not support backend` 虽然正确，但不足以纠正用户的心智；
- 指导式文案能把错误提示转成可执行迁移信息。

替代方案：

- 对错误 backend 静默回退到命令默认 backend。
- 放弃原因：会掩盖用户输入错误，削弱支持矩阵的约束价值，也不符合零信任和显式失败原则。

### 决策四：帮助文本和文档把 provider-specific 与 backend 选择分开说明

命令树收敛后，帮助文本需要防止另一种混淆：用户可能误以为 provider-specific 命令既然不再显示 provider 根组，就变成 shared 命令了。

因此本次要求：

- provider-specific 命令帮助文本明确显示 capability、命令类别和支持 backend；
- 文档中明确“provider-specific 命令仍然只支持指定 backend，但其命令路径属于业务语义树”；
- 示例统一展示“不传 backend 的默认调用”和“传错 backend 的失败提示”。

## Risks / Trade-offs

- [风险] 顶层 provider 根组删除后，现有测试与文档会大面积引用旧路径。  
  缓解：把 CLI 回归测试和两份核心文档纳入本次 change 的显式范围，统一迁移命令示例。

- [风险] 若多个 provider 将来在同一业务语义路径下注册扩展命令，可能产生路径冲突。  
  缓解：当前 change 仅收敛现有 `akshare` 示例命令，并要求保留 `command_key` 的 provider 前缀；未来若出现冲突，再通过命令目录审核或路径命名规范处理。

- [风险] 用户可能因为帮助页不再看到 `akshare` 顶层组，而误判某些命令是 shared。  
  缓解：在帮助文本中明确展示命令类别和支持 backend，并在错误 backend 报错中补充指导信息。

- [风险] 若装配逻辑改动过大，可能影响 `watch` 包装或统一请求对象构建。  
  缓解：不改执行器和 watch 主链，只改命令树装配方式，并保留现有 `CommandDefinition` 与 `resolve_backend_selection()` 接口。

## Migration Plan

1. 调整 OpenSpec 和实现设计，确定 provider-specific 命令的新 CLI 路径和挂载规则。
2. 改造 `commands.py` 的 provider extension 装配方式，删除顶层 provider 根组注册。
3. 修改 `providers.py` 中现有扩展命令的 `cli_path`，并保留现有 `command_key`、capability 和 handler 绑定。
4. 调整 `resolver.py` 的错误 backend 提示文案，补充默认路由说明。
5. 更新 CLI 回归测试和文档示例，验证新路径和默认 backend 语义。
6. 定向回归 `watch`、shared 命令和 provider-specific 命令，确认统一执行链未被破坏。

## Open Questions

- provider-specific 扩展命令的首个业务语义路径应使用 `equity industry boards`，还是再抽成更中性的 `industry boards`？当前建议优先沿用现有共享树语义，使用 `equity industry boards`。
- 是否需要在 CLI 顶层保留兼容性提示或迁移别名？当前提案不保留双入口，以避免继续扩大命令面。
