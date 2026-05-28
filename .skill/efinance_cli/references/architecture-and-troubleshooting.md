# 架构与排查参考

## 1. 真实执行链路

`efinance-cli` 的真实链路是：

1. `efinance_cli.main`
2. `efinance_cli.app.create_cli`
3. `efinance_cli.commands`
4. `efinance_cli.registry`
5. `efinance_cli.introspection`
6. `efinance_cli.executor.CommandExecutor`
7. `efinance_cli.enrichment.service.enrich_market_data`
8. `efinance_cli.rendering.render_value`
9. 上游 `efinance.*`

## 1.1 使用前环境检查

在真正调用命令前，先检查系统环境：

1. 是否存在 `python`
2. 是否存在 `efinance` 或 `efinance-cli`

推荐处理：

- 若没有 `python`，直接说明环境不满足，不要继续假设命令可用。
- 若有 `python` 但没有 `efinance` / `efinance-cli`，先执行：

```bash
pip install -U the-efinance-cli
```

- 安装来源参考 [vortezwohl/efinance-cli](https://github.com/vortezwohl/efinance-cli)。
- 安装后再继续检查命令是否可执行。

## 2. 程序真实默认值 vs skill 推荐策略

### 程序真实默认值

- `--format table`
- `--indicator-level basic`

### skill 推荐策略

- 默认建议加 `--format json`
- 默认建议加 `--indicator-level full`

解释时必须显式区分这两者。

## 3. 真实 JSON 输出行为

`--format json` 不是统一响应协议，而是 `render_json(value)`：

- `DataFrame -> to_dict(orient="records")`
- `Series -> to_dict()`
- `dict -> 递归序列化`
- `list/tuple/set -> list`
- dataclass -> `asdict`
- namedtuple -> `_asdict`
- 其他 -> `default=str`

结论：

- 不要伪造固定顶层字段
- 输出结构取决于命令返回值类型

## 4. search 的特殊性

顶层 `search` 不是纯动态命令，而是手写包装：

- 直接调用 `efinance.utils.search_quote`
- 结果会转成 `DataFrame`
- 非 watch 模式直接 `_emit`
- watch 模式会包装成临时 `CommandSpec` 再走统一执行器

因此：

- `search --format json` 的输出本质是候选项 records 数组
- 它不是 `utils search-quote` 的原始 namedtuple 单值输出

## 5. 指标增强的真实范围

只有部分命令会被增强：

- 历史 K 线
- 单标的基础信息/快照
- 最新行情
- 实时列表

不在增强范围内的命令，即使传 `--indicator-level full` 也不会凭空多出指标。

## 6. full 级别意味着什么

`full` 会增加更多回补与计算，包括但不限于：

- Ichimoku
- Parabolic SAR
- Mass Index
- Pivot Points
- Fibonacci Retracement
- rolling support/resistance
- ADL / Chaikin 系列
- EMV

这意味着：

- 查询更重
- 对实时列表更容易触发额外历史请求
- 更适合深度分析，不一定适合极高频 watch

## 7. 常见失败分层

### 参数层

现象：

- 未知参数
- 缺少必填参数
- 枚举值错误
- watch 后没有子命令

处理：

- 先查 `references/command-catalog.json`

### CLI 层

现象：

- 命令存在，但不支持 watch
- search / watch 的包装行为和用户预期不一致

处理：

- 先确认是不是顶层特殊命令

### 上游 efinance / 远端接口层

现象：

- 超时
- 限流
- 空结果
- 字段变化

处理：

1. 原命令重试 1 到 3 次
2. 拉长 watch 间隔
3. 降低指标级别
4. 改走更保守路径：`search -> get-quote-id -> 目标命令`

### 增强层

现象：

- 原始结果有，但指标列缺失
- 单行结果没有被补指标

处理：

1. 确认命令是否在增强范围
2. 确认代码能否提取
3. 确认历史数据能否回补
4. 从 `full` 降到 `advanced` 或 `basic`

### 渲染层

现象：

- 文件输出失败
- 编码问题
- JSON 结构与预期不符

处理：

- 先按真实序列化规则解释，不要按假 schema 解释

## 8. 特殊兼容层

`fund get-base-info` 走的是本地兼容层，不是上游原函数。

原因：

- 为绕过 `pandas>=3` 下字符串 dtype 写回数值导致的类型错误

排查时不要误判成“CLI 改写了业务语义”，它主要是在做兼容性修复。
