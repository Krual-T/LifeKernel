---
name: recorder
description: 统一记录 knowledge/news/lifelog/agent_kernel_memory/tasks 的通用 JSONL 记录技巧，支持新增/更新/删除（CRUD）、UUID 自动 id 与 auto record 到 lifelog。
---

# 统一 JSONL 记录（knowledge / news / lifelog / agent_kernel_memory / tasks）

## 概述

将“记录类数据”统一为 JSONLCRUD，并确保 UTF-8 无 BOM。**所有记录必须遵循 `.codex/schema.json` 的强约束 Schema**。

## 适用场景

- 新增或更新 knowledge、news、lifelog、agent_kernel_memory、tasks 等记录类数据
- 希望自动化记录并保持结构统一

## 输入

- record_type：`knowledge` | `news` | `lifelog` | `agent_kernel_memory` | `tasks` | `update` | `delete`
- update：按 `id + key + value` 查询记录后就地更新（覆盖写入）
- delete：按 `id` 查询记录后删除
- data：记录内容（按各自 schema）
- related_files：相关文件路径（可选）
- auto_record：是否自动写入 lifelog（默认：对 knowledge 为 `true`）

## 输出

- 对应 JSONL 文件追加一条记录（append-only）
- 若开启 auto_record，同时写入一条 lifelog 记录

## 统一步骤

1. **确定目标路径**
   - knowledge：`workspace/records/knowledge/knowledge.jsonl`
   - news：`workspace/records/news/news.jsonl`
   - lifelog：`workspace/records/lifelog/YYYY/MM/DD.jsonl`
   - agent_kernel_memory：`workspace/records/agent_kernel_memory/agent_kernel_memory.jsonl`
   - tasks：`workspace/records/tasks/tasks.jsonl`
2. **生成记录对象**
   - 统一字段必填：`id`、`type`、`timestamp`、`source`、`content`
   - 其他字段按 `.codex/schema.json` 的 record_type 必填/可选项填充
   - `id`：默认自动生成 UUID（`uuid4`），如需手动指定需显式传入
   - 业务字段按 record_type schema 补充
3. **UTF-8 无 BOM CRUD**
   - CRUD必须符合`.codex/schema.json` 的强约束 Schema`
4. **可选：auto record**
   - 当 record_type = knowledge 且 auto_record = true 时，追加一条 lifelog
5. **必要时更新可视化**
   - knowledge/lifelog/tasks：`workspace/view/index.html`
   - news：`workspace/view/news.html`

## 更新记录（CRUD）

用于在 JSONL 中“就地更新/删除”记录：先查询目标记录与所在文件，再读取文件并覆盖写回（保留原有非 JSON 行）。
**注意**：对 `agent_kernel_memory` 的 delete 为**逻辑删除**（写入 `deleted: true`），不进行物理删除。

参数：
- record_type：`update`
- target_type：`knowledge` | `news` | `lifelog` | `agent_kernel_memory` | `tasks`
- id：目标记录 id
- key：需要更新的字段名
- value / value_json：更新值（字符串或 JSON）

示例（PowerShell，更新）：
```powershell
python .\\.codex\\skills\\recorder\\scripts\\record_jsonl.py --record-type update --target-type tasks --id "b3e9c6b0-9f5f-47ff-8d62-1f5f8b7f2a1c" --key status --value "done"
```

```powershell
python .\\.codex\\skills\\recorder\\scripts\\record_jsonl.py --record-type update --target-type knowledge --id "7f5d6f8a-1c3a-4f7e-9e42-2c3e1d6b0e9a" --key tags --value-json "[\"coworker\",\"research\"]"
```

示例（PowerShell，删除）：
```powershell
python .\\.codex\\skills\\recorder\\scripts\\record_jsonl.py --record-type delete --target-type tasks --id "b3e9c6b0-9f5f-47ff-8d62-1f5f8b7f2a1c"
```

## 脚本（推荐）

- `scripts/record_jsonl.py`
  - 统一写入 knowledge/lifelog/agent_kernel_memory/tasks
  - knowledge 默认 auto record 到 lifelog

示例：

Windows（PowerShell）：
```powershell
python .\.codex\skills\recorder\scripts\record_jsonl.py --record-type knowledge --title "Live Preview 目录列表返回反斜杠" --solution "对 href 做 decodeURIComponent 并将 \\ 替换为 /" --tags "lifelog,live-preview" --module work --source conversation
```

```powershell
python .\.codex\skills\recorder\scripts\record_jsonl.py --record-type lifelog --description "整理归档索引" --module work --source conversation --status completed --related-file docs/skills_archive/ARCHIVE_LOG.md
```

Linux（bash）：
```bash
python ./.codex/skills/recorder/scripts/record_jsonl.py --record-type knowledge --title "Live Preview 目录列表返回反斜杠" --solution "对 href 做 decodeURIComponent 并将 \\ 替换为 /" --tags "lifelog,live-preview" --module work --source conversation
```

```bash
python ./.codex/skills/recorder/scripts/record_jsonl.py --record-type lifelog --description "整理归档索引" --module work --source conversation --status completed --related-file docs/skills_archive/ARCHIVE_LOG.md
```

## 字段规范（通用）

- `id`：UUID（`uuid4`）
- `type`：`knowledge` | `news` | `lifelog` | `agent_kernel_memory` | `tasks`
- `timestamp`：ISO8601
- `source`：`conversation` | `from_screenshot`
- `content`：用于统一检索的正文摘要
- `module`：`work` | `personal` | `learning` | `health`（可选）
- `related_files`：workspace 内相关路径数组（可选）

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
