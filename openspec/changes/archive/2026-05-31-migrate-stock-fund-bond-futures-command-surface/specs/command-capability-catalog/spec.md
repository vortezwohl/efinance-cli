## MODIFIED Requirements

### Requirement: 系统必须通过显式命令目录定义共享命令
系统 MUST 通过显式命令目录定义当前 CLI 的稳定命令，而 SHALL NOT 依赖第三方函数名、模块名或函数签名作为用户可见命令树的稳定来源；该命令目录 MUST 覆盖四个资产域与已定义 utility 入口。

#### Scenario: 命令目录覆盖完整迁移矩阵
- **WHEN** 系统构建当前 command catalog
- **THEN** 命令目录 MUST 覆盖 `command-catalog.json` 中已定义的 `stock`、`fund`、`bond`、`futures`、`quote`、`market`、`resolve` 与 `search local` 命令

#### Scenario: 命令目录不再保留 equity 主路径
- **WHEN** 系统查询股票相关命令定义
- **THEN** 该目录的稳定 CLI 路径 MUST 使用 `stock ...`，而不是 `equity ...`

### Requirement: 每个共享命令必须显式声明能力与支持矩阵
每个共享命令 MUST 显式绑定一个 capability 标识，并声明可被哪些 backend 支持或不支持；这项要求 MUST 同时适用于资产域命令与 utility 入口。

#### Scenario: 命令与 backend 支持矩阵显式可查
- **WHEN** 用户查看帮助页或系统进行 backend 解析
- **THEN** 系统 MUST 能从命令定义中直接获得该命令的 capability、命令类别和支持 backend
