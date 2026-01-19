---
name: tasks-daily-jsonl
description: 用 JSONL 管理任务，数据存储在 workspace/records/tasks/tasks.jsonl，提供 Python CLI 完成增删改查。
---

# 任务管理（JSONL）

## 概述

`workspace/records/tasks/tasks.jsonl` 作为任务主数据文件，JSONL 每行一条记录（append-only）。

## 字段约定（核心）

- `id`: `YYYY-MM-DD-HHMM-<slug>`
- `title`: 标题
- `details`: 详情（可选）
- `status`: `pending` | `done`
- `priority`: `low` | `medium` | `high`
- `module`: `work` | `personal` | `learning` | `health`
- `created_at`: ISO8601
- `completed_at`: ISO8601 | null
- `due_time`: ISO8601 | null
- `source`: `conversation` | `from_screenshot`
- `related_files`: workspace 内相关路径数组

## 编码要求

- 所有 JSONL 文件必须 **UTF-8 无 BOM**。

## CLI（Python）

使用 `scripts/task_cli.py`：

### 创建

Windows（PowerShell）：
```powershell
python .\scripts\task_cli.py create --title "准备 Q1 报告" --priority high --due-time "2026-01-18T17:00:00+08:00" --module work
```

Linux（bash）：
```bash
python ./scripts/task_cli.py create --title "准备 Q1 报告" --priority high --due-time "2026-01-18T17:00:00+08:00" --module work
```

### 更新

Windows（PowerShell）：
```powershell
python .\scripts\task_cli.py update --id 2026-01-18-0000-send-file --status done
```

Linux（bash）：
```bash
python ./scripts/task_cli.py update --id 2026-01-18-0000-send-file --status done
```

### 删除

Windows（PowerShell）：
```powershell
python .\scripts\task_cli.py delete --id 2026-01-18-0000-send-file
```

Linux（bash）：
```bash
python ./scripts/task_cli.py delete --id 2026-01-18-0000-send-file
```

### 查询

Windows（PowerShell）：
```powershell
python .\scripts\task_cli.py get --id 2026-01-18-0000-send-file
python .\scripts\task_cli.py list --status pending
```

Linux（bash）：
```bash
python ./scripts/task_cli.py get --id 2026-01-18-0000-send-file
python ./scripts/task_cli.py list --status pending
```

## 任务展示

```
[work] 准备 Q1 报告
Status: pending | Priority: high | Due: 2026-01-18 17:00
Details: 资料整理 + 初稿输出
```

## 关联可视化

- `workspace/view/index.html`
- `workspace/records/tasks/tasks.jsonl`

## 注意事项

- append-only，禁止修改既有行。
- 重要字段尽量完整，便于检索。
