## ADDED Requirements

### Requirement: 系统必须以 `stock` / `fund` / `bond` / `futures` 作为稳定资产域
系统 MUST 在当前 CLI 中把 `stock`、`fund`、`bond`、`futures` 定义为稳定的用户可见资产域，而 SHALL NOT 继续把 `equity` 作为正式资产分类名称。

#### Scenario: 帮助页展示四个资产域根命令
- **WHEN** 用户查看根命令帮助
- **THEN** 系统 MUST 展示 `stock`、`fund`、`bond`、`futures` 作为资产域根命令

#### Scenario: 用户可见帮助中不再把 equity 作为当前资产域
- **WHEN** 用户查看任意当前 CLI 帮助页或文档示例
- **THEN** 系统 SHALL NOT 把 `equity` 描述为当前股票资产域的正式名称

### Requirement: utility 入口不得被混同为资产域
系统 MAY 保留 `quote`、`market`、`resolve`、`search`、`watch` 等 utility 入口，但 MUST 将其与四个资产域明确区分。

#### Scenario: utility 入口与资产域在帮助页中边界清晰
- **WHEN** 用户查看命令树或文档
- **THEN** 系统 MUST 让 `quote`、`market`、`resolve`、`search`、`watch` 显示为 utility 语义，而不是资产分类
