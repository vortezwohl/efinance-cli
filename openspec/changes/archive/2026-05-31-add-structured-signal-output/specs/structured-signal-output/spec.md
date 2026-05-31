## ADDED Requirements

### Requirement: 最新行情的结构化观察输出
系统 SHALL 为支持的最新行情命令提供结构化观察输出模式，并在所有支持的输出格式中包含同等核心信息。

#### Scenario: 最新行情 observation payload 被组装
- **WHEN** 用户对支持的最新行情命令请求结构化观察输出
- **THEN** 系统 SHALL 在结果中包含 `meta`、`latest_quote`、`current_metrics`、`trace_points` 和 `recent_events` 区块

#### Scenario: 最新行情 trace window 默认值为 32
- **WHEN** 用户未为支持的最新行情命令显式指定 trace window
- **THEN** 系统 SHALL 使用最近 32 根作为 trace 输出窗口

#### Scenario: 最新行情 trace window 可由用户配置
- **WHEN** 用户为支持的最新行情命令指定了有效的 trace window
- **THEN** 系统 SHALL 使用用户请求的窗口值，而不是默认值

### Requirement: 历史行情的结构化观察输出
系统 SHALL 为支持的历史行情命令提供结构化观察输出模式，并保留近期 bar 上下文与近期客观事件信息。

#### Scenario: 历史行情 observation payload 被组装
- **WHEN** 用户对支持的历史行情命令请求结构化观察输出
- **THEN** 系统 SHALL 基于返回的历史数据组装 `meta`、`current_metrics`、`trace_points` 和 `recent_events` 区块

#### Scenario: 历史行情输出保留连续 trace 点位
- **WHEN** 支持的历史行情命令返回的数据足以满足 trace window
- **THEN** 系统 SHALL 输出所请求指标组的最近 trace 点位，而不是把连续数据压缩成单个横向摘要值

### Requirement: 当前指标区块只陈列事实
系统 SHALL 把当前指标值作为观察事实输出，并且 SHALL NOT 在默认结构化观察输出中插入预判性的方向性总结。

#### Scenario: 当前指标区块不出现方向性标签
- **WHEN** 系统渲染结构化观察输出
- **THEN** `current_metrics` 区块 SHALL 只包含指标名称与指标值，不包含 bullish、bearish、neutral、regime、confidence 等默认标签

### Requirement: Trace 点位顺序先于 recent events
系统 SHALL 在结构化观察输出中先输出 `trace_points`，再输出 `recent_events`。

#### Scenario: Trace 点位先于事件列表
- **WHEN** 系统渲染结构化观察输出
- **THEN** `trace_points` 区块 SHALL 出现在 `recent_events` 区块之前
