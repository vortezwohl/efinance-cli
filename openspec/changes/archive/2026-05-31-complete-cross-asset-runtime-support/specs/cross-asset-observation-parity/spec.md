## ADDED Requirements

### Requirement: 关键资产主链必须具备一等 observation / enrichment 支持
系统 MUST 让关键资产主链的 `history`、`live`、`profile` 命令具备一致等级的 observation / enrichment 支持，而 SHALL NOT 继续让 `stock` 成为唯一一等主链。

#### Scenario: 多资产 history 共享明确观察策略
- **WHEN** 用户对 `stock`、`bond`、`futures` 或 `quote` 的 history 命令请求 observation 输出
- **THEN** 系统 MUST 返回稳定的序列观察输出，并复用或明确定义对应的指标与近期事件策略

#### Scenario: fund history 命令具备定义清晰的 observation 语义
- **WHEN** 用户对 `fund nav history` 或 `fund nav history-batch` 请求 observation 输出
- **THEN** 系统 MUST 返回定义清晰的单 source 或多 source 序列 observation，而不是退回无约束原始记录输出

### Requirement: live / profile 主链不得只依赖股票历史回补
系统 MUST 为关键 `live` / `profile` 命令提供与其资产语义一致的补充与观察策略，而 SHALL NOT 只保留 `stock` 路径的专用回补逻辑。

#### Scenario: 非 stock 的关键主链拥有明确补充边界
- **WHEN** 系统处理 `bond`、`futures`、`quote` 或 `fund` 的关键主链命令
- **THEN** 系统 MUST 明确其 enrichment / observation 支持边界，并以测试固定下来
