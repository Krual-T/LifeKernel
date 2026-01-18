# Knowledge 规范

## 目录
- 本目录用于存放可读的知识卡片与数据。
- 主要数据文件：`knowledge.jsonl`（一行一条记录，append-only）。

## 推荐写入方式
- 使用统一记录脚本：
  - `python .\.codex\skills\record-jsonl-unified\scripts\record_jsonl.py --record-type knowledge ...`
- 默认开启 auto record：写入 knowledge 时会自动追加一条 lifelog。

## JSONL 字段建议
- id: 字符串，唯一标识
- timestamp: ISO8601
- title: 标题
- summary: 摘要（可选）
- problem: 问题描述
- symptom: 现象
- root_cause: 根因
- solution: 解决方案
- environment: 环境/前提
- tags: 标签数组
- examples: 示例数组

## 约定
- 内容中文优先，便于检索与阅读。
- 可新增字段，但尽量保持向后兼容。