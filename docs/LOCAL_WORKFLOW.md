# 本机路径与项目权限

`AGENTS.md` 保存项目约定。`local.paths.example.toml` 保存可提交的路径配置格式；
本机填写后的 `local.paths.toml` 和 `.codex/config.toml` 被 Git 忽略。

这份本机路径配置同时供 LiarsoftTool 与 rscript2renpy 使用。`tools` 中记录两个
源码仓库、LiarsoftTool 构建目录及 CLI/GUI、Ren'Py SDK；两仓库各有自己的
`AGENTS.md`，跨仓库修改时都要阅读。不要复制本机路径配置形成两份独立来源。
在 LiarsoftTool 中，可用 `../rscript2renpy/local.paths.toml` 定位当前机器的配置。

LiarsoftTool 代码改动使用 `tools.liarsofttool_build` 构建并执行 CTest。
资源预处理在工作副本中进行，使用 `tools.liarsofttool_cli`；保留原版与补丁原件。
GSC/TSC、编码或资源格式变化时先验证工具输出，再在 rscript2renpy 中检查相关
解析、生成、共享模板及完整工程 lint。两仓库的构建产物和本机资源均不纳入 Git。

路径配置仅记录工具、输入、补丁和输出的位置，不会自动改变生成器参数。
空字符串表示尚未配置。新机器先复制示例文件，再填入绝对路径；不要把本机
资源目录写死进生成器。原版及补丁目录只读使用，生成结果写入配置的工程目录。

Python 3.11 及以上可用标准库读取配置。例如，给现有 Forest 工程执行 lint：

```bash
python3 - <<'PY'
from pathlib import Path
import subprocess
import tomllib

paths = tomllib.loads(Path("local.paths.toml").read_text(encoding="utf-8"))
sdk = Path(paths["tools"]["renpy_sdk"])
project = Path(paths["forest"]["project"])
subprocess.run([str(sdk / "renpy.sh"), str(project), "lint"], check=True)
PY
```

构建时使用相同方式取 `resources` 和 `project`，作为生成器的两个位置参数。
原版标签取 `base_language`；明确选定需要启用的补丁后，才传入
`--language NAME=PATCH_DIR`。不要自动加入配置中所有补丁，或传入空路径。
重建现有工程前检查是否存在手工修改，遵守生成器的覆盖规则。

本机 Codex 项目配置使用：

```toml
sandbox_mode = "workspace-write"

[sandbox_workspace_write]
writable_roots = ["/home/idleness/Source/LiarsoftTool", "/home/idleness/Source/renpy"]
```

上面是 rscript2renpy 的配置。LiarsoftTool 的同名配置将额外根目录换成
`/home/idleness/Source/rscript2renpy` 和 `/home/idleness/Source/renpy`。
两个配置均只追加协作仓库与 Ren'Py 输出目录的写权限，保持其余审批及网络设置。
Codex 必须重新加载项目配置才会采用它；保存文件不会改写正在运行的聊天所持有的
权限快照。重新打开项目或启动新聊天后，检查权限上下文中是否包含该目录；
若应用仍覆盖此设置，以实际权限上下文为准，不通过工具绕过限制。

新本机配置已检查路径存在，但这不证明资源完整或与工程完全对应。
Khime 中文补丁来源尚未确认，`khime.patches.zh` 保持空值。

配置键及受信任项目的加载规则见
[Codex 官方配置说明](https://learn.chatgpt.com/docs/config-file/config-reference)。
