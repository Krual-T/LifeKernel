# Memory 说明

## 目录结构
- `memory.jsonl`: assistant 私有记忆（append-only）

## 推荐写入方式
- 统一使用 `record-jsonl-unified`：
  - Windows（PowerShell）：
    - `python .\.codex\skills\record-jsonl-unified\scripts\record_jsonl.py --record-type memory --summary "..." --module work`
  - Linux（bash）：
    - `python ./.codex/skills/record-jsonl-unified/scripts/record_jsonl.py --record-type memory --summary "..." --module work`
  - 或统一使用 `uv run`：
    - `uv run python ./.codex/skills/record-jsonl-unified/scripts/record_jsonl.py --record-type memory --summary "..." --module work`

## 规则
- JSONL 一行一条记录，append-only。
- 文件编码必须为 UTF-8 无 BOM。
- 内容统一中文，避免记录敏感信息。
