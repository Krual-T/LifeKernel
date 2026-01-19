---
name: news-fetch
description: "Search and archive significant global events (7-day window). Topics: international conflicts, trade/China policy, and AI/Agent updates. Include entity tracking, semantic dedupe against news.jsonl, and atomic archival via recorder."
---

# News Fetch

用于一次性抓取“最近7天”的重大国际事件/政策/AI Agent 动态，并落库到 `news` 模块。

## 工作流（保持简洁）

1. **动态日期锚定**
   - 以系统当前日期为 T，窗口为 T-7 至 T（含首尾）

2. **确认范围**
   - 默认范围：国际冲突、贸易政策、中国政策、AI/Agent（含公司/实验室/论文）
   - 默认关注实体：OpenAI、Google/DeepMind、阿里、字节、腾讯、智谱、清华相关实验室、幻方量化
   - 若用户提供新增实体或范围，加入 `scope.entities_watch` / `scope.topics`

3. **多路并行检索（按 Topic 拆分 Query）**
   - 必须使用 `web.run`，时间窗限定最近 7 天
   - 每个 topic 单独构建查询，避免热点霸屏
   - AI 领域优先：公司官方博客/研究发布 + arXiv
   - 政策领域优先：政府官网/央行/监管机构/权威媒体

4. **语义去重（Smart Dedupe）**
   - 读取 `workspace/records/news/news.jsonl` 历史记录
   - 由 AI 判断是否为同一事件（允许标题/日期轻微差异）
   - 来源权威度更高者优先保留
   - 写入 `dedupe` 字段（策略+剔除数量）

5. **原子化写入（Atomic Storage）**
   - 每条新闻单独写一条 `news` 记录（便于检索/RAG）
   - 不写 `news_digest`，仅保留原子化条目
   - 使用 `recorder` 脚本：`record_jsonl.py --record-type news`
   - 推荐通过 `--extra` 写入结构化内容

6. **News Fetch 自用 TODO**
   - 每次调用 News Fetch，都先在 `workspace/records/tasks/task_list.md` 创建本次抓取的 TODO 清单
   - 清单至少包含：分 Topic 检索、去重、写入 news、补充 coverage_gap、产出摘要

## 推荐记录结构（news）

```json
{
  "type": "news_item",
  "date": "YYYY-MM-DD",
  "category": "AI 自动判定（可随主题变化）",
  "summary": "...",
  "sources": [{"name":"...","url":"..."}],
  "entities": ["..."],
  "source_rank": "official|media|preprint"
}
```

## 记录示例（PowerShell）

```powershell
$extra = @'
{"type":"news_digest","time_window":{"start":"2026-01-13","end":"2026-01-19","timezone":"local"},"scope":{"topics":["国际冲突","贸易政策","中国政策","AI与Agent"],"entities_watch":["OpenAI","Google/DeepMind","阿里","字节","腾讯","智谱","清华相关实验室","幻方量化"]},"items":[],"dedupe":{"strategy":"title+source+date","dropped":0}}
'@
python .\\.codex\\skills\\recorder\\scripts\\record_jsonl.py --record-type news --title "新闻扫描（最近7天）" --summary "本次新闻扫描概览。" --tags "news,international,policy,ai,agent" --module "news" --source "web" --extra $extra
```
