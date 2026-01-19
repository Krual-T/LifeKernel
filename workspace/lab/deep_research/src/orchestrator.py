from __future__ import annotations

import asyncio
import json
from dataclasses import asdict
from typing import Dict, List, Optional, Sequence, Tuple, Union

from .agents import AgentResult, AgentSpec, Finding, ResearchPlan
from .prompts import (
    COUNTERPOINT_PROMPT,
    EVIDENCE_PROMPT,
    PLANNER_PROMPT,
    SYNTHESIS_PROMPT,
)
from .storage import write_json, write_report
from .tools import ToolResult, build_tools
from .utils import make_run_id, utc_now_iso


class BaseProvider:
    async def generate(
        self, prompt: str, agent: AgentSpec, context: Optional[Dict[str, str]] = None
    ) -> Union[str, Dict[str, object]]:
        raise NotImplementedError


class MockProvider(BaseProvider):
    def __init__(self, seed: int = 7) -> None:
        self.seed = seed

    async def generate(
        self, prompt: str, agent: AgentSpec, context: Optional[Dict[str, str]] = None
    ) -> Union[str, Dict[str, object]]:
        if agent.name == "planner":
            return {
                "scope": "聚焦多智能体协作能力、编排机制与产出可追溯性。",
                "questions": [
                    "LifeKernel 当前是否具备多智能体协作运行时？",
                    "工程化 deep research 的最小必要能力是什么？",
                    "与主流框架相比有哪些优势与不足？",
                ],
                "exclusions": ["商业采购与价格评估", "未公开的内部路线图"],
            }
        if agent.name == "evidence":
            return "已根据本地材料整理了核心要点与证据（见 findings.json）。"
        if agent.name == "counterpoint":
            return "识别出编排层与多智能体运行时缺失等关键不足。"
        return "报告已按概览/发现/不足/建议输出。"


class ManualProvider(BaseProvider):
    async def generate(
        self, prompt: str, agent: AgentSpec, context: Optional[Dict[str, str]] = None
    ) -> Union[str, Dict[str, object]]:
        print(f"\n=== {agent.name} ({agent.role}) ===\n")
        print(prompt)
        print("\n请输入该 agent 的输出，输入空行结束：")
        lines: List[str] = []
        while True:
            line = input()
            if not line.strip():
                break
            lines.append(line)
        return "\n".join(lines)


