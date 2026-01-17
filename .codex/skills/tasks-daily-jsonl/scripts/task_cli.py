#!/usr/bin/env python
import argparse
import json
from datetime import datetime
from pathlib import Path

ALLOWED_STATUS = {"pending", "done"}
ALLOWED_PRIORITY = {"low", "medium", "high"}
ALLOWED_MODULE = {"work", "personal", "learning", "health"}
TASKS_PATH = Path("D:/Projects/LifeKernel/workspace/tasks/tasks.jsonl")


def parse_dt(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value)


def load_tasks() -> list[dict]:
    if not TASKS_PATH.exists():
        return []
    lines = TASKS_PATH.read_text(encoding="utf-8").splitlines()
    tasks = []
    for line in lines:
        if not line.strip():
            continue
        tasks.append(json.loads(line))
    return tasks


def write_tasks(tasks: list[dict]) -> None:
    TASKS_PATH.parent.mkdir(parents=True, exist_ok=True)
    content = "
".join(json.dumps(t, ensure_ascii=False) for t in tasks) + "
"
    TASKS_PATH.write_text(content, encoding="utf-8")


def validate_enums(task: dict) -> None:
    if task.get("status") not in ALLOWED_STATUS:
        raise SystemExit(f"invalid status: {task.get('status')}")
    if task.get("priority") not in ALLOWED_PRIORITY:
        raise SystemExit(f"invalid priority: {task.get('priority')}")
    if task.get("module") not in ALLOWED_MODULE:
        raise SystemExit(f"invalid module: {task.get('module')}")


def cmd_create(args: argparse.Namespace) -> None:
    tasks = load_tasks()
    now = datetime.now().astimezone()
    created = parse_dt(args.created_at).astimezone() if args.created_at else now
    completed = parse_dt(args.completed_at).astimezone() if args.completed_at else None
    task_id = args.id or created.strftime("%Y-%m-%d-%H%M") + "-task"
    if any(t.get("id") == task_id for t in tasks):
        raise SystemExit(f"id already exists: {task_id}")

    status = args.status
    if status == "done" and completed is None:
        completed = now

    task = {
        "id": task_id,
        "title": args.title,
        "details": args.details,
        "status": status,
        "priority": args.priority,
        "module": args.module,
        "created_at": created.isoformat(timespec="seconds"),
        "completed_at": completed.isoformat(timespec="seconds") if completed else None,
        "due_time": parse_dt(args.due_time).astimezone().isoformat(timespec="seconds") if args.due_time else None,
        "source": args.source,
        "related_files": args.related_files,
    }
    validate_enums(task)
    tasks.append(task)
    write_tasks(tasks)


def cmd_update(args: argparse.Namespace) -> None:
    tasks = load_tasks()
    found = False
    now = datetime.now().astimezone()
    for t in tasks:
        if t.get("id") != args.id:
            continue
        found = True
        if args.title is not None:
            t["title"] = args.title
        if args.details is not None:
            t["details"] = args.details
        if args.status is not None:
            t["status"] = args.status
            if args.status == "done" and not t.get("completed_at"):
                t["completed_at"] = now.isoformat(timespec="seconds")
        if args.priority is not None:
            t["priority"] = args.priority
        if args.module is not None:
            t["module"] = args.module
        if args.created_at is not None:
            t["created_at"] = parse_dt(args.created_at).astimezone().isoformat(timespec="seconds")
        if args.completed_at is not None:
            t["completed_at"] = parse_dt(args.completed_at).astimezone().isoformat(timespec="seconds")
        if args.due_time is not None:
            t["due_time"] = parse_dt(args.due_time).astimezone().isoformat(timespec="seconds")
        if args.source is not None:
            t["source"] = args.source
        if args.related_files is not None:
            t["related_files"] = args.related_files
        validate_enums(t)
        break
    if not found:
        raise SystemExit(f"task not found: {args.id}")
    write_tasks(tasks)


def cmd_delete(args: argparse.Namespace) -> None:
    tasks = load_tasks()
    new_tasks = [t for t in tasks if t.get("id") != args.id]
    if len(new_tasks) == len(tasks):
        raise SystemExit(f"task not found: {args.id}")
    write_tasks(new_tasks)


def cmd_get(args: argparse.Namespace) -> None:
    tasks = load_tasks()
    for t in tasks:
        if t.get("id") == args.id:
            print(json.dumps(t, ensure_ascii=False))
            return
    raise SystemExit(f"task not found: {args.id}")


def cmd_list(args: argparse.Namespace) -> None:
    tasks = load_tasks()
    if args.status:
        tasks = [t for t in tasks if t.get("status") == args.status]
    if args.module:
        tasks = [t for t in tasks if t.get("module") == args.module]
    if args.priority:
        tasks = [t for t in tasks if t.get("priority") == args.priority]
    for t in tasks:
        print(json.dumps(t, ensure_ascii=False))


def main() -> int:
    parser = argparse.ArgumentParser(description="Tasks CRUD for tasks.jsonl (state table).")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_create = sub.add_parser("create")
    p_create.add_argument("--title", required=True)
    p_create.add_argument("--id")
    p_create.add_argument("--details")
    p_create.add_argument("--status", default="pending")
    p_create.add_argument("--priority", default="medium")
    p_create.add_argument("--module", default="work")
    p_create.add_argument("--created-at")
    p_create.add_argument("--completed-at")
    p_create.add_argument("--due-time")
    p_create.add_argument("--source", default="conversation")
    p_create.add_argument("--related-files", nargs="*", default=[])
    p_create.set_defaults(func=cmd_create)

    p_update = sub.add_parser("update")
    p_update.add_argument("--id", required=True)
    p_update.add_argument("--title")
    p_update.add_argument("--details")
    p_update.add_argument("--status")
    p_update.add_argument("--priority")
    p_update.add_argument("--module")
    p_update.add_argument("--created-at")
    p_update.add_argument("--completed-at")
    p_update.add_argument("--due-time")
    p_update.add_argument("--source")
    p_update.add_argument("--related-files", nargs="*")
    p_update.set_defaults(func=cmd_update)

    p_delete = sub.add_parser("delete")
    p_delete.add_argument("--id", required=True)
    p_delete.set_defaults(func=cmd_delete)

    p_get = sub.add_parser("get")
    p_get.add_argument("--id", required=True)
    p_get.set_defaults(func=cmd_get)

    p_list = sub.add_parser("list")
    p_list.add_argument("--status")
    p_list.add_argument("--module")
    p_list.add_argument("--priority")
    p_list.set_defaults(func=cmd_list)

    args = parser.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
