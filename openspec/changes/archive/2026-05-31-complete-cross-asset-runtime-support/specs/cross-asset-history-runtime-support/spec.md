## ADDED Requirements

### Requirement: 各资产 history 命令必须具备真实端到端支持
系统 MUST 让迁移后的关键 history 命令在声明支持的 backend 上具备真实端到端支持，而 SHALL NOT 只停留在“命令存在并可路由”的状态。

#### Scenario: bond / futures / quote history 不再只是 generic 路径
- **WHEN** 用户执行 `bond price history`、`futures price history` 或 `quote price history`
- **THEN** 系统 MUST 返回稳定标准化结果，并进入明确的后续处理路径，而不是长期依赖无约束 generic 兜底

#### Scenario: fund history batch 具有稳定批量语义
- **WHEN** 用户执行 `fund nav history-batch`
- **THEN** 系统 MUST 返回稳定的多 source 历史结果结构，并具备与单标的 history 明确对应的渲染与观察语义

### Requirement: history 支持矩阵必须反映真实能力
系统 MUST 仅为真实完整实现的 history capability 声明 backend 支持。

#### Scenario: backend 声明支持的 history capability 通过定向验证
- **WHEN** provider 为某 history capability 声明 supported
- **THEN** 该 capability MUST 具备对应的标准结果与定向测试验证
