# Lifelog 说明

## 目录结构
- `YYYY/MM/DD.jsonl`: 按日期分文件的操作日志（append-only）

## 推荐写入方式
- 统一使用 `record-jsonl-unified`：
  - Windows（PowerShell）：
    - `python .\.codex\skills\record-jsonl-unified\scripts\record_jsonl.py --record-type lifelog --description "..." --status completed --module work`
  - Linux（bash）：
    - `python ./.codex/skills/record-jsonl-unified/scripts/record_jsonl.py --record-type lifelog --description "..." --status completed --module work`
  - 或统一使用 `uv run`：
    - `uv run python ./.codex/skills/record-jsonl-unified/scripts/record_jsonl.py --record-type lifelog --description "..." --status completed --module work`

## 规则
- JSONL 一行一条记录，append-only。
- 文件编码必须为 UTF-8 无 BOM。
- 描述文本中文优先。
