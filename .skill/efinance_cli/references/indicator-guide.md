# 指标参考

## 1. 本 skill 的默认策略

本 skill 默认推荐：

```bash
--indicator-level full
```

但这只是推荐策略，不是 CLI 程序真实默认值。

CLI 程序真实默认值仍然是：

```bash
--indicator-level basic
```

## 2. 为什么默认推荐 full

因为这个 skill 的目标不是最轻的查询，而是让 agent：

- 尽可能拿到更完整的量化上下文
- 在一次查询里少来回补命令
- 更容易直接解释趋势、波动、量价和支撑阻力

## 3. full 的代价

默认推荐 `full` 的同时，必须提醒：

- 它更慢
- 它更重
- 它更依赖历史回补成功
- 在实时列表 + watch 场景下更容易增加请求压力

如果用户只要轻量结果，应该主动建议：

- `advanced`
- `basic`

## 4. 分级理解

### basic

适合快速看短中期趋势和基础动量：

- MA / EMA
- MACD
- RSI
- KDJ
- BOLL
- ATR
- OBV
- volume_ratio

### advanced

适合进一步看趋势强弱、通道和资金结构：

- ROC
- BIAS
- BBI
- PPO
- TRIX
- TSI
- CCI
- Williams %R
- ADX / DI
- Donchian
- Keltner
- NATR
- SuperTrend
- MFI
- PVT
- CMF
- Force Index
- VWAP
- VR
- PSY

### full

适合做更完整的结构分析：

- Ichimoku
- Parabolic SAR
- Mass Index
- Pivot Points
- Fibonacci Retracement
- rolling support / resistance
- ADL
- Chaikin Oscillator
- Chaikin Volatility
- EMV

## 5. 解释原则

解释任何指标时至少覆盖：

1. 看什么
2. 怎么辅助判断
3. 常见阈值或比较方式
4. 最容易误导的场景

## 6. full 级别最常见的价值

### 趋势结构

- Ichimoku
- SuperTrend
- Parabolic SAR

适合回答：

- 现在是偏多还是偏空
- 趋势有没有延续迹象
- 支撑阻力大概在哪

### 波动与突破

- ATR / NATR
- Donchian
- Keltner
- BOLL
- Chaikin Volatility

适合回答：

- 波动是不是在放大
- 区间是不是在收缩
- 有没有突破环境

### 量价与资金

- OBV
- MFI
- CMF
- ADL
- PVT
- Force Index
- VWAP

适合回答：

- 涨跌有没有量能配合
- 资金是净流入倾向还是净流出倾向
- 当前价相对平均成交成本处于什么位置

### 关键位

- Pivot
- Fibonacci
- support_20 / resistance_20

适合回答：

- 回撤大概看到哪
- 近期区间边界在哪
- 哪些位置更适合作为观察位

## 7. 什么时候不该坚持 full

以下场景应主动考虑降级：

- 用户只要基础字段
- 用户要高频 watch
- 用户在批量扫很多标的
- 上游历史回补经常失败
- 用户只需要结构化导出，不需要技术分析

## 8. 推荐说法

推荐这样表达：

- “程序默认是 `basic`，但这个 skill 默认建议用 `full`，因为它更适合做完整量化解释。”
- “如果你更在意性能或稳定性，可以把 `full` 降为 `advanced` 或 `basic`。”
- “这些指标来自历史回补增强，不是原始实时接口直接返回的字段。”
