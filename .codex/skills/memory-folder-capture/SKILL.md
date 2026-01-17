---
name: memory-folder-capture
description: 维护 assistant 私有的 memory 文件夹（workspace/memory），用于记录偏好、决策与上下文。适用于需要自动记录内部备注的场景。
---

# Memory 记录（私有）

## 概述

将 assistant 内部备注写入 `workspace/memory/`。内容不面向用户，用于保留偏好与上下文。

## 流程

1. 确保目录存在
   - 若缺失则创建 `workspace/memory/`。

2. 写入备注
   - 推荐追加写入格式（JSONL 或按日期 Markdown）。
   - 保持简短、可扫描。

3. 与 lifelog 区分
   - lifelog 用于任务/操作记录。
   - memory 用于偏好、决策与上下文。

## 备注

- 不记录敏感信息（secrets）。
- 记录描述统一中文。
