## ADDED Requirements

### Requirement: 系统必须提供完整的 utility 入口命令面
系统 MUST 在四个资产域之外提供 `quote`、`market`、`resolve` 与 `search local` 等 utility 入口，并保持它们位于稳定的用户任务路径下。

#### Scenario: quote 入口暴露跨资产查询命令
- **WHEN** 系统构建 utility 命令树
- **THEN** 系统 MUST 暴露 `quote profile`、`quote trades`、`quote flow today`、`quote flow history`、`quote price latest` 与 `quote price history`

#### Scenario: market 与 resolve 入口暴露高级 utility 命令
- **WHEN** 系统构建 utility 命令树
- **THEN** 系统 MUST 暴露 `market price live`、`resolve quote-id` 与 `search local`

### Requirement: 顶层 search 与 watch 必须保留特殊入口语义
系统 MUST 保留顶层 `search` 默认调用和顶层 `watch` 刷新包装语义，而 SHALL NOT 把它们降级为普通资产域命令。

#### Scenario: search 仍可直接作为顶层查询入口
- **WHEN** 用户执行顶层 `search`
- **THEN** 系统 MUST 继续把它作为默认证券候选搜索入口

#### Scenario: watch 仍可包装任意支持刷新命令
- **WHEN** 用户执行顶层 `watch` 并追加完整子命令
- **THEN** 系统 MUST 把刷新参数转发给目标命令，而不是把 `watch` 当作业务命令本身执行
