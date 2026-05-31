## 1. Observation 模式基础设施

- [x] 1.1 定义适用于最新行情与历史行情命令的内部结构化 observation payload 模型。
- [x] 1.2 增加运行时选项，用于选择结构化 observation 输出路径，并支持 `trace_window` 配置，默认值为 32。
- [x] 1.3 明确第一批支持结构化 observation 的命令集合，并在不移除现有 raw/enriched 路径的前提下完成调度接入。

## 2. 事件检测与 Trace 提取

- [x] 2.1 实现可复用的近期 trace 提取逻辑，支持按请求的 trace window 输出多个规范化指标组。
- [x] 2.2 实现趋势类指标的事实型近期事件检测，包括交叉、站上/跌破和方向变化事件。
- [x] 2.3 实现动量、波动/通道、量价/资金流指标的事实型近期事件检测。
- [x] 2.4 规范 recent event 输出字段，统一使用英文结构化字段和英文事实描述。

## 3. 结构化 Observation 组装

- [x] 3.1 构建最新行情的结构化 observation assembler，输出 `meta`、`latest_quote`、`current_metrics`、`trace_points`、`recent_events`。
- [x] 3.2 构建历史行情的结构化 observation assembler，沿用同一 schema 家族。
- [x] 3.3 确保 observation assembler 只输出事实，不输出默认的 bullish/bearish/confidence/regime 总结。
- [x] 3.4 调整 section 顺序，保证 `trace_points` 位于 `recent_events` 之前。

## 4. Boxed Table 与多格式渲染

- [x] 4.1 实现结构化 observation 的 boxed table renderer，统一所有 section 的 ASCII 外框风格。
- [x] 4.2 为 boxed table renderer 实现动态宽度计算、折行和“不可穿墙”约束。
- [x] 4.3 实现 `trace_points` 的 boxed 横向浮点数 block 渲染，不使用字符图。
- [x] 4.4 实现 `recent_events` 的单外框多事件渲染形式，而不是一事件一外框。
- [x] 4.5 实现 JSON 序列化，确保与 table 拥有相同 observation 信息量。
- [x] 4.6 实现 CSV / TSV 的 long-form 序列化，确保与 table / JSON 拥有相同 observation 信息量。

## 5. 验证与回归覆盖

- [x] 5.1 为 trace window 行为补充单元测试，包括默认 32 根和用户覆盖场景。
- [x] 5.2 为多指标家族 recent event detection 补充单元测试。
- [x] 5.3 为 boxed table 渲染补充回归测试，覆盖动态宽度、折行、不穿墙、统一外框和 trace block 渲染。
- [x] 5.4 为 CSV / TSV long-form 导出补充回归测试。
- [x] 5.5 为支持的最新行情和历史行情命令补充端到端命令级测试。

## 6. 文档与交付

- [x] 6.1 更新 CLI 文档，说明结构化 observation 模式、英文输出契约、trace window 行为和 boxed table 风格。
- [x] 6.2 记录 observation payload、recent event 结构和 CSV / TSV 长表契约，供后续消费者使用。
- [x] 6.3 记录上线说明，包括兼容性预期、支持命令范围和回退到现有 raw/enriched 路径的策略。
