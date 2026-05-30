# efinance-cli 设计与使用说明

## 1. 文档定位

本文档说明当前版本 `efinance-cli` 的命令组织方式、后端选择语义与迁移边界。

当前版本已经不再把 CLI 视为 `efinance` 上游函数的自然语言包装，而是逐步重构为：

- 以后端无关的共享命令为主；
- 以 provider 扩展命令补充后端特有能力；
- 以统一请求 schema、统一结果契约和统一执行骨架承载运行时行为。

这意味着用户需要优先理解“能力”和“命令语义”，而不是去记忆某个第三方库的函数名。

## 2. 当前命令模型

当前 CLI 处于迁移期，同时存在三类命令：

1. 共享命令  
   面向稳定业务语义，命令入口和参数定义尽量与具体后端解耦。

2. provider 扩展命令  
   保留后端专属能力，不强行压成共享最小公分母。

3. 旧函数驱动命令  
   仍然存在于命令树中，用于迁移过渡；但它们不再是后续架构演进的核心对象。

## 3. 顶层命令树

当前用户可见的顶层入口包含：

```text
efinance
├─ search
├─ watch
├─ stock
├─ fund
├─ bond
├─ futures
├─ quote
├─ market
├─ resolve
├─ instrument
├─ equity
└─ akshare
```

说明：

- `search` 是共享命令 `instrument.search` 的顶层快捷入口；
- `instrument`、`equity`、`fund` 中的共享命令逐步进入新的 capability 架构；
- `stock`、`bond`、`futures`、`quote`、`market`、`resolve` 仍包含较多旧函数驱动命令；
- `akshare` 是 provider 扩展命令根组，用于承载 `akshare` 特有能力；
- `watch` 是统一的循环刷新包装命令，会复用同一条请求解析与执行链路。

## 4. 共享命令与 provider 扩展命令

### 4.1 共享命令

共享命令的目标是为相同业务能力提供稳定入口。当前已经落地的共享命令如下：

| 命令键 | CLI 路径 | 说明 | 支持后端 |
| --- | --- | --- | --- |
| `instrument.search` | `search` / `instrument search` | 搜索证券候选项 | `efinance`、`akshare` |
| `equity.price.history` | `equity price history` | 权益类历史行情 | `efinance`、`akshare` |
| `equity.price.live` | `equity price live` | 权益类实时行情列表 | `efinance`、`akshare` |
| `equity.profile` | `equity profile` | 权益类基础资料 | `efinance`、`akshare` |
| `fund.nav.history` | `fund nav history` | 基金净值历史 | `efinance`、`akshare` |

共享命令的共同特征：

- 参数来自显式 request schema，而不是第三方函数签名反射；
- 帮助页会显示命令键、能力标识、支持后端与命令类别；
- 非 raw 视图会进入统一的标准化、增强、observation 与渲染管线；
- raw 视图会保留 `raw_payload`、`provider_fields`、`metadata` 等 provider 原始上下文。

### 4.2 provider 扩展命令

provider 扩展命令用于保留特定后端独有能力。当前已经落地的示例是：

```bash
efinance akshare industry boards
```

该命令表示：

- 命令语义属于 `akshare` 专属扩展；
- 它不伪装成跨后端共享能力；
- 仍然复用统一执行骨架与结果契约；
- 错误地显式指定其他 backend 时，会明确失败，而不是静默降级。

未来 `yfinance` 若接入，也会遵循同样的扩展命令挂载方式。

## 5. `--backend` 语义

`--backend` 是共享命令和 provider 扩展命令的统一后端选择参数。

### 5.1 共享命令

共享命令支持显式传入 `--backend`：

```bash
efinance equity price history --symbol 600519 --backend efinance
efinance equity price history --symbol 600519 --backend akshare
efinance fund nav history --symbol 161725 --backend akshare
```

规则如下：

- 不传 `--backend` 时，默认使用 `efinance`；
- 显式传入的 backend 必须在该命令的支持矩阵内；
- 不受支持的 backend 会直接报错，不会偷偷回退到默认后端。

### 5.2 provider 扩展命令

provider 扩展命令也接受 `--backend`，但其默认行为不同：

```bash
efinance akshare industry boards
efinance akshare industry boards --backend akshare
```

规则如下：

- 不传 `--backend` 时，默认解析到所属 provider；
- 显式传入相同 provider 允许执行；
- 显式传入其他 provider 会明确失败。

## 6. 统一运行时参数

共享命令与 provider 扩展命令统一支持以下运行时参数：

- `--backend`
- `--format table|json|csv|tsv`
- `--full`
- `--transpose`
- `--no-index`
- `--limit N`
- `--output PATH`
- `--encoding utf-8`
- `--indicator-level basic|advanced|full`
- `--view raw|observation`
- `--trace-window N`
- `--watch`
- `--interval FLOAT`
- `--count INT`
- `--clear/--no-clear`

说明：

- `--view raw` 适合调试 provider 差异、核对原始字段和扩展字段；
- `--view observation` 适合统一阅读结构化观察结果；
- `watch` 顶层包装命令与命令内 `--watch` 会复用同一请求对象和同一 backend 解析逻辑；
- `--count` 仅表示刷新次数，不表示业务记录数量。

## 7. 当前推荐用法

### 7.1 共享搜索

```bash
efinance search --query 贵州茅台
efinance instrument search --query 腾讯 --backend akshare --format json
```

### 7.2 权益类历史与实时

```bash
efinance equity price history --symbol 600519 --start-date 20250101 --end-date 20250501
efinance equity price history --symbol 600519 --backend akshare --view raw --format json
efinance equity price live --backend efinance --record-limit 20
efinance watch --interval 3 equity price live --backend akshare --record-limit 10
```

### 7.3 权益类资料与基金净值

```bash
efinance equity profile --symbol 000001
efinance equity profile --symbol 000001 --backend akshare --view raw
efinance fund nav history --symbol 161725
efinance fund nav history --symbol 161725 --backend akshare --format json
```

### 7.4 provider 扩展能力

```bash
efinance akshare industry boards
```

## 8. BREAKING 变化

当前版本相对于旧的函数驱动 CLI，有以下重要变化：

1. 命令稳定对象已经从“第三方函数”转为“命令键 + capability + request schema”。
2. 共享命令的参数定义不再承诺与 `efinance` 上游函数签名一一对应。
3. 同一业务命令在不同后端下允许存在字段完整度差异，但会努力满足相同核心结果契约。
4. provider 特有能力不再强行伪装成通用命令，而是挂到各自扩展命令根组。
5. `--backend` 选择失败时会显式报错，不再依赖隐式兼容或静默回退。

## 9. 迁移期边界

当前版本仍是迁移中的过渡态，需要明确以下边界：

- 并非所有旧命令都已迁移到共享 capability 架构；
- 旧函数驱动命令仍可使用，但不建议把它们当作长期稳定接口；
- `yfinance` 目前仅预留 optional provider 挂载点，尚未实现具体能力；
- 某些 observation 与 enrichment 路径仍同时兼容旧结果形态与新标准契约。

如果你在扩展新命令，应优先判断它属于：

- 共享能力；
- provider 专属扩展；
- 还是仅用于迁移过渡的旧路径兼容。

不要再把新的用户能力直接绑定到第三方函数名上。
