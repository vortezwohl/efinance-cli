## Context

当前代码库已经完成“多后端能力骨架”建设：

- `BackendName` 枚举已经包含 `YFINANCE`；
- `list_optional_provider_names()` 已把 `yfinance` 标记为预留 provider；
- `CommandExecutor -> CommandFacade -> BackendProvider -> CapabilityHandler` 的执行主链已经稳定；
- 共享命令的 schema、结果契约、observation 和 rendering 已经围绕标准结果工作；
- 现有正式 provider 仍只有 `efinance` 与 `akshare`。

本轮调研基于项目 `.venv` 中已安装的 `yfinance==1.4.1` 源码完成，重点事实如下：

- 搜索入口是 `yfinance.search.Search`，返回 `quotes/news/lists/research/nav` 多类结果；
- 历史行情入口是 `Ticker.history()` 与批量 `download()`，底层统一走 `PriceHistory`；
- 快照与资料面分成 `FastInfo`、`Quote.info`、`history_metadata` 等不同对象；
- 基金画像走 `FundsData`，能提供概览、费率、资产配置、前十大持仓、债券评级、行业权重；
- 实时流走 `live.WebSocket` / `AsyncWebSocket`，与当前 CLI 的同步轮询式 `watch` 不是一回事；
- 真实运行验证中，`Search`、`Ticker.history()`、`FastInfo`、`FundsData` 都可能直接抛出 `YFRateLimitError`，说明 Yahoo 限流必须被视作一等设计约束。

这意味着 `yfinance` 接入不能简单照搬 `efinance` / `akshare`：

- 它天然更偏全球 ticker / Yahoo symbol 语义，而不是国内市场代码表；
- 它的资料面与实时字段来自不同入口，字段完整度不稳定；
- 它具备一些很强的 Yahoo 专属能力，但并不适合全部塞进共享命令；
- 它的网络稳定性更依赖速率控制、错误收束和显式降级。

## Goals / Non-Goals

**Goals:**

- 让 `yfinance` 成为当前架构下的正式 backend，而不是文档里的 future placeholder。
- 为共享命令建立一组“真实可维护”的 `yfinance` 支持面，而不是名义支持。
- 把 `yfinance` 的历史、快照、资料面、基金资料与搜索能力映射到现有标准结果契约。
- 为 Yahoo 限流、字段缺失和市场语义差异建立显式 guardrails。
- 把不适合共享抽象的 Yahoo 能力收敛到 provider-extension 命令组。
- 严格遵循“单 backend 命令必须是 provider-extension”的现行命令分类规则。

**Non-Goals:**

- 不要求 `yfinance` 覆盖当前所有共享命令。
- 不在本轮把 WebSocket 流式订阅重构进现有 `watch` 主链。
- 不承诺所有 `yfinance` 支持的 Yahoo 页面能力都被 CLI 暴露。
- 不为了 `yfinance` 牺牲现有共享 schema 的稳定性，去把整个命令面重写成 Yahoo 原生参数语义。
- 不以“静默回退到其他 backend”作为 `yfinance` 不支持场景的兼容策略。

## Decisions

### 决策一：共享命令支持按“最小稳定闭环”分层接入

`yfinance` 的共享支持不会一次性铺满所有命令，而是分三层：

1. 第一层，必须接入：
   - `instrument.search`
   - `stock.price.history`
   - `stock.profile`
   - `fund.nav.history`
   - `fund.profile`
   - `quote.price.history`
   - `quote.price.latest`
   - `quote.profile`
2. 第二层，条件接入：
   - `fund.nav.history-batch`
   - `stock.price.latest`
   - `stock.price.snapshot`
3. 第三层，明确不纳入首轮共享支持：
   - `bond.*`
   - `futures.*`
   - `market.price.live`
   - 国内市场专属 flow / trades / report-dates / disclosure 之类 Yahoo 无稳定对应的数据面

原因：

- `yfinance` 对股票 / ETF / mutual fund / quote 通路最自然；
- 当前共享命令里大量中国市场专属命令并没有 Yahoo 等价物；
- 先把“能稳定标准化”的链路做扎实，比扩大名义覆盖面更重要。

