#!/usr/bin/env python
import argparse
import json
from datetime import datetime
from pathlib import Path

def parse_dt(value: str) -> datetime:
    if value.endswith('Z'):
        value = value[:-1] + '+00:00'
    return datetime.fromisoformat(value)


def main() -> int:
    parser = argparse.ArgumentParser(description='Append a task JSONL entry.')
    parser.add_argument('--title', required=True)
    parser.add_argument('--id')
    parser.add_argument('--details')
    parser.add_argument('--status', default='pending')
    parser.add_argument('--priority', default='medium')
    parser.add_argument('--module', default='work')
    parser.add_argument('--created-at')
    parser.add_argument('--completed-at')
    parser.add_argument('--due-time')
    parser.add_argument('--source', default='conversation')
    parser.add_argument('--related-files', nargs='*', default=[])
    args = parser.parse_args()

    now = datetime.now().astimezone()
    created = parse_dt(args.created_at).astimezone() if args.created_at else now
    completed = parse_dt(args.completed_at).astimezone() if args.completed_at else None
    entry_id = args.id or created.strftime('%Y-%m-%d-%H%M') + '-task'

    entry = {
        'id': entry_id,
        'title': args.title,
        'details': args.details,
        'status': args.status,
        'priority': args.priority,
        'module': args.module,
        'created_at': created.isoformat(timespec='seconds'),
        'completed_at': completed.isoformat(timespec='seconds') if completed else None,
        'due_time': parse_dt(args.due_time).astimezone().isoformat(timespec='seconds') if args.due_time else None,
        'source': args.source,
        'related_files': args.related_files,
    }

    path = Path('D:/Projects/LifeKernel/workspace/tasks/tasks.jsonl')
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(entry, ensure_ascii=False) + '\n'
    if path.exists():
        path.write_text(path.read_text(encoding='utf-8') + line, encoding='utf-8')
    else:
        path.write_text(line, encoding='utf-8')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
