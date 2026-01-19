from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AgentSpec:
    name: str
    role: str
    goal: str
    max_tokens: int = 1200


@dataclass
class AgentResult:
    agent: str
    role: str
    goal: str
    content: str
    citations: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent": self.agent,
            "role": self.role,
            "goal": self.goal,
            "content": self.content,
            "citations": self.citations,
            "metadata": self.metadata,
        }


@dataclass
class ResearchPlan:
    topic: str
    questions: List[str]
    scope: str
    exclusions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "topic": self.topic,
            "questions": self.questions,
            "scope": self.scope,
            "exclusions": self.exclusions,
        }


@dataclass
class Finding:
    title: str
    summary: str
    evidence: List[str] = field(default_factory=list)
    confidence: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "summary": self.summary,
            "evidence": self.evidence,
            "confidence": self.confidence,
        }
