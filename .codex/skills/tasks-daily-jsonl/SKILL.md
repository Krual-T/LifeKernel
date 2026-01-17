﻿﻿---
name: tasks-daily-jsonl
description: 使用 Markdown 维护进行中任务（workspace/tasks/task_list.md），用 JSONL 记录完成任务（workspace/tasks/task_log/YYYY/MM/DD.jsonl）。适用于新增、更新、完成或查看任务，并以卡片风格展示未完成任务。
---

# 任务清单 + 完成日志

## 概述

进行中任务写入 `workspace/tasks/task_list.md`，完成后追加到 `workspace/tasks/task_log/YYYY/MM/DD.jsonl`。

## 进行中任务（Markdown）

- 文件：`workspace/tasks/task_list.md`
- 规则：一行一条任务（可带详情行）

示例：

```
- [ ] 提交 Q1 报告 (work, high, due 2026-01-18 17:00)
  - 详情：总结 + 附表
- [ ] Review PR-42 (work, medium)
```

## 完成日志（JSONL）

每行一个 JSON 对象。必填字段：
- `id`：稳定任务 ID，`YYYY-MM-DD-HHMM-<slug>`
- `title`：任务标题
- `details`：可选详情
- `status`：固定为 `done`
- `priority`：`low` | `medium` | `high`
- `module`：`work` | `personal` | `learning` | `health`
- `created_at`：ISO8601（含时区）
- `completed_at`：ISO8601（含时区）
- `due_time`：ISO8601 或 null
- `source`：`conversation` | `from_screenshot`
- `related_files`：workspace 相对路径数组（可选）

## 流程

1. 新增任务
   - 追加到 `task_list.md`（勾选框为 `[ ]`）。

2. 更新任务
   - 在 `task_list.md` 中修改标题/优先级/截止时间/详情。

3. 完成任务
   - 在 `task_list.md` 将 `[ ]` 改为 `[x]`。
   - 追加 JSONL 记录到 `task_log/YYYY/MM/DD.jsonl`。

4. 展示未完成任务（卡片）
   - 读取 `task_list.md` 中 `[ ]` 项并渲染卡片。

## 卡片格式

```
[work] 提交 Q1 报告
Status: pending | Priority: high | Due: 2026-01-18 17:00
Details: 总结 + 附表
```

## 备注

- 批量改动或删除前先确认。
- 描述性内容统一中文。

