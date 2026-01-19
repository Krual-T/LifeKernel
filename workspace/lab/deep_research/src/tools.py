from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional


@dataclass
class ToolResult:
    tool: str
    items: List[Dict[str, str]]


class BaseTool:
    name = "base"

    def run(self, query: str) -> ToolResult:
        raise NotImplementedError


class LocalSearchTool(BaseTool):
    name = "local_search"

    def __init__(
        self, root: str, max_files: int = 200, ignore: Optional[List[str]] = None
    ) -> None:
        self.root = root
        self.max_files = max_files
        self.ignore = _normalize_ignores(root, ignore or [])

    def _iter_files(self) -> Iterable[str]:
        count = 0
        for dirpath, dirnames, filenames in os.walk(self.root):
            if _is_ignored(dirpath, self.ignore):
                continue
            dirnames[:] = [
                d
                for d in dirnames
                if not d.startswith(".") and d not in {".git", ".venv", "__pycache__"}
            ]
            for filename in filenames:
                if filename.startswith("."):
                    continue
                path = os.path.join(dirpath, filename)
                yield path
                count += 1
                if count >= self.max_files:
                    return

    def run(self, query: str) -> ToolResult:
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        items: List[Dict[str, str]] = []
        for path in self._iter_files():
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
            except OSError:
                continue
            if not pattern.search(text):
                continue
            items.append(
                {
                    "path": path,
                    "snippet": _extract_snippet(text, pattern),
                }
            )
        return ToolResult(tool=self.name, items=items)


def _extract_snippet(text: str, pattern: re.Pattern, window: int = 80) -> str:
    match = pattern.search(text)
    if not match:
        return ""
    start = max(match.start() - window, 0)
    end = min(match.end() + window, len(text))
    snippet = text[start:end].replace("\n", " ").strip()
    return snippet


def build_tools(config: Dict[str, Dict[str, object]]) -> Dict[str, BaseTool]:
    tools: Dict[str, BaseTool] = {}
    local_cfg = config.get("local_search", {})
    if local_cfg.get("enabled"):
        root = str(local_cfg.get("root", "."))
        ignore = [str(x) for x in local_cfg.get("ignore", [])]
        tools["local_search"] = LocalSearchTool(root=root, ignore=ignore)
    return tools


def _normalize_ignores(root: str, ignores: List[str]) -> List[str]:
    normalized: List[str] = []
    for item in ignores:
        if not item:
            continue
        path = item
        if not os.path.isabs(path):
            path = os.path.join(root, item)
        normalized.append(os.path.normcase(os.path.abspath(path)))
    return normalized


def _is_ignored(path: str, ignores: List[str]) -> bool:
    norm = os.path.normcase(os.path.abspath(path))
    return any(norm.startswith(ignore) for ignore in ignores)
