# Tasks 说明

## 目录结构
- `tasks.jsonl`: 任务主数据（append-only）
- `task_list.md`: 进行中任务列表（如启用）

## 推荐写入方式
- 统一使用 `record-jsonl-unified`：
  - Windows（PowerShell）：
    - `python .\.codex\skills\record-jsonl-unified\scripts\record_jsonl.py --record-type tasks --title "..." --status pending --priority medium --module work`
  - Linux（bash）：
    - `python ./.codex/skills/record-jsonl-unified/scripts/record_jsonl.py --record-type tasks --title "..." --status pending --priority medium --module work`
  - 或统一使用 `uv run`：
    - `uv run python ./.codex/skills/record-jsonl-unified/scripts/record_jsonl.py --record-type tasks --title "..." --status pending --priority medium --module work`

## 规则
- JSONL 一行一条记录，append-only。
- 文件编码必须为 UTF-8 无 BOM。
- 任务完成后可记录 completed_at 并更新 status。
