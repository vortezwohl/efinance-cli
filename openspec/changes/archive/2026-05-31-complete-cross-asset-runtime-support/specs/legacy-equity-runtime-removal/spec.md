## ADDED Requirements

### Requirement: 系统不得继续把 equity 作为现行运行时命令语义
系统 SHALL NOT 在现行 runtime、测试与文档中继续把 `equity.*` 作为稳定命令键或现行用户语义。

#### Scenario: runtime 元信息不再泄漏 equity
- **WHEN** 系统为当前股票相关命令生成 observation 元信息、调试信息或补充接口查找逻辑
- **THEN** 系统 MUST 使用 `stock.*` 命令键，而不是 `equity.*`

#### Scenario: 现行测试与文档不再使用 equity 作为正式路径
- **WHEN** 用户阅读当前测试基线、使用文档或架构文档
- **THEN** 系统 SHALL NOT 把 `equity` 描述为现行正式命令路径或现行稳定命令键
