---
name: lifelog-daily-jsonl
description: 维护按日期组织的 JSONL lifelog（workspace/lifelog/MM/DD.jsonl）。用于初始化日志目录、追加操作记录或按日期/模块/状态/来源进行查询与汇总。
---

# Lifelog 日志（JSONL）

## 概述

在 `workspace/lifelog/MM/DD.jsonl` 中维护每日 JSONL 日志，每行一条记录，用于保存 Git 之外的操作上下文。

## 流程

1. 写入前确认
   - 若用户未明确要求写入，先征求确认。

2. 确保当日路径存在
   - 根据本地日期生成路径：`workspace/lifelog/MM/DD.jsonl`。
   - 若目录或文件不存在，创建之。

3. 追加记录（JSONL）
   - 每行一个 JSON 对象。
   - 必填字段：
     - `id`：`YYYY-MM-DD-HHMM-<short-slug>`
     - `timestamp`：ISO8601（含时区）
     - `skill_name`：字符串或 null
     - `description`：中文描述
     - `status`：`completed` | `failed` | `pending follow-up`
     - `related_files`：workspace 相对路径数组
     - `module`：`work` | `personal` | `learning` | `health`
     - `source`：`conversation` | `from_screenshot`

示例：

```json
{"id":"2026-01-17-2105-init-lifelog","timestamp":"2026-01-17T21:05:00-05:00","skill_name":null,"description":"初始化 lifelog 目录与当日日志文件","status":"completed","related_files":["workspace/lifelog/01/17.jsonl"],"module":"work","source":"conversation"}
```

4. 查询/汇总
   - 读取指定日期文件。
   - 依据 `module`、`status`、`source` 过滤。
   - 输出简洁摘要（时间 + 描述）。

## 备注

- JSONL 采用追加写入（append-only）。
- 记录描述统一中文。
- 未经请求不要新增额外文件。
