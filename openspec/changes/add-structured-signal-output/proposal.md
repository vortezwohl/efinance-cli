## 为什么要做

当前 CLI 虽然已经能够为行情结果补充技术指标列，但整体仍然更像“原始指标转储器”，而不是“结构化观察输出器”。用户无法稳定地查看最近一段连续指标点位，无法在不同命令间一致地检查客观事件现象，默认表格渲染在指标变多后也会迅速变宽、变乱、变得难读。

现在推进这项变更的原因是：项目已经具备可复用的指标计算层和增强链路，但缺少一套稳定的“观察输出协议”。如果继续只增加指标列，输出只会越来越宽、越来越吵，而不会真正提升可读性和分析效率。

## 变更内容

- 为 `get-quote-history` 与 `get-latest-quote` 引入结构化信号观察输出模型。
- 识别多个指标家族中的客观近期事件，不再只局限于均线或 MACD 交叉，包括但不限于交叉、阈值穿越、方向变化、上下轨触碰、正负号变化、连续抬升/回落等现象。
- 为关键指标组提供默认最近 32 根的连续 trace 输出，并允许用户自行设置 trace window。
- 调整 trace 输出约束：`trace_points` 在 `table` 中允许横向展开，但必须仍然输出浮点数，不使用字符图、sparkline 或主观图形符号。
- 调整 section 顺序：`trace_points` 应位于 `recent_events` 之前，用户先看连续数值，再看事件总结。
- 重做 CLI 的 `table` 渲染，使其采用统一的 ASCII boxed section 风格；除 `trace_points` 的数值块可横向展开外，其余 section 以纵向条目为主。
- 统一 table section 外观：每个 section 都必须是规整的 ASCII 矩形框，内部按条目列出内容，`recent_events` 采用“一个总外框内列出多条事件”的形式，而不是“一事件一外框”。
- 强化 table 排版约束：任何字符串都不允许顶穿边框；边框宽度必须根据排版后的内容动态计算；对超长内容必须先折行，再据此计算最终框宽。
- 确保 `table`、`json`、`csv`、`tsv` 暴露相同信息量，差异仅体现在表现形式，不允许某一格式缺失最近事件或连续 trace 信息。
- 默认输出只陈列观察事实和近期事件，不预先给出 bullish、bearish、neutral、confidence、regime 等主观方向性判断。
- CLI 输出语言统一为英文，包括 section 名、字段名、事件 relation、事件 description 以及序列化 key；但 OpenSpec 提案与内部协作文档使用中文。
- 在新增结构化观察输出路径的同时，保留现有原始/增强指标数据的访问路径，避免一次性替换全部输出行为。

## 能力范围

### 新增能力
- `structured-signal-output`：为最新行情与历史行情命令提供统一的结构化观察 schema，覆盖元信息、最新行情字段、当前指标、近期事件与最近 trace 点位。
- `multi-indicator-event-detection`：跨趋势、动量、波动、通道、量价/资金流等指标家族识别客观近期事件，输出事实型事件记录，而不是预判后的多空总结。
- `vertical-multi-format-rendering`：让 `table`、`json`、`csv`、`tsv` 基于同一观察信息集输出，其中 table 采用 boxed section 风格，`trace_points` 支持横向浮点数块，其余内容优先纵向呈现。

### 修改能力
- 无。

## 影响范围

- 受影响代码路径包括 `efinance_cli/enrichment/`、`efinance_cli/indicators/`、`efinance_cli/rendering.py`、`efinance_cli/executor.py`、`efinance_cli/commands.py` 以及相关测试。
- 该变更会引入新的 CLI 运行时选项与新的结构化输出路径，尤其影响支持 `get-latest-quote` 和 `get-quote-history` 的命令族。
- 该变更不会新增第三方依赖，但会引入新的内部观察 schema、事件检测逻辑，以及一套独立于 `DataFrame.to_string()` 的 boxed table 渲染契约，需要专门的回归测试覆盖。
