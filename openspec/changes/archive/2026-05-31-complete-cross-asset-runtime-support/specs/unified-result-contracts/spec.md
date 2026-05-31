## MODIFIED Requirements

### Requirement: 系统必须为关键命令家族提供稳定结果契约
系统 MUST 为关键命令家族提供稳定结果契约，而 SHALL NOT 让多资产 history/live/profile/flow/trades/catalog 命令长期依赖缺乏约束的宽兜底结果结构。

#### Scenario: history 家族具备稳定序列契约
- **WHEN** 系统执行 `stock`、`bond`、`futures`、`quote` 的 history 命令
- **THEN** 系统 MUST 返回稳定的序列结果契约，字段语义可被 enrichment / observation 复用

#### Scenario: 关键记录类命令具备家族级契约
- **WHEN** 系统执行 `flow`、`trades`、`catalog` 或关键 `profile` 命令
- **THEN** 系统 MUST 使用对应家族级稳定契约或经过明确定义的记录契约，而不是无约束原始对象
