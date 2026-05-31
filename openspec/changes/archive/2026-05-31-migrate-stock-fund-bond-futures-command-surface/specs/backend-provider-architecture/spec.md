## MODIFIED Requirements

### Requirement: 系统必须通过 provider 显式表达新增命令族的支持矩阵
系统 MUST 把每个数据后端建模为 `BackendProvider`，并由 provider 声明其身份、支持的 capability、扩展命令和 handler 获取方式；在完整命令面迁移后，provider 对新增命令族的覆盖面 MUST 通过显式支持矩阵表达，而 SHALL NOT 通过“命令未迁移”隐式缺失。

#### Scenario: efinance 提供完整首批命令面
- **WHEN** 系统解析迁移后的命令目录
- **THEN** `efinance` provider MUST 为完整首批资产域与 utility 命令提供 handler 或明确的 side-effect 执行路径

#### Scenario: akshare 对部分命令显式不支持
- **WHEN** 用户为仅 `efinance` 支持的迁移命令显式传入 `--backend akshare`
- **THEN** 系统 MUST 在调用前返回明确的支持矩阵冲突错误，而不是让命令缺席
