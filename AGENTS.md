# LifeKernel｜Codex 执行规范（可拓展范式）

## 1. 角色与边界
1. 项目名称：**LifeKernel**；运行环境：**Windows + Codex CLI**。
2. 目录结构（示例）：
   ```text
   D:\Projects\LifeKernel\
   ├─ workspace\            # 主要工作区
   ├─ .codex\
   │  └─ skills\            # 项目内技能库
   └─ docs\                 # 文档与设计说明
   ```
3. 权限与安全（必须遵守）：
   - 只在以下目录读写：
     - `LifeKernel\workspace\`
     - `LifeKernel\.codex\skills\`
     - `LifeKernel\docs\`
   - 禁止操作系统目录（如 `C:\Windows`、`C:\Program Files`）。
   - 默认使用 `sandbox_mode = "workspace-write"`。
4. 语言：**优先中文**。记录内容（描述性文本）统一中文；字段名可保留英文以便解析。
5. 范式目标：统一“捕获 → 记录 → 组织 → 回溯 → 复用”的闭环，并可持续扩展模块。

---

## 2. 核心目标
1. 统一记录入口：**全部记录类数据使用 `record-jsonl-unified` skill**（knowledge / lifelog / memory / tasks）。
2. 自动捕获可复用流程，沉淀为 skills；并定期审计与改进。
3. **Git 全自动**：在规则允许时自动 `git add/commit/push`。
4. 维护任务、知识、决策、行动日志的上下文，确保可追溯。
5. 从对话或 OCR 文本中识别任务与日程，按模块管理与提醒。
6. 可拓展：新增模块不改变核心范式，仅扩展记录 schema、视图与规则。

---

## 3. 可拓展范式（统一闭环）
**捕获 → 记录 → 组织 → 回溯 → 复用**
- 捕获：从对话、OCR、文件、外部输入识别“任务/知识/决策/想法/行动”。
- 记录：统一调用 `record-jsonl-unified` 写入 JSONL。
- 组织：按模块与标签组织；必要时生成视图文件。
- 回溯：通过 task_list / knowledge 查询 / lifelog 追踪。
- 复用：沉淀为 skills 或流程模板。

---

## 4. 行为规范

### 4.1 对话 → Skill 自动捕获

**Skill 自动调用提示（全局规则）**
- 当用户点名 skill 或请求内容与 skill 适用场景高度匹配时，必须调用对应 skill。
- 多个 skill 同时命中时，先说明使用顺序并按顺序执行。
- 若跳过明显 skill，需说明原因。

- 当出现“重复步骤/明确流程/以后都这样做”等信号时，主动提出：
  - skill 名称
  - 适用场景
  - 可复用步骤
- 用户确认后再创建或更新 `SKILL.md`。

### 4.2 Skills 评估与完善
- 遍历 `.codex/skills` 目录。
- 每个 skill 评分 1–10，并给出简短原因。
- 提供明确的改进清单；用户确认后执行修改。

### 4.3 Git 全自动流程（已授权）
- 当 `.codex/skills` 或 `workspace` 有变更时：
  - 自动执行：`git add` → `git commit` → `git push`
  - commit message 自动生成（简洁、可读）
- 用户可随时说：
  - “暂停自动提交” → 停止自动提交
  - “恢复自动提交” → 继续自动提交

### 4.4 任务与记录规范（统一入口）
**统一入口**：所有记录类数据必须通过 `record-jsonl-unified` 写入；不要手写 JSONL。

#### 4.4.1 任务管理
- **进行中任务**：`workspace/tasks/task_list.md`
- **完成记录**：`workspace/tasks/task_log/YYYY/MM/DD.jsonl`
- 进行中任务用 Markdown 列表；完成后写入 JSONL 归档。
- 展示未完成任务时使用**卡片风格**。

#### 4.4.2 Lifelog（操作记录）
- 路径：`workspace/lifelog/YYYY/MM/DD.jsonl`
- 每完成一个动作自动写入一条记录。
- 记录描述统一中文。

#### 4.4.3 记忆（assistant 私有）
- 路径：`workspace/memory/`
- 用于记录偏好、决策与上下文（仅内部使用）。
- 记录内容统一中文。

### 4.5 知识与想法
- 知识与想法统一写入 `workspace/knowledge/knowledge.jsonl`。
- 头脑风暴/想法记录统一加 `tags: idea, brainstorm`。

### 4.6 视图与可视化
- 需要时更新 `workspace/view/index.html` 或相关视图。
- 视图文件仅作为可读展示，不作为源数据。

### 4.7 提醒规则
- 发现逾期或未完成任务时，主动温和提醒。
- 用户说“今天任务/本周任务/未完成任务”时，按卡片风格展示。

---

## 5. 输出与交互原则
1. 重要操作前仍需简要说明意图与影响。
2. 输出尽量结构化（Markdown 或轻量 JSON）。
3. 关键命令、关键文件路径、关键决策必须清晰可追溯。

---

## 6. 初始化检查（每次会话开始时）
1. 检查 `.codex\skills` 与 `workspace` 是否存在。
2. 提示已存在的 skills 与记录文件（简要概览）。
3. 用 3–5 句话总结：目标理解 + 本次优先事项。
