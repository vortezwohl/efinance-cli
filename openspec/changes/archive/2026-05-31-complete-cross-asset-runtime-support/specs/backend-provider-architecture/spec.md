## MODIFIED Requirements

### Requirement: provider 支持矩阵必须只声明真实完整支持
系统 MUST 让 provider 通过显式支持矩阵声明其 capability 覆盖范围；该支持矩阵 SHALL NOT 把仅有路由能力、无稳定结果或无验证的 capability 声明为 supported。

#### Scenario: 声明支持需要对应实现与测试
- **WHEN** provider 为某 capability 声明 supported
- **THEN** 该 capability MUST 具备真实 handler 实现、稳定标准结果和至少一条定向验证
