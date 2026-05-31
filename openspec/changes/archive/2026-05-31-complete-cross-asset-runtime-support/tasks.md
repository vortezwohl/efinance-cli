## 1. Gap Audit And Support Definition

- [x] 1.1 盘点迁移后命令中仍然只是 route-only、generic-only 或残留 `equity.*` 语义的 capability，形成缺口清单。
- [x] 1.2 明确“完整支持”的判定标准，并把它映射到 `history` / `live` / `profile` / `flow` / `trades` / `catalog` / `nav` 等关键命令家族。
- [x] 1.3 复查当前 support matrix 与真实实现差异，确定需要补实现的命令与需要收紧声明的 backend。

## 2. Cross-Asset History Runtime Support

- [x] 2.1 扩展 `providers.py` 与 `contracts.py`，为 `bond.price.history`、`futures.price.history`、`quote.price.history`、`fund.nav.history-batch` 等命令补齐稳定标准化结果。
- [x] 2.2 扩展 `enrichment/service.py`，让关键 history 家族进入明确的一等增强路径，而不是只支持 `stock.price.history`。
- [x] 2.3 扩展 `observation.py`，为多资产 history 家族补齐稳定 observation 输出或多 source 序列策略。

## 3. Key Command Family Parity

- [x] 3.1 复查并补齐 `live` / `profile` 命令家族的结果契约与 observation / enrichment 一致性。
- [x] 3.2 复查并补齐 `flow` / `trades` / `catalog` 命令家族的完整运行时支持，避免长期停留在宽兜底但无约束状态。
- [x] 3.3 收紧 provider 支持矩阵，只为真实完整实现的 capability 保留 supported 声明。

## 4. Legacy Equity Removal

- [x] 4.1 清理 runtime 中残留的 `equity.*` 命令键、注释和补充逻辑，统一到 `stock.*`。
- [x] 4.2 清理测试中的 `equity.*` 断言与旧路径基线，改为现行稳定命令键。
- [x] 4.3 清理文档和设计说明中的 `equity` 现行语义残留。

## 5. Verification

- [x] 5.1 为多资产 `history` / `live` / `profile` 关键主链补齐定向回归测试。
- [x] 5.2 为 support matrix 与真实实现一致性补齐 provider / resolver 回归测试。
- [x] 5.3 使用 `.venv\Scripts\python.exe -m pytest` 运行与本次变更直接相关的测试集合，记录剩余风险。