备选方案：

- 直接把所有 `quote.*`、`stock.*` 标成支持。放弃，因为这会制造大量“路由成功但字段不完整”的伪支持。

### 决策二：历史类能力统一优先走 `Ticker.history()`，批量历史按受控方式使用 `download()`

设计上将优先把单标的历史统一到 `Ticker.history()`：

- `stock.price.history`
- `quote.price.history`
- `fund.nav.history`

只有在共享命令已经天然是批量语义、且验证过返回 shape 可稳定物化时，才允许受控引入 `download()`。

原因：

- `Ticker.history()` 返回 shape 更稳定，metadata 也更容易与 symbol 绑定；
- `download()` 会引入 MultiIndex、批量失败聚合、线程控制、去重与索引对齐的额外复杂度；
- 先把单标的主链打通，更符合当前架构的最小闭环原则。

备选方案：

- 所有历史都统一用 `download()`。放弃，因为它会让标准化、错误定位和 observation 输入复杂化。

### 决策三：最新价 / 快照能力拆成 `FastInfo` 优先，`Quote.info` 兜底

`yfinance` 的实时近似能力不应直接等同于 `live.WebSocket`。共享命令中的 `quote.price.latest`、可能的 `stock.price.latest` / `snapshot` 将采用：

- 首选 `FastInfo` 的 `lastPrice/open/dayHigh/dayLow/lastVolume/marketCap/...`
- 必要时从 `history_metadata` 与 `Quote.info` 补 `currency/market/exchange/quoteType/shortName`
- 明确把其语义定义为“最近一次 Yahoo 提供的快照”，而不是强实时 streaming

原因：

- `FastInfo` 与现有 `realtime-quotes` 契约更接近；
- `WebSocket` 是长连接订阅模型，暂时不适合硬塞进轮询命令；
- `Quote.info` 字段更多，但慢且不稳定，适合作为资料面补充而不是首选快照源。

备选方案：

- 首轮就把 `watch --backend yfinance` 接到 WebSocket。放弃，因为这会把执行模型从同步拉取改成事件驱动，超出本轮范围。

### 决策四：资料面分成股票资料与基金资料两条标准化路径

`stock.profile` / `quote.profile` 与 `fund.profile` 不能复用一套粗糙映射：

- 股票 / 普通 quote 资料面来自 `Quote.info`、`history_metadata`、必要时补 `FastInfo`
- 基金资料面来自 `FundsData`，优先暴露 fund overview、operations、asset classes、top holdings、bond ratings、sector weightings

这要求结果契约层允许：

- 共享核心字段继续统一，例如 `code/name/quote_id/market`
- provider_fields 保留 Yahoo 特有字段块，避免强行压平导致信息流失

原因：

- `FundsData` 自带明显不同于股票资料面的结构；
- 强行套用现有 `profile-info` 的扁平思路会损失大量基金专属信息；
- 共享命令可以保留统一入口，但标准结果必须允许不同类型的补充载荷。

备选方案：

- 把基金资料也全塞成一个扁平 dict。放弃，因为会让基金画像退化成几项弱字段。

### 决策五：Yahoo 专属高价值能力进入 provider-extension，而不是继续扩张共享命令

以下类型能力优先定义为 `yfinance` 扩展命令：

- 新闻 `Ticker.news`
- 期权链 `Ticker.option_chain()`
- 基金前十大持仓 / 资产配置 / 债券评级 / 行业权重的细分视图
- 后续可能的 earnings calendar、recommendations、analyst targets

原因：

- 它们属于 Yahoo 明显更强但不具备多后端对等性的能力；
- 放进扩展命令树后，帮助页和测试边界更清晰；
- 可以避免为了抽象共享能力而弱化这些数据面的表达力。

备选方案：

- 继续扩张共享命令树，为每种资料面都寻找“跨 provider 最小公分母”。放弃，因为当前真实需求是把 `yfinance` 接进来，而不是再发起一轮命令面大战略重构。

