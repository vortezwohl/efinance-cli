## 1. 命令面收敛设计落地

- [x] 1.1 盘点当前 provider-specific 扩展命令的 CLI 路径、支持矩阵和帮助文案，确认需要迁移的用户可见入口。
- [x] 1.2 调整 `efinance_cli/commands.py` 的扩展命令装配方式，移除顶层 provider 根组注册，并改为按业务语义路径挂载扩展命令。
- [x] 1.3 调整现有扩展命令定义的 `cli_path`，使其进入目标业务语义命令树，同时保持现有 `command_key`、capability 和 handler 绑定不变。

## 2. Backend 语义与错误提示收口

- [x] 2.1 复查并固化 provider-specific 扩展命令“不传 `--backend` 时走命令默认 backend”的解析规则。
- [x] 2.2 修改错误 backend 的失败提示，明确该命令支持的 backend、默认路由 backend，以及用户不需要显式传错 backend。
- [x] 2.3 复查帮助文本，确保 provider-specific 命令会展示命令类别与支持 backend，而不会再把 provider 名称当作顶层命令语义。

## 3. 测试与文档迁移

- [x] 3.1 更新 CLI 回归测试，替换旧的 `efinance akshare ...` 路径断言，并覆盖新路径下的默认 backend 与错误 backend 场景。
- [x] 3.2 更新架构和使用文档中的命令树示意、示例命令和 `--backend` 语义说明，删除把 provider 根组当作现行入口的内容。
- [x] 3.3 补充或调整帮助页断言，验证顶层命令面不再直接暴露 provider 根组。

## 4. 定向验证与收尾

- [x] 4.1 运行与扩展命令、backend 解析和 watch 路径直接相关的测试集合，验证统一执行骨架未被破坏。
- [x] 4.2 复查工作区，确认本次改动没有扩散到 handler、结果契约或无关命令语义。
