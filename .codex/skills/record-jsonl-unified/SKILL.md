---
name: record-jsonl-unified
description: 统一记录 knowledge/lifelog/memory/tasks 的通用 JSONL 记录技巧，支持 auto record 到 lifelog。
---

# 统一 JSONL 记录（knowledge / lifelog / memory / tasks）

## 概述

将“记录类数据”统一为 JSONL（append-only）写入，并确保 UTF-8 无 BOM。支持在写入知识（knowledge）时自动写一条 lifelog（auto record）。

## 适用场景

- 新增或更新 knowledge、lifelog、memory、tasks 等记录类数据
- 希望自动化记录并保持结构统一

## 输入

- record_type：`knowledge` | `lifelog` | `memory` | `tasks`
- data：记录内容（按各自 schema）
- related_files：相关文件路径（可选）
- auto_record：是否自动写入 lifelog（默认：对 knowledge 为 `true`）

## 输出

- 对应 JSONL 文件追加一条记录（append-only）
- 若开启 auto_record，同时写入一条 lifelog 记录

## 统一步骤

1. **确定目标路径**
   - knowledge：`workspace/knowledge/knowledge.jsonl`
   - lifelog：`workspace/lifelog/YYYY/MM/DD.jsonl`
   - memory：`workspace/memory/`（推荐 JSONL 或按日 Markdown）
   - tasks：`workspace/tasks/tasks.jsonl`
2. **生成记录对象**
   - 统一字段建议：`id`、`timestamp`、`source`、`module`、`related_files`
   - 业务字段按 record_type schema 补充
3. **UTF-8 无 BOM 追加写入**
   - 记录必须 append-only
4. **可选：auto record**
   - 当 record_type = knowledge 且 auto_record = true 时，追加一条 lifelog
5. **必要时更新可视化**
   - knowledge：`workspace/tools/knowledge_viewer.html`
   - lifelog/tasks：`workspace/tools/jsonl_viewer.html`

## 字段规范（通用）

- `id`：`YYYY-MM-DD-HHMM-<slug>`
- `timestamp`：ISO8601
- `source`：`conversation` | `from_screenshot`
- `module`：`work` | `personal` | `learning` | `health`
- `related_files`：workspace 内相关路径数组

## 编码规范

- 所有记录文件必须 **UTF-8 无 BOM**

## 自动记录（auto record）

- 默认策略：对 knowledge 写入时开启
- auto record 的 lifelog 描述格式：
  - `新增 knowledge：<title/summary>`

## 注意事项

- JSONL 一行一条记录，不可写多行
- 不记录 secrets
- 记录描述使用中文，字段名可保留英文