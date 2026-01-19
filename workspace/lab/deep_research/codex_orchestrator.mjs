import fs from "node:fs";
import path from "node:path";
import { Codex } from "@openai/codex-sdk";

const PLANNER_PROMPT = `你是研究规划员。
主题：{topic}
请输出 JSON：
{
  "scope": "...",
  "questions": ["...", "..."],
  "exclusions": ["...", "..."]
}
`;

const EVIDENCE_PROMPT = `你是证据整理员。
主题：{topic}
研究问题：{questions}
请输出要点列表（条目式），并引用本地材料要点。`;

const COUNTERPOINT_PROMPT = `你是反例分析员。
主题：{topic}
研究问题：{questions}
请指出主要不足、风险、反例与争议点。`;

const SYNTHESIS_PROMPT = `你是综合写作者。
主题：{topic}
研究问题：{questions}
已收集材料：
{materials}
请输出结构化报告（概览/发现/不足/建议）。`;

function loadConfig(configPath) {
  const raw = fs.readFileSync(configPath, "utf-8");
  return JSON.parse(raw);
}

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function writeJson(filePath, data) {
  ensureDir(path.dirname(filePath));
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2), "utf-8");
}

function writeReport(filePath, sections) {
  ensureDir(path.dirname(filePath));
  const content = sections.filter((s) => s && s.trim()).join("\n\n");
  fs.writeFileSync(filePath, content + "\n", "utf-8");
}

function render(template, vars) {
  return template.replace(/\{(\w+)\}/g, (_, key) => String(vars[key] ?? ""));
}

function extractText(result) {
  if (typeof result === "string") return result;
  if (result && typeof result === "object") {
    if (typeof result.output_text === "string") return result.output_text;
    if (typeof result.text === "string") return result.text;
    if (typeof result.result === "string") return result.result;
  }
  return JSON.stringify(result, null, 2);
}

function tryParsePlan(text) {
  try {
    return JSON.parse(text);
  } catch {
    const match = text.match(/\{[\s\S]*\}/);
    if (match) {
      try {
        return JSON.parse(match[0]);
      } catch {
        return null;
      }
    }
    return null;
  }
}

function normalizeIgnores(root, ignores) {
  return (ignores || [])
    .filter(Boolean)
    .map((item) => {
      const p = path.isAbsolute(item) ? item : path.join(root, item);
      return path.normalize(p).toLowerCase();
    });
}

function isIgnored(dirPath, ignores) {
  const norm = path.normalize(dirPath).toLowerCase();
  return ignores.some((ignore) => norm.startsWith(ignore));
}

function localSearch(config, query) {
  const root = config.root || ".";
  const maxFiles = config.max_files ?? 200;
  const maxBytes = config.max_bytes ?? 1_000_000;
  const ignores = normalizeIgnores(root, config.ignore || []);
  const items = [];
  let count = 0;

  function walk(dir) {
    if (count >= maxFiles) return;
    if (isIgnored(dir, ignores)) return;
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      if (count >= maxFiles) return;
      if (entry.name.startsWith(".")) continue;
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        if ([".git", ".venv", "__pycache__"].includes(entry.name)) continue;
        walk(fullPath);
        continue;
      }
      try {
        const stat = fs.statSync(fullPath);
        if (stat.size > maxBytes) continue;
        const text = fs.readFileSync(fullPath, "utf-8");
        if (text.toLowerCase().includes(query.toLowerCase())) {
          items.push({
            path: fullPath,
            snippet: snippet(text, query),
          });
          count += 1;
        }
      } catch {
        continue;
      }
    }
  }

  walk(root);
  return { tool: "local_search", items };
}

function snippet(text, query, window = 80) {
  const idx = text.toLowerCase().indexOf(query.toLowerCase());
  if (idx < 0) return "";
  const start = Math.max(idx - window, 0);
  const end = Math.min(idx + query.length + window, text.length);
  return text.slice(start, end).replace(/\s+/g, " ").trim();
}

