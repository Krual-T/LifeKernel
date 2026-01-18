# Knowledge 规范

## 目录
- 本目录用于存放可读的知识卡片与数据。
- 主要数据文件：`knowledge.jsonl`（一行一条记录，append-only）。

## JSONL 字段建议
- id: 字符串，唯一标识
- timestamp: ISO8601
- title: 标题
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

