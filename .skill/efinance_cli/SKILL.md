---
name: efinance-cli
description: 使用 efinance-cli 查询股票、基金、债券、期货与通用行情，并在需要时解释全部命令、参数、合法值、真实 JSON 输出行为、底层 efinance 实现链路、量化指标含义、故障定位与重试策略。适用于 agent 需要稳定调用 efinance-cli、理解 CLI 与上游 efinance 的关系、以及做量化结果解释与排查的场景。
---

# efinance-cli

使用这个 skill 时，把自己视为熟悉 `efinance-cli` 和上游 `efinance` 的命令专家。

## 核心规则

1. 默认优先让 `efinance-cli` 命令使用 `--format json`。
2. 默认优先让 `efinance-cli` 命令使用 `--indicator-level full`。
3. 使用前必须确保系统里有 `python` 和 `efinance` / `efinance-cli` 命令。
4. 如果系统有 `python` 但没有 `efinance` / `efinance-cli` 命令，优先执行 `pip install -U the-efinance-cli`。
5. 安装来源参考 [vortezwohl/efinance-cli](https://github.com/vortezwohl/efinance-cli)。
6. 必须区分“CLI 程序真实默认值”和“skill 推荐默认策略”。
7. 不得伪造 `efinance-cli` 的 JSON 包装结构。
8. 需要全量命令、参数、合法值时，读取 `references/command-catalog.json`。
9. 需要理解执行链路、真实输出、失败分层与重试策略时，读取 `references/architecture-and-troubleshooting.md`。
10. 需要解释量化指标时，读取 `references/indicator-guide.md`。

## 使用前置检查

在第一次真正使用这个 skill 调命令之前，先检查：

1. 系统里是否有 `python`
2. 系统里是否有 `efinance` 或 `efinance-cli`

处理规则：

- 如果 `python` 不存在，不要继续假设 CLI 可用，先提示环境不满足。
- 如果 `python` 存在，但 `efinance` / `efinance-cli` 不存在，先安装：

```bash
pip install -U the-efinance-cli
```

- 安装完成后，再继续使用 `efinance` / `efinance-cli` 命令。
- 如果两个命令都存在，优先使用当前环境里实际可执行的那个命令名。

## 先讲清两件事实

### 1. CLI 真实默认值

当前程序真实默认值是：

- `--format table`
- `--indicator-level basic`

### 2. skill 推荐默认策略

这个 skill 的推荐策略是：

- 若用户没明确要求其他格式，优先建议加 `--format json`
- 若用户没明确要求更轻量的指标级别，优先建议加 `--indicator-level full`

不要把这两件事说反。

## 真实 JSON 输出规则

`efinance-cli --format json` 输出的是命令返回值本身的序列化结果，不会额外包一层统一状态对象。

真实序列化规则：

- `DataFrame` 输出为 records 数组
- `Series` 输出为 object
- `dict` 递归输出为 object
- `list` / `tuple` / `set` 输出为 array
- dataclass 先 `asdict`
- namedtuple 先 `_asdict`
- `None` 输出为 `null`
- 其他类型按 `default=str`

如果用户问“这个命令的 JSON 长什么样”，应根据返回值类型回答，不要发明固定 schema。

## 默认工作流

### 1. 先定约

先明确：

- 目标市场：`stock` / `fund` / `bond` / `futures` / `common` / `utils`
- 目标动作：搜索、基础信息、实时行情、K 线、资金流、报告下载、市场映射等
- 是否允许副作用：如 `fund get-pdf-reports`、`utils add-market`
- 是否需要 watch
- 是否需要量化指标
- 输出是给人看还是给后续程序消费

### 2. 选命令

推荐顺序：

1. 关键字不清楚时，先 `search` 或 `utils get-quote-id`
2. 已知证券代码时，优先对应市场模块
3. 已知 `quote_id` 或 `fs` 时，再用 `common` / `utils`
4. 需要下载文件或改本地映射时，明确提示副作用

### 3. 组命令

除非用户明确不要，默认推荐：

- `--format json`
- `--indicator-level full`

但要同时说明：

- 这是 skill 推荐值
- 程序真实默认值不是这个

### 4. 校验参数

- 先核对命令路径
- 再核对必填参数
- 再核对合法值
- 日期优先用 `YYYYMMDD`
- 枚举值严格按 `references/command-catalog.json`
- `klt`、`fqt`、`fs`、`ft` 等高频开放参数，优先使用参考目录中的已知合法值

### 5. 解释结果

解释结果时：

- 先说这是原始查询结果还是增强后结果
- 如果用了 `--indicator-level full`，要说明指标来自历史回补增强
- 若用户在做程序消费，优先解释 JSON 结果类型和字段
- 若用户在做人类判断，优先解释关键指标和局限

## 默认命令策略

### 常规查询

默认给出类似这样的命令风格：

```bash
efinance stock get-quote-history 600519 --format json --indicator-level full
```

### 搜索

优先示例：

```bash
efinance search 苹果 --format json
```

### 实时监控

仅当命令支持 watch 时：

```bash
efinance stock get-realtime-quotes --format json --indicator-level full --watch --interval 5
```

### 副作用命令

副作用命令先明确说明风险，再给命令：

```bash
efinance fund get-pdf-reports 161725 --save-dir reports
```

## watch 规则

- 不是所有命令都支持 watch
- `fund get-pdf-reports` 和 `utils add-market` 不支持 watch
- 高频命令配合 `full` 指标时，应主动建议更长间隔
- 若 watch 场景中出现间歇性空结果，先怀疑远端数据源或历史回补失败，不要立即下业务结论

## 量化指标规则

默认推荐 `full`，但解释时必须说明：

- 这是 skill 推荐级别，不是 CLI 实际默认级别
- `full` 的额外成本更高
- 对实时列表命令，`full` 会触发更多历史回补请求
- 若用户只需要轻量判断，可降为 `advanced` 或 `basic`

最低解释要求：

1. 指标看什么
2. 它辅助判断什么
3. 常见阈值或比较方式
4. 最容易误导的场景

## 何时读参考文件

- 全量命令、参数、合法值、watch 支持、副作用：`references/command-catalog.json`
- 执行链路、真实 JSON 输出、默认值与推荐值差异、失败分层、重试：`references/architecture-and-troubleshooting.md`
- 指标解释与 full 级别额外价值：`references/indicator-guide.md`
