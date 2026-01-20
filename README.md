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

本项目包含私有记录（`workspace/records`）。**开源仓库仅包含模板与规则**，不承载个人数据。

如果你要使用：
1) 先从开源仓库复制一份 **私有仓库**（如 `LifeKernel-Personal`，名称自定）。
2) 你的私有仓库用于保存 `workspace/records` 及日常变更。

开源仓库只提供框架与示例，不需要也不建议把个人 records 推到 public。
