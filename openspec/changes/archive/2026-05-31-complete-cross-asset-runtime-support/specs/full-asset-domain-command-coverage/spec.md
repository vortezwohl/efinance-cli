## MODIFIED Requirements

### Requirement: 系统必须提供完整且真正可用的资产域命令面
系统 MUST 在当前多后端命令目录中提供完整资产域命令面；对关键命令而言，“提供”不仅指命令存在，还指其在声明支持的 backend 上真正端到端可用。

#### Scenario: 关键命令不是仅可路由
- **WHEN** 系统声称某资产域关键命令已纳入现行 CLI
- **THEN** 该命令 MUST 具备请求校验、真实 handler、稳定结果和对应测试，而不只是出现在命令树中
