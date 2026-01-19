---
name: lifelog-daily-jsonl
description: 以 JSONL 方式记录 lifelog 到 workspace/records/lifelog/YYYY/MM/DD.jsonl，按日期分文件，便于追踪与归档。
---

# Lifelog 日志（JSONL）

## 概述

将操作日志按日期追加写入 `workspace/records/lifelog/YYYY/MM/DD.jsonl`，每行一条记录（append-only）。

## 记录规则

- 每条记录必须包含 timestamp（ISO8601）。
- 以日期分文件：当天所有记录都写入对应 `YYYY/MM/DD.jsonl`。
- 文件编码必须为 **UTF-8 无 BOM**。

## 记录方式（Python 脚本）

- 使用 `scripts/append_lifelog.py`
- 常用参数：
  - `--description` 描述
  - `--timestamp` ISO8601（可选，默认当前时间）
  - `--id` 自定义 id（可选）
  - `--module` 例如 `work`
  - `--skill-name` 触发的 skill 名称
  - `--source` 例如 `conversation`
  - `--status` 例如 `completed`
  - `--related-files` 相关文件（workspace 内路径）

Windows（PowerShell）：
```powershell
python .\scripts\append_lifelog.py --description "修复 UTF-8 无 BOM" --module work --skill-name lifelog-daily-jsonl --related-files workspace/records/lifelog/2026/01/18.jsonl
```

Linux（bash）：
```bash
python ./scripts/append_lifelog.py --description "修复 UTF-8 无 BOM" --module work --skill-name lifelog-daily-jsonl --related-files workspace/records/lifelog/2026/01/18.jsonl
```

## JSONL 字段建议

- `id`: `YYYY-MM-DD-HHMM-<slug>`
- `timestamp`: ISO8601
- `skill_name`: 触发 skill（可为空）
- `description`: 描述
- `status`: `completed` | `failed` | `pending follow-up`
- `related_files`: workspace 内相关路径数组
- `module`: `work` | `personal` | `learning` | `health`
- `source`: `conversation` | `from_screenshot`

## 注意事项

- JSONL 一行一条记录，append-only。
- 避免记录敏感信息。
- 记录描述使用中文，字段名可保留英文。
