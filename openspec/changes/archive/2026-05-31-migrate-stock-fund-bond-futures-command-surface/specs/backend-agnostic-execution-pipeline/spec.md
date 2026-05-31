## MODIFIED Requirements

### Requirement: 系统必须通过统一执行骨架处理完整命令面
系统 MUST 使用统一执行骨架处理命令调用，包括请求校验、backend 解析、能力调用、标准化、增强、观察、渲染和输出；这项要求 MUST 适用于迁移后的资产域命令、utility 命令、批量命令和带副作用命令。

#### Scenario: 批量命令仍走统一执行骨架
- **WHEN** 用户执行 `fund nav history-batch` 或其他批量命令
- **THEN** 系统 MUST 继续复用同一请求校验、backend 路由与结果物化主链

#### Scenario: side-effect 命令仍走统一执行骨架
- **WHEN** 用户执行 `fund reports download` 或 `market add`
- **THEN** 系统 MUST 继续复用统一命令请求、backend 解析和结果输出路径，而不是单独旁路
