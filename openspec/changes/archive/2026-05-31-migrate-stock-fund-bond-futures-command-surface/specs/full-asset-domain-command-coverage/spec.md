## ADDED Requirements

### Requirement: 系统必须提供完整的 stock 域命令面
系统 MUST 在当前多后端命令目录中提供 `stock` 域的首批完整命令面，至少覆盖 `price latest/history/live/snapshot`、`flow today/history`、`trades`、`profile`、`sector`、`constituents`、`holders latest-count/top10`、`ipo latest`、`leaderboard daily`、`performance quarterly`、`report-dates`。

#### Scenario: stock 域暴露价格与资料命令
- **WHEN** 系统构建 `stock` 命令树
- **THEN** 系统 MUST 暴露 `stock price latest`、`stock price history`、`stock price live`、`stock price snapshot` 与 `stock profile`

#### Scenario: stock 域暴露扩展信息命令
- **WHEN** 系统构建 `stock` 命令树
- **THEN** 系统 MUST 暴露 `stock sector`、`stock constituents`、`stock holders latest-count`、`stock holders top10`、`stock ipo latest`、`stock leaderboard daily`、`stock performance quarterly`、`stock report-dates`、`stock trades`、`stock flow today` 与 `stock flow history`

### Requirement: 系统必须提供完整的 fund 域命令面
系统 MUST 在当前多后端命令目录中提供 `fund` 域的首批完整命令面，至少覆盖 `profile`、`catalog`、`managers`、`allocation industry/position/types`、`reports download`、`performance period`、`disclosure dates`、`nav history`、`nav history-batch`、`estimate live`。

#### Scenario: fund 域暴露净值与资料命令
- **WHEN** 系统构建 `fund` 命令树
- **THEN** 系统 MUST 暴露 `fund profile`、`fund catalog`、`fund managers`、`fund nav history` 与 `fund nav history-batch`

#### Scenario: fund 域暴露配置与报告命令
- **WHEN** 系统构建 `fund` 命令树
- **THEN** 系统 MUST 暴露 `fund allocation industry`、`fund allocation position`、`fund allocation types`、`fund estimate live`、`fund performance period`、`fund disclosure dates` 与 `fund reports download`

### Requirement: 系统必须提供完整的 bond 域命令面
系统 MUST 在当前多后端命令目录中提供 `bond` 域的首批完整命令面，而 SHALL NOT 继续让 `bond` 缺席于现行 CLI。

#### Scenario: bond 域暴露核心查询命令
- **WHEN** 系统构建 `bond` 命令树
- **THEN** 系统 MUST 暴露 `bond catalog`、`bond profile`、`bond trades`、`bond flow today`、`bond flow history`、`bond price history` 与 `bond price live`

### Requirement: 系统必须提供完整的 futures 域命令面
系统 MUST 在当前多后端命令目录中提供 `futures` 域的首批完整命令面，而 SHALL NOT 继续让 `futures` 缺席于现行 CLI。

#### Scenario: futures 域暴露核心查询命令
- **WHEN** 系统构建 `futures` 命令树
- **THEN** 系统 MUST 暴露 `futures catalog`、`futures price history`、`futures price live` 与 `futures trades`
