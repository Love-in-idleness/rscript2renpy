# 项目工作约定

## 开始工作

- 使用 `rg` 搜索源码。先检查 `git status --short`，保留已有修改与未跟踪资源。
- 阅读 `README.md`；公共层改动参考 `docs/SHARED_TEMPLATE_MIGRATION.md`，文字布局改动参考 `docs/TEXT_WRAPPING.md`。
- 本机路径集中在被 Git 忽略的 `local.paths.toml`。使用前检查路径存在及资源格式；配置记录位置，不证明资源已完整转换。
- 路径配置格式见 `local.paths.example.toml`，读取方式与权限加载说明见 `docs/LOCAL_WORKFLOW.md`。
- 项目级 Codex 权限在 `.codex/config.toml`；保存配置不代表当前聊天已重新加载权限。

## 修改归属

- 通用指令、图层、音频和文字运行时放在 `runtime/`；共享构建、资源及界面放在 `port_template/`。
- 游戏方言和专用行为留在 `forest/`、`khime/` 的生成器或 `game/` 覆盖层。
- 持久修复必须修改仓库源码，再由生成器同步目标工程；不要只改生成工程，或对复制后的公共运行时做字符串替换。
- 公共能力改动同时检查 Forest 与 Khime；生成前确认资源、语言补丁、输出路径和已有手工修改。Forest 会覆盖生成文件，Khime 的 `--force` 只能用于确认可以覆盖的目标。
- 原版及语言补丁资源只读使用。游戏资源、生成工程、存档和签名密钥不得提交。
- 不支持的效果在对应转换处扁平化，并用生成注释保留原值和原因。未知 opcode 不凭空补全语义，记录证据与未确认部分。
- 界面修复先查看原图或用户截图，复用现有视觉控件和布局。

## 验证

- 按改动选择相关检查，不为纯文档或路径配置改动运行游戏测试。
- 基础检查：`python3 -B tests/test_runtime.py`、`python3 -B tests/test_port_template.py`、`git diff --check`。
- 公共层：`python3 -B tests/test_shared_port.py`；需要真实 SDK 检查时追加本机配置中的 SDK 路径。
- Forest：`python3 -B tests/test_forest_builder.py <资源目录>`、`python3 -B tests/test_forest_validation.py`；资源检查先查看 `tests/test_forest_resources.py --help`。
- Khime：`python3 -B tests/test_khime_builder.py <资源目录>`。
- 文字：`python3 -B tests/test_text_wrap.py`；SDK 内部接口或布局改动还需 `python3 -B tests/run_native_text_wrap.py <SDK目录>`。
- 触屏控制：`python3 -B tests/run_touch_controls.py <SDK目录>`。独立测试工程使用临时存档，不操作正式游戏进度。
- 同步完整工程后执行 `<SDK目录>/renpy.sh <工程目录> lint`。SDK 升级后重跑相关原生测试。
- 实际游戏画面、音频、路线、旧存档和安卓实机验证由用户完成；未经明确请求不启动正式游戏。独立自动测试只能证明其覆盖的行为。
- 分开报告静态检查、自动测试、lint、人工验证；说明未运行的检查和既有失败，不把 lint 当作完整游玩证明。

## Git 与权限

- 提交只包含当前任务的文件；不要混入已有改动。每项独立任务验证后及时本地提交，未明确要求不推送。
- 按当前 README 维护源码，不创建新的 GitHub Release 或版本包。
- 优先使用当前合适的 checkout；需要新分支时使用 `codex/` 前缀。
- 管理员权限操作须先说明目的和具体命令并获得授权。不要通过其他工具绕过目录权限。
