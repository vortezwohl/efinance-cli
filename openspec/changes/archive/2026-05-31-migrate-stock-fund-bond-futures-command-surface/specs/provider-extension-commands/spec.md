## MODIFIED Requirements

### Requirement: 系统必须允许 provider-specific 扩展命令挂载到稳定业务路径
系统 MUST 允许 backend provider 注册共享命令之外的扩展命令，并把这些命令挂载到稳定的业务语义命令树中；在资产域迁移后，这些命令 MUST 挂载在 `stock`、`fund`、`bond`、`futures` 或 utility 路径下，而 SHALL NOT 回退为 provider 名称根组。

#### Scenario: provider 扩展命令不再以 provider 根组暴露
- **WHEN** 用户查看根命令帮助或执行 provider-specific 扩展命令
- **THEN** 系统 SHALL NOT 要求用户通过 provider 名称顶层分组访问该命令

#### Scenario: provider 扩展命令仍保留其 backend 约束
- **WHEN** 用户执行 provider-specific 扩展命令
- **THEN** 系统 MUST 继续展示并校验其命令类别与支持 backend，而不会因为路径业务化就把它误判为完全共享能力
