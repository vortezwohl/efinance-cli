## Context

当前命令面已经迁到 `stock` / `fund` / `bond` / `futures` 及若干 utility 入口，但“命令存在”并不等于“完整支持”。现状的主要问题有三类：

1. 多资产 `history` 主链不对称  
   `stock.price.history` 已进入较完整的标准化与 observation 主链，而 `bond.price.history`、`futures.price.history`、`quote.price.history`、`fund.nav.history-batch` 等更多停留在 generic 路径或宽契约路径。
2. support matrix 与真实能力边界仍有落差  
   某些 capability 已可路由，但是否具备与声明相符的标准化、测试、observation 与错误边界，还没有被系统性定义。
3. `equity.*` 旧语义仍有残留  
   observation 文档串、旧 smoke 测试与少量描述文本仍在泄漏旧命令键，影响后续维护与调试的一致性。

用户现在要求“完整支持”，这意味着下一步不能再只加命令目录，而要让迁移后的关键命令真正成为一等运行时对象。

## Goals / Non-Goals

**Goals:**

- 让迁移后的关键命令族在声明支持的 backend 上都具备真实端到端支持，而不是仅能路由。
- 让 `history` / `live` / `profile` / `flow` / `trades` / `catalog` 等关键命令族拥有稳定契约和明确主链。
- 让多资产 observation / enrichment 支持不再只偏向 `stock` 主链。
- 彻底移除现行 runtime、测试和文档中的 `equity.*` 残留。
- 用测试明确约束“声明支持”和“真实可用”必须一致。

**Non-Goals:**

- 不新增新的用户命令树或新的资产分类。
- 不承诺所有 backend 在所有命令上达到完全 parity；若上游无能力，可通过收紧支持矩阵解决。
- 不把所有列表命令都升级为高度专用 observation 模板；优先保证关键命令族的一等支持。
- 不引入新 provider。

## Decisions

### 决策一：把“完整支持”定义为四层闭环，而不是单点可运行

本次把命令完整支持定义为以下四层同时成立：

1. 命令可通过 CLI 和 request schema 正常进入执行器；
2. provider handler 能调用真实上游并返回稳定标准结果；
3. 结果能进入预期的 enrichment / observation / rendering 路径；
4. 对应 support matrix、测试和文档与真实行为一致。

替代方案：
- 只看 CLI 是否可调用。
- 放弃原因：这正是当前“命令存在但不完整”的问题来源。

### 决策二：按命令家族补齐主链，而不是逐命令散点修补

实现上优先按命令家族收口：

- `price history`
- `price live`
- `profile`
- `flow history/today`
- `trades`
- `catalog`
- `nav history/history-batch`

每个家族定义统一标准化和 observation/enrichment 策略，再把资产差异映射进家族规则。这样比对着单个命令逐个打补丁更可维护。

替代方案：
- 一条命令写一套专用逻辑。
- 放弃原因：会迅速把当前 data-driven catalog 又拉回样板堆。

### 决策三：对关键 history 家族提供一等 observation / enrichment 支持

`stock.price.history` 不能长期成为唯一一条一等 history 主链。此次至少要把 `bond.price.history`、`futures.price.history`、`quote.price.history` 与 `fund.nav.history` / `fund.nav.history-batch` 的支持边界明确化：

- 能共享历史指标与近期事件模板的命令，应进入同一 observation / enrichment 主链；
- 语义明显不同但仍属序列数据的命令，应定义专用但同等级的输出策略；
- 不能继续仅靠 generic records 输出冒充完整支持。

### 决策四：support matrix 必须与测试绑定

provider 声明支持某 capability 的前提是：该 capability 至少有一条对应的定向回归验证其标准结果与错误边界。否则支持矩阵不可信。

替代方案：
- 允许先声明支持，测试后补。
- 放弃原因：当前“看起来支持、其实只是挂上了 handler”就是这么形成的。

### 决策五：把 `equity.*` 残留清理作为显式需求，而不是顺手修文案

这次不把 `equity.*` 残留视为低优先级清理项。它会直接影响：

- observation 元信息键名；
- 历史回补查找逻辑；
- 测试断言与错误诊断；
- 文档和使用心智。

因此它应作为独立能力纳入变更，而不是“实现时顺便搜一遍替换”。

## Risks / Trade-offs

- [风险] history 家族横跨多个资产，标准化差异比 `stock` 单域大。  
  缓解：先按家族定义稳定最小字段，再对资产特有字段保留 provider_fields 或扩展字段。

- [风险] 某些 backend 上游能力本身不足，无法做到真正 parity。  
  缓解：允许收紧支持矩阵，但不允许继续挂着“支持”标签而只有半套实现。

- [风险] observation / enrichment 扩大覆盖面后，测试组合会增长。  
  缓解：重点围绕关键命令家族建立代表性回归，而不是对每条命令复制完整矩阵。

- [风险] 清理 `equity.*` 可能触发旧测试、旧文档和调试工具一起变化。  
  缓解：把 runtime、tests、docs 一并纳入本次范围，不做半迁移。

## Migration Plan

1. 盘点当前声明支持但仍属 route-only / generic-only 的命令家族，形成缺口表。
2. 先补多资产 history 家族的一等标准化与 observation / enrichment 主链。
3. 再补 live/profile/flow/trades/catalog 等关键命令家族的完整运行时支持。
4. 清理 `equity.*` 残留与相关测试/文档。
5. 重新核对 support matrix，只保留真实完整支持的声明。
6. 跑定向回归，确认“声明支持”和“真实实现”一致。

## Open Questions

- `fund.nav.history-batch` 是否应拥有与单标的 history 同等级的 observation 输出，还是维持“多 source 序列视图”即可？当前倾向后者，但要把其定义写清楚。
- `quote.price.history` 是否直接共享 `stock/bond/futures` 的历史观察模板，还是按跨资产通用入口单独约束？当前倾向共享模板，但需要在实现时验证字段稳定性。
