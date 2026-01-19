---
name: news-fetch
description: "Fetch latest news (recent 7 days) for international conflicts, trade policy, China policy, and AI/Agent updates; include specified companies/labs, dedupe against existing news records, and write a single news record via recorder."
---

# News Fetch

用于一次性抓取“最近7天”的重大国际事件/政策/AI Agent 动态，并落库到 `news` 模块。

## 工作流（保持简洁）

1. **确认范围**
   - 默认范围：国际冲突、贸易政策、中国政策、AI/Agent
   - 默认关注实体：OpenAI、Google/DeepMind、阿里、字节、腾讯、智谱、清华相关实验室、幻方量化
   - 若用户提供新增实体或范围，加入 `scope.entities_watch` / `scope.topics`

2. **检索与筛选**
   - 必须使用 `web.run`，时间窗限定最近 7 天（以用户本地日期为准）
   - 优先官方公告/权威媒体/论文平台（官方站点、政府网站、arXiv 等）
   - 记录每条事件的标题、日期、类别、摘要、来源链接、相关实体

3. **去重**
   - 从 `workspace/records/news/news.jsonl` 读取已有记录
   - 以 `title + source + date` 为 key 去重（同类事件只保留最新/最权威来源）
   - 写入 `dedupe` 字段（策略+剔除数量）

4. **写入 news 记录（统一入口）**
   - 使用 `recorder` 脚本：`record_jsonl.py --record-type news`
   - 推荐通过 `--extra` 写入结构化内容

## 推荐记录结构（news）

```json
{
  "type": "news_digest",
  "time_window": { "start": "YYYY-MM-DD", "end": "YYYY-MM-DD", "timezone": "local" },
  "scope": {
    "topics": ["国际冲突","贸易政策","中国政策","AI与Agent"],
    "entities_watch": ["OpenAI","Google/DeepMind","阿里","字节","腾讯","智谱","清华相关实验室","幻方量化"]
  },
  "items": [
    {
      "title": "...",
      "date": "YYYY-MM-DD",
      "category": "国际冲突|贸易政策|中国政策|AI公司|AI/Agent研究",
      "summary": "...",
      "sources": [{"name":"...","url":"..."}],
      "entities": ["..."]
    }
  ],
  "source_updates": [{"name":"...","domain":"...","added":"YYYY-MM-DD"}],
  "dedupe": { "strategy": "title+source+date", "dropped": 0 },
  "coverage_gap": ["..."]
}
```

## 记录示例（PowerShell）

```powershell
$extra = @'
{"type":"news_digest","time_window":{"start":"2026-01-13","end":"2026-01-19","timezone":"local"},"scope":{"topics":["国际冲突","贸易政策","中国政策","AI与Agent"],"entities_watch":["OpenAI","Google/DeepMind","阿里","字节","腾讯","智谱","清华相关实验室","幻方量化"]},"items":[],"dedupe":{"strategy":"title+source+date","dropped":0}}
'@
python .\\.codex\\skills\\recorder\\scripts\\record_jsonl.py --record-type news --title "新闻扫描（最近7天）" --summary "本次新闻扫描概览。" --tags "news,international,policy,ai,agent" --module "news" --source "web" --extra $extra
```
