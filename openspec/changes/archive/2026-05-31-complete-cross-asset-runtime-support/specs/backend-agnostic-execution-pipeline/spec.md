## MODIFIED Requirements

### Requirement: 统一执行骨架必须承载关键命令家族的一等主链
系统 MUST 使用统一执行骨架处理迁移后的命令家族；对关键 history/live/profile 命令而言，该骨架 MUST 把它们送入明确的一等标准化、增强和 observation 路径，而 SHALL NOT 长期停留在无约束 generic 结果路径。

#### Scenario: 关键命令进入明确主链
- **WHEN** 用户执行关键 history/live/profile 命令
- **THEN** 系统 MUST 进入对应家族的标准化与后续处理主链

#### Scenario: generic 兜底只用于非关键或未专门建模结果
- **WHEN** 系统处理非关键或仍无专门建模的结果
- **THEN** 系统 MAY 使用 generic 兜底，但 SHALL NOT 把关键命令长期留在该路径
