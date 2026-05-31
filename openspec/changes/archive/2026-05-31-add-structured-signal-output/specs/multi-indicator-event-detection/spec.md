## ADDED Requirements

### Requirement: 跨指标家族识别客观近期事件
系统 SHALL 在支持的结构化观察输出中，跨趋势、动量、波动、通道、量价/资金流等指标家族识别近期客观事件。

#### Scenario: 事件检测覆盖多个指标家族
- **WHEN** 系统基于兼容的 OHLCV 历史数据组装结构化观察输出
- **THEN** 系统 SHALL 在多个指标家族上执行配置的事件规则，而不是仅限于均线或 MACD 交叉

### Requirement: 事件记录必须是事实型结构
系统 SHALL 将 recent events 输出为结构化事实记录，而不是预判后的方向性总结。

#### Scenario: 事件记录包含事实字段
- **WHEN** 系统输出一个已检测到的近期事件
- **THEN** 该事件记录 SHALL 包含 `bars_ago`、`event_key`、`subject_a`、`relation`、`subject_b`（如适用）、前值/现值（如适用）以及英文事实描述

#### Scenario: 事件描述保持观察口径
- **WHEN** 系统渲染事件描述
- **THEN** 描述 SHALL 只陈述发生了什么，例如 crossing、move、touch、sign change、consecutive move，而 SHALL NOT 追加默认投资判断

### Requirement: Recent events 受 trace window 约束
系统 SHALL 默认将 recent event 检测范围限定在与 trace 输出相同的近期窗口内，除非命令显式要求不同事件窗口。

#### Scenario: 超出 observation window 的事件不会出现在默认 recent event 列表中
- **WHEN** 用户请求 32 根 observation window
- **THEN** 默认的 recent event 列表 SHALL 只包含这 32 根内检测到的事件

### Requirement: 事件 relation 使用规范化英文标识
系统 SHALL 为结构化事件输出使用规范化英文 relation 标识。

#### Scenario: crossing 事件使用规范化 relation
- **WHEN** 系统检测到线与线的 crossing 事件
- **THEN** 系统 SHALL 输出 `crossed_above`、`crossed_below` 一类规范化 relation，而不是本地化或主观性措辞

#### Scenario: 非 crossing 事件使用规范化 relation
- **WHEN** 系统检测到 threshold、band、sign 或 direction 变化事件
- **THEN** 系统 SHALL 输出能够描述该观察现象的规范化英文 relation
