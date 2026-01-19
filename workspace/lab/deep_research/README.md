# Deep Research（多智能体工程化方案）

本目录提供一个“可插拔 LLM + 多智能体编排 + 可追溯产出”的最小工程骨架，用于在本地完成深度调研（deep research）任务。默认不依赖第三方库，便于在受限环境运行与二次扩展。

## 目录结构

```text
workspace/lab/deep_research/
├─ run.py                  # 入口脚本
├─ config.example.json     # 示例配置
├─ src/
│  ├─ orchestrator.py       # 编排器：任务拆解、并发与汇总
│  ├─ agents.py             # Agent 规格与输出结构
│  ├─ tools.py              # 工具接口（本地搜索/文件读取/占位 Web）
│  ├─ storage.py            # 产出写入（JSON/Markdown）
│  ├─ prompts.py            # 统一提示模板（可替换）
│  └─ utils.py              # 轻量通用工具
└─ outputs/                 # 每次运行的产出目录
```

## 快速开始

1) 复制配置
```powershell
Copy-Item .\\config.example.json .\\config.json
```

2) 运行（默认 mock provider，不依赖外部 API）
```powershell
python .\\run.py --config .\\config.json
```

3) 产出位置
```
workspace/lab/deep_research/outputs/<run_id>/
  ├─ report.md
  ├─ plan.json
  ├─ findings.json
  └─ run_meta.json
```

## 使用 Codex SDK（多智能体写作）

1) 安装依赖
```powershell
npm install
```

2) 复制 Codex 配置
```powershell
Copy-Item .\\config.codex.example.json .\\config.codex.json
```

3) 运行（Codex SDK）
```powershell
node .\\codex_orchestrator.mjs .\\config.codex.json
```

> 说明：Codex SDK 需 Node.js 18+，认证方式与可用模型请遵循官方文档配置。

## 设计要点

- 多智能体：按角色拆解任务，异步并发执行，再统一汇总。
- 可追溯：每个 agent 产出都会保存为结构化 JSON，最终报告汇总引用。
- 可扩展：LLM 与工具为接口层，可替换为任意模型/检索/搜索实现。

## 如何接入真实 LLM

在 `src/orchestrator.py` 中，默认使用 `MockProvider`。你可以实现自己的 Provider（例如调用内部服务或已有 SDK），只需遵循 `BaseProvider` 接口即可。

## 注意

如需联网搜索，请在 `src/tools.py` 中实现 WebSearchTool（默认占位），并确保合规授权。