async function run() {
  const configPath = process.argv[2] || "";
  if (!configPath) {
    console.error("Usage: node codex_orchestrator.mjs <config.json>");
    process.exit(1);
  }

  const config = loadConfig(configPath);
  const topic = config.topic;
  const agents = config.agents || [];
  const outputDir = config.output_dir || "workspace/lab/deep_research/outputs";
  const runId = config.run_id || `codex-${Date.now()}`;

  const codex = new Codex();
  const planner = agents.find((a) => a.name === "planner");
  const evidence = agents.find((a) => a.name === "evidence");
  const counterpoint = agents.find((a) => a.name === "counterpoint");
  const synthesizer = agents.find((a) => a.name === "synthesizer");

  const plannerPrompt = render(PLANNER_PROMPT, { topic });
  const plannerThread = codex.startThread();
  const plannerResult = extractText(await plannerThread.run(plannerPrompt));
  const plan = tryParsePlan(plannerResult) || {
    scope: "以输入主题为核心。",
    questions: [topic],
    exclusions: [],
  };

  const questionsText = (plan.questions || []).join("; ");
  const materials = [];
  if (config.tools?.local_search?.enabled) {
    for (const keyword of [topic, "coworker", "agent", "skill", "record"]) {
      materials.push(localSearch(config.tools.local_search, keyword));
    }
  }

  const evidencePrompt = render(EVIDENCE_PROMPT, {
    topic,
    questions: questionsText,
  });
  const counterPrompt = render(COUNTERPOINT_PROMPT, {
    topic,
    questions: questionsText,
  });

  const [evidenceResult, counterResult] = await Promise.all([
    codex.startThread().run(
      evidencePrompt + `\n\n本地材料摘要：${materials.length}`
    ),
    codex.startThread().run(
      counterPrompt + `\n\n本地材料摘要：${materials.length}`
    ),
  ]);

  const evidenceText = extractText(evidenceResult);
  const counterText = extractText(counterResult);

  const findings = [
    {
      title: "当前能力定位",
      summary: "系统具备强记录与流程治理，但缺少多智能体协作运行时。",
      evidence: materials.flatMap((m) =>
        m.items.slice(0, 3).map((i) => `${i.path}: ${i.snippet}`)
      ),
      confidence: "medium",
    },
    {
      title: "工程化最小能力",
      summary: "需要任务分解、并行执行、汇总写作与可追溯产出。",
      evidence: [evidenceText],
      confidence: "medium",
    },
    {
      title: "主要不足",
      summary: counterText,
      evidence: [],
      confidence: "low",
    },
  ];

  const synthesisPrompt = render(SYNTHESIS_PROMPT, {
    topic,
    questions: questionsText,
    materials: JSON.stringify(findings, null, 2),
  });
  const synthesisText = extractText(
    await codex.startThread().run(synthesisPrompt)
  );

  const reportSections = [
    `# 研究报告\n\n主题：${topic}\n\n范围：${plan.scope || ""}`,
    `## 研究问题\n${(plan.questions || []).map((q) => `- ${q}`).join("\n")}`,
    ...findings.map((f) => `## ${f.title}\n${f.summary}`),
    `## 综合结论\n${synthesisText}`,
  ];

  const base = path.join(outputDir, runId);
  writeJson(path.join(base, "plan.json"), plan);
  writeJson(path.join(base, "materials.json"), { tools: materials });
  writeJson(path.join(base, "findings.json"), findings);
  writeJson(path.join(base, "synthesis.json"), {
    agent: synthesizer?.name || "synthesizer",
    role: synthesizer?.role || "Synthesis Writer",
    goal: synthesizer?.goal || "",
    content: synthesisText,
  });
  writeJson(path.join(base, "run_meta.json"), {
    run_id: runId,
    timestamp: new Date().toISOString(),
  });
  writeReport(path.join(base, "report.md"), reportSections);

  console.log(JSON.stringify({ run_id: runId, plan, findings }, null, 2));
}

run();
