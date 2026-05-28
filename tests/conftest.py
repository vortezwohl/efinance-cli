"""pytest 级别的测试环境初始化。

该文件确保测试时优先导入当前工作树下的 `efinance_cli` 包，而不是用户环境中已
安装的旧版本同名包，否则会造成命令面、模型定义与渲染逻辑的回归结果失真。
"""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
