from __future__ import annotations

import json
import os
from typing import Any, Dict, Iterable, List


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def write_json(path: str, data: Any) -> None:
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def write_report(path: str, sections: Iterable[str]) -> None:
    ensure_dir(os.path.dirname(path))
    content = "\n\n".join([s for s in sections if s.strip()])
    with open(path, "w", encoding="utf-8") as f:
        f.write(content + "\n")
