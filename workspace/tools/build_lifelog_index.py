#!/usr/bin/env python
import json
from pathlib import Path

def main() -> int:
    root = Path('D:/Projects/LifeKernel/workspace/lifelog')
    paths = []
    if root.exists():
        for p in root.rglob('*.jsonl'):
            rel = p.relative_to(root).as_posix()
            paths.append(rel)
    out = root / 'index.json'
    out.write_text(json.dumps({'files': sorted(paths)}, ensure_ascii=False, indent=2), encoding='utf-8')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