class Orchestrator:
    def __init__(
        self,
        topic: str,
        agents: Sequence[AgentSpec],
        provider: BaseProvider,
        tools_config: Dict[str, Dict[str, object]],
        output_dir: str,
        run_id: Optional[str] = None,
    ) -> None:
        self.topic = topic
        self.agents = {agent.name: agent for agent in agents}
        self.provider = provider
        self.tools = build_tools(tools_config)
        self.output_dir = output_dir
        self.run_id = run_id or make_run_id("deep-research")

    async def run(self) -> Dict[str, object]:
        plan = await self._build_plan()
        tool_results = self._collect_materials(plan)
        evidence_task = asyncio.create_task(self._run_agent("evidence", plan, tool_results))
        counter_task = asyncio.create_task(
            self._run_agent("counterpoint", plan, tool_results)
        )
        evidence, counterpoint = await asyncio.gather(evidence_task, counter_task)
        findings = self._build_findings(plan, evidence, counterpoint, tool_results)
        synthesis = await self._run_synthesis(plan, findings)
        report_sections = self._assemble_report(plan, findings, synthesis, counterpoint)
        self._persist(plan, tool_results, findings, synthesis, report_sections)
        return {
            "run_id": self.run_id,
            "plan": plan.to_dict(),
            "findings": [f.to_dict() for f in findings],
            "synthesis": synthesis.to_dict(),
        }

    async def _build_plan(self) -> ResearchPlan:
        planner = self.agents.get("planner")
        if planner is None:
            raise ValueError("planner agent not configured")
        prompt = PLANNER_PROMPT.format(topic=self.topic)
        raw = await self.provider.generate(prompt, planner, {"topic": self.topic})
        if isinstance(raw, dict):
            questions = [str(q) for q in raw.get("questions", [])]
            scope = str(raw.get("scope", ""))
            exclusions = [str(x) for x in raw.get("exclusions", [])]
        else:
            questions = _parse_bullets(raw)
            scope = "以输入主题为核心。"
            exclusions = []
        return ResearchPlan(topic=self.topic, questions=questions, scope=scope, exclusions=exclusions)

    def _collect_materials(self, plan: ResearchPlan) -> List[ToolResult]:
        results: List[ToolResult] = []
        if "local_search" in self.tools:
            for query in _keywords_from_topic(plan.topic):
                results.append(self.tools["local_search"].run(query))
        return results

    async def _run_agent(
        self, name: str, plan: ResearchPlan, tool_results: List[ToolResult]
    ) -> AgentResult:
        agent = self.agents.get(name)
        if agent is None:
            raise ValueError(f"agent {name} not configured")
        prompt = EVIDENCE_PROMPT if name == "evidence" else COUNTERPOINT_PROMPT
        rendered = prompt.format(topic=plan.topic, questions="; ".join(plan.questions))
        if tool_results:
            rendered += f"\n\n本地材料：{_tool_summary(tool_results)}"
        raw = await self.provider.generate(rendered, agent, {"topic": plan.topic})
        return AgentResult(
            agent=agent.name,
            role=agent.role,
            goal=agent.goal,
            content=str(raw),
        )

    def _build_findings(
        self,
        plan: ResearchPlan,
        evidence: AgentResult,
        counterpoint: AgentResult,
        tool_results: List[ToolResult],
    ) -> List[Finding]:
        findings: List[Finding] = []
        findings.append(
            Finding(
                title="当前能力定位",
                summary="系统具备强记录与流程治理，但缺少多智能体协作运行时。",
                evidence=_flatten_tool_items(tool_results),
                confidence="medium",
            )
        )
        findings.append(
            Finding(
                title="工程化最小能力",
                summary="需要任务分解、并行执行、汇总写作与可追溯产出。",
                evidence=[evidence.content],
                confidence="medium",
            )
        )
        findings.append(
            Finding(
                title="主要不足",
                summary=counterpoint.content,
                evidence=[],
                confidence="low",
            )
        )
        return findings

    async def _run_synthesis(self, plan: ResearchPlan, findings: List[Finding]) -> AgentResult:
        agent = self.agents.get("synthesizer")
        if agent is None:
            raise ValueError("synthesizer agent not configured")
        materials = json.dumps([f.to_dict() for f in findings], ensure_ascii=False, indent=2)
        prompt = SYNTHESIS_PROMPT.format(
            topic=plan.topic, questions="; ".join(plan.questions), materials=materials
        )
        raw = await self.provider.generate(prompt, agent, {"topic": plan.topic})
        return AgentResult(
            agent=agent.name,
            role=agent.role,
            goal=agent.goal,
            content=str(raw),
        )

    def _assemble_report(
        self,
        plan: ResearchPlan,
        findings: List[Finding],
        synthesis: AgentResult,
        counterpoint: AgentResult,
    ) -> List[str]:
        overview = (
            f"# 研究报告\n\n"
            f"主题：{plan.topic}\n\n"
            f"范围：{plan.scope}\n"
        )
        questions = "\n".join([f"- {q}" for q in plan.questions])
        findings_md = "\n".join(
            [f"## {f.title}\n{f.summary}" for f in findings]
        )
        gaps = f"## 主要不足\n{counterpoint.content}"
        synthesis_md = f"## 综合结论\n{synthesis.content}"
        return [overview, "## 研究问题\n" + questions, findings_md, gaps, synthesis_md]

    def _persist(
        self,
        plan: ResearchPlan,
        tool_results: List[ToolResult],
        findings: List[Finding],
        synthesis: AgentResult,
        report_sections: List[str],
    ) -> None:
        base = f"{self.output_dir}/{self.run_id}"
        write_json(f"{base}/plan.json", plan.to_dict())
        write_json(
            f"{base}/materials.json",
            {"tools": [asdict(result) for result in tool_results]},
        )
        write_json(
            f"{base}/findings.json",
            [f.to_dict() for f in findings],
        )
        write_json(
            f"{base}/run_meta.json",
            {"run_id": self.run_id, "timestamp": utc_now_iso()},
        )
        write_json(
            f"{base}/synthesis.json",
            synthesis.to_dict(),
        )
        write_report(f"{base}/report.md", report_sections)


def _parse_bullets(text: str) -> List[str]:
    lines = [line.strip("- ").strip() for line in text.splitlines() if line.strip()]
    return [line for line in lines if len(line) > 2]


def _keywords_from_topic(topic: str) -> List[str]:
    tokens = [t for t in topic.replace("/", " ").split() if len(t) > 2]
    return list(dict.fromkeys(tokens + ["coworker", "agent", "skill", "record"]))


def _tool_summary(results: List[ToolResult]) -> str:
    total = sum(len(r.items) for r in results)
    return f"{len(results)} tools, {total} hits"


def _flatten_tool_items(results: List[ToolResult]) -> List[str]:
    items: List[str] = []
    for result in results:
        for item in result.items:
            path = item.get("path", "")
            snippet = item.get("snippet", "")
            if path:
                items.append(f"{path}: {snippet}")
    return items[:10]