补充约束：

- 若某个新增命令当前仅由 `yfinance` 单独支持，它必须直接定义为 provider-extension；
- 只有真实支持至少两个 backend 的命令，才允许进入 shared catalog；
- 不允许为了“未来也许会多 backend”而先把单 backend 命令挂成 shared 占位。

### 决策六：限流与不完整市场覆盖必须进入运行时 guardrails，而不是藏在重试里

本轮会显式定义 `yfinance` runtime guardrails：

- 识别并保留 `YFRateLimitError` 语义；
- 在结果或错误信息中指明“Yahoo rate limited”，而不是只报通用网络错误；
- 对共享命令帮助与文档补充“全球市场更友好，中国本地数据能力有限”的说明；
- 对未支持命令返回明确 backend 不支持错误，不走 fallback；
- 对字段缺失走“契约级最小成功 + provider_fields 保留 + observation 降级”，而不是伪造字段。

原因：

- 调研时四条最小验证链就复现了限流，这不是边缘异常；
- 如果只在 retry 层吞掉，会让用户误以为 `yfinance` 天然等价于现有国内数据源。

备选方案：

- 增加更多重试并假设大多数问题会消失。放弃，因为限流是平台行为，不是单纯瞬时网络抖动。

## Risks / Trade-offs

- [风险] Yahoo 限流会让自动化测试和手工验证不稳定。 → 缓解：provider 层主测 contract/unit tests，以 mock/fake payload 为主；少量 live smoke test 标记为可选或手工。
- [风险] `yfinance` 的全球 symbol 语义与现有 `market_type` / 国内代码习惯不一致。 → 缓解：新增 `yfinance` 专属请求归一化层，明确哪些共享参数可映射、哪些命令只接受 Yahoo ticker / quote id。
- [风险] 基金资料面比现有 `profile-info` 契约 richer，直接压平会丢信息。 → 缓解：扩展结果契约或允许 provider_fields 挂载结构化子块，并让 raw / observation 都可见。
- [风险] 如果过早把 WebSocket 纳入共享实时链，会把执行模型复杂化。 → 缓解：首轮只承诺快照式 latest/quote 支持，把 streaming 放到扩展命令或后续变更。
- [风险] 用户可能期待 `yfinance` 覆盖 bond / futures / 中国市场专属命令。 → 缓解：在支持矩阵、帮助文本、错误信息和文档中显式标记不支持范围。

## Migration Plan

1. 在 provider 注册表中正式接入 `yfinance`，补齐依赖探测、backend 解析和帮助展示。
2. 先实现搜索、历史、股票资料、基金历史、基金资料、quote latest/profile 这组最小闭环 handler。
3. 为 `yfinance` 增加契约测试与标准化测试，确保输出能进入现有 enrichment / observation / rendering 主链。
4. 增加 Yahoo 专属扩展命令组，把新闻 / 期权链 / 基金画像等高差异能力从共享命令面隔离出来。
5. 最后再视稳定性评估是否扩大 `stock.price.latest`、`snapshot`、`history-batch` 等条件支持面。

回退策略：

- 若 `yfinance` 正式 provider 不稳定，可在不影响 `efinance` / `akshare` 的前提下，仅回退其 provider 注册与命令支持矩阵声明；
- 若某个共享 capability 标准化失败，可单独撤回该 capability 对 `yfinance` 的支持，而不必整体删除 `yfinance` backend。

## Open Questions

- `fund.profile` 是否应扩展出新的共享结果契约，还是先通过 `profile-info + provider_fields` 过渡？
- `quote.price.latest` 在 `yfinance` 下是否要接受批量 symbol 输入，还是首轮只保证单标的稳定输出？
- `instrument.search` 是否需要新增 `classify -> market` 的 Yahoo 专属映射表，来改善搜索结果到后续命令的衔接？
- provider-extension 命令树是挂到 `quote` / `fund` / `stock` 现有根组下，还是为 `yfinance` 定义一组更显式的扩展子路径？
