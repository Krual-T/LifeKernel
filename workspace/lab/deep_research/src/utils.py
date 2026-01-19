from __future__ import annotations

import datetime as dt
import re


def utc_now_iso() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def make_run_id(prefix: str) -> str:
    safe = slugify(prefix)
    timestamp = dt.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    return f"{safe}-{timestamp}"


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9\\-\\s]", "", text)
    text = re.sub(r"\\s+", "-", text)
    text = re.sub(r"-{2,}", "-", text)
    return text or "run"
