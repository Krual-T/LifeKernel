# LifeKernel

## 项目简介

LifeKernel 是一个面向个人知识沉淀、任务管理与行为自动化的数字管家内核。它将“捕获 → 记录 → 组织 → 回溯 → 复用”统一为可扩展的 Skills 与规范化 JSONL 数据流，支持：

- 统一记录入口（knowledge / news / lifelog / agent_kernel_memory / tasks）
- 任务与日志可追溯、可检索
- 技能沉淀与可复用流程
- 视图展示（仅展示，不作为源数据）

## Windows 中文乱码说明（已提供修复脚本）

乱码的核心原因是**终端编码与编辑器编码不一致**。需要同时确保 VS Code 与终端都使用 UTF-8（无 BOM），中文才能稳定不乱码。项目已提供修复脚本：

- Windows：`fix_garbled_characters.ps1`
- Linux：`fix_garbled_characters.sh`

PowerShell 执行方式（建议 PowerShell 7）：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\fix_garbled_characters.ps1
```

VS Code 建议设置（`settings.json`）：

```json
{
  "files.encoding": "utf8",
  "files.autoGuessEncoding": true
}
```

参考阅读（请先读）：
```text
https://www.cnblogs.com/gccbuaa/p/19227315
```

## 开源与隐私

本项目包含私有记录（`workspace/records`）。为同时保留私有记录历史并开源代码，采用**双远端**：

- `origin`：私有仓库（包含完整 `workspace/records`）
- `public`：开源仓库（**必须剔除** `workspace/records`）

自动提交仅推送 `origin`。除非明确指令“发布开源/同步 public”，否则禁止推送 `public`。

## 一次性配置（仅第一次需要）

1) 添加 public 远端

```powershell
git remote add public https://github.com/<you>/LifeKernel.git
```

2) 安装 filter-repo（用于生成不含 records 的发布分支）

```powershell
uv add git-filter-repo
```

## 发布开源（每次需要公开时执行）

以下流程会生成一个不含 `workspace/records` 的发布分支并推送到 `public`。

```powershell
# 1) 确保本地是最新的私有主分支
git checkout main
git pull origin main

# 2) 创建/更新发布分支（从私有主分支复制）
git branch -f <public_branch_name> main

# 3) 在发布分支中移除 records（改写历史）
git checkout <public_branch_name>
git filter-repo --path workspace/records --invert-paths --force

# 4) 推送到 public
git push public <public_branch_name> --force

# 5) 切回私有主分支继续工作
git checkout main
```

说明：
- `<public_branch_name>` 是发布用分支，**只用于推送 public**。
- `git push public <public_branch_name>` 表示将同名分支推送到 `public` 远端。
- 该流程会重写发布分支历史，不影响私有 `main`。

## 注意事项

- 开源仓库中不会包含任何真实 `workspace/records` 数据。
- 私有记录仍在 `origin` 保持完整历史与变更。
