## MODIFIED Requirements

### Requirement: 系统必须为迁移后的命令族提供稳定结果契约
系统 MUST 为共享 capability 定义稳定的结果契约，而 SHALL NOT 让迁移后的命令族直接裸露第三方返回结构；新增命令族 MUST 至少支持历史行情、实时行情、资料、通用记录列表、标量列表、标量值与 side-effect 状态这些契约层。

#### Scenario: 强结构化命令继续输出标准字段
- **WHEN** 系统执行 `stock price history`、`stock price live`、`stock profile` 或 `fund nav history`
- **THEN** 系统 MUST 返回可被 enrichment / observation 复用的标准字段结构

#### Scenario: 宽列表命令仍有稳定契约外壳
- **WHEN** 系统执行目录、成交、资金流、配置、板块、龙虎榜等列表型命令
- **THEN** 系统 MUST 以稳定的记录列表契约封装结果，而不是把 provider 原始对象直接泄漏到执行骨架

#### Scenario: 标量与 side-effect 命令具备稳定输出
- **WHEN** 系统执行 `resolve quote-id`、`fund disclosure dates`、`fund reports download` 或 `market add`
- **THEN** 系统 MUST 使用标量值、标量列表或 side-effect 状态契约表达结果
