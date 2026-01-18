#!/usr/bin/env python
import argparse
import json
from datetime import datetime
from pathlib import Path

def parse_dt(value: str) -> datetime:
    if value.endswith('Z'):
        value = value[:-1] + '+00:00'
    return datetime.fromisoformat(value)


def get_repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def main() -> int:
    parser = argparse.ArgumentParser(description='Append a lifelog JSONL entry.')
    parser.add_argument('--description', required=True)
    parser.add_argument('--timestamp')
    parser.add_argument('--id')
    parser.add_argument('--module', default='work')
    parser.add_argument('--skill-name', default=None)
    parser.add_argument('--source', default='conversation')
    parser.add_argument('--status', default='completed')
    parser.add_argument('--related-files', nargs='*', default=[])
    args = parser.parse_args()

    now = datetime.now().astimezone()
    dt = parse_dt(args.timestamp).astimezone() if args.timestamp else now
    entry_id = args.id or dt.strftime('%Y-%m-%d-%H%M') + '-log'

    entry = {
        'id': entry_id,
        'timestamp': dt.isoformat(timespec='seconds'),
        'module': args.module,
        'skill_name': args.skill_name,
        'source': args.source,
        'description': args.description,
        'status': args.status,
        'related_files': args.related_files,
    }

    repo_root = get_repo_root()
    path = repo_root / 'workspace' / 'lifelog' / dt.strftime('%Y/%m/%d.jsonl')
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(entry, ensure_ascii=False) + '\n'
    with path.open('a', encoding='utf-8') as f:
        f.write(line)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
