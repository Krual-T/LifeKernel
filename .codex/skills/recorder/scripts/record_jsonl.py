import argparse
import json
import os
import uuid
from datetime import datetime


def ensure_dir(path: str) -> None:
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)


def iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def generate_id() -> str:
    return str(uuid.uuid4())


def append_jsonl(path: str, data: dict) -> None:
    ensure_dir(path)
    line = json.dumps(data, ensure_ascii=False)
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(line + "\n")


def parse_list(value: str) -> list:
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


def get_lifelog_path(timestamp: str) -> str:
    try:
        dt = datetime.fromisoformat(timestamp)
    except ValueError:
        dt = datetime.now().astimezone()
    return os.path.join(
        "workspace",
        "records",
        "lifelog",
        f"{dt:%Y}",
        f"{dt:%m}",
        f"{dt:%d}.jsonl",
    )


def get_record_path(record_type: str, record_id: str = "") -> str:
    if record_type == "knowledge":
        return os.path.join("workspace", "records", "knowledge", "knowledge.jsonl")
    if record_type == "news":
        return os.path.join("workspace", "records", "news", "news.jsonl")
    if record_type == "memory":
        return os.path.join("workspace", "records", "memory", "memory.jsonl")
    if record_type == "tasks":
        return os.path.join("workspace", "records", "tasks", "tasks.jsonl")
    raise SystemExit(f"unsupported record type: {record_type}")


def load_latest_record(path: str, record_id: str) -> dict:
    if not os.path.exists(path):
        raise SystemExit(f"record file not found: {path}")
    latest = None
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            if data.get("id") == record_id:
                latest = data
    if latest is None:
        raise SystemExit(f"record id not found: {record_id}")
    return latest


def find_record_by_id(target_type: str, record_id: str) -> tuple[str, dict]:
    if target_type != "lifelog":
        path = get_record_path(target_type)
        record = load_latest_record(path, record_id)
        return path, record

    lifelog_root = os.path.join("workspace", "records", "lifelog")
    if not os.path.exists(lifelog_root):
        raise SystemExit(f"record file not found: {lifelog_root}")

    for root, _, files in os.walk(lifelog_root):
        for name in files:
            if not name.endswith(".jsonl"):
                continue
            path = os.path.join(root, name)
            latest = None
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if data.get("id") == record_id:
                        latest = data
            if latest is not None:
                return path, latest

    raise SystemExit(f"record id not found: {record_id}")


def load_records_with_raw(path: str) -> list:
    if not os.path.exists(path):
        raise SystemExit(f"record file not found: {path}")
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            raw = line.rstrip("\n")
            if not raw:
                continue
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                records.append({"raw": raw, "data": None})
                continue
            records.append({"raw": raw, "data": data})
    return records


def write_records(path: str, records: list) -> None:
    ensure_dir(path)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for item in records:
            data = item.get("data")
            raw = item.get("raw")
            if data is not None:
                f.write(json.dumps(data, ensure_ascii=False) + "\n")
            elif raw:
                f.write(raw + "\n")


def build_lifelog_entry(description: str, timestamp: str, module: str, skill_name: str,
                         source: str, status: str, related_files: list) -> dict:
    entry = {
        "id": generate_id(),
        "timestamp": timestamp,
        "module": module or "work",
        "skill_name": skill_name or "recorder",
        "source": source or "conversation",
        "description": description,
        "status": status or "completed",
    }
    if related_files:
        entry["related_files"] = related_files
    return entry


def main() -> None:
    parser = argparse.ArgumentParser(description="Unified JSONL recorder")
    parser.add_argument("--record-type", required=True, choices=["knowledge", "news", "lifelog", "memory", "tasks", "update", "delete"])
    parser.add_argument("--timestamp", default=None)
    parser.add_argument("--id", dest="record_id", default=None)
    parser.add_argument("--module", default=None)
    parser.add_argument("--source", default=None)
    parser.add_argument("--status", default=None)
    parser.add_argument("--related-file", action="append", default=[])
    parser.add_argument("--auto-record", action="store_true")
    parser.add_argument("--no-auto-record", action="store_true")

    parser.add_argument("--title", default=None)
    parser.add_argument("--summary", default=None)
    parser.add_argument("--problem", default=None)
    parser.add_argument("--symptom", default=None)
    parser.add_argument("--root-cause", dest="root_cause", default=None)
    parser.add_argument("--solution", default=None)
    parser.add_argument("--environment", default=None)
    parser.add_argument("--tags", default=None)
    parser.add_argument("--examples", default=None)

    parser.add_argument("--description", default=None)
    parser.add_argument("--details", default=None)
    parser.add_argument("--priority", default=None)
    parser.add_argument("--due-time", dest="due_time", default=None)
    parser.add_argument("--completed-at", dest="completed_at", default=None)
    parser.add_argument("--note", default=None)

    parser.add_argument("--extra", default=None, help="Extra JSON string to merge into record")
    parser.add_argument("--target-type", default=None, choices=["knowledge", "news", "lifelog", "memory", "tasks"])
    parser.add_argument("--key", dest="update_key", default=None)
    parser.add_argument("--value", dest="update_value", default=None)
    parser.add_argument("--value-json", dest="update_value_json", default=None)

    args = parser.parse_args()

    timestamp = args.timestamp or iso_now()
    related_files = args.related_file

    if args.record_type == "update":
        if not args.target_type:
            raise SystemExit("--target-type is required for update")
        if not args.record_id:
            raise SystemExit("--id is required for update")
        if not args.update_key:
            raise SystemExit("--key is required for update")
        if args.update_value is None and args.update_value_json is None:
            raise SystemExit("--value or --value-json is required for update")

        path, _ = find_record_by_id(args.target_type, args.record_id)
        if args.update_value_json:
            try:
                value = json.loads(args.update_value_json)
            except json.JSONDecodeError as exc:
                raise SystemExit("--value-json must be valid JSON") from exc
        else:
            value = args.update_value

        records = load_records_with_raw(path)
        updated_any = False
        for item in records:
            data = item.get("data")
            if not data:
                continue
            if data.get("id") == args.record_id:
                data[args.update_key] = value
                if "timestamp" not in data:
                    data["timestamp"] = timestamp
                updated_any = True
        if not updated_any:
            raise SystemExit(f"record id not found: {args.record_id}")
        write_records(path, records)

    elif args.record_type == "delete":
        if not args.target_type:
            raise SystemExit("--target-type is required for delete")
        if not args.record_id:
            raise SystemExit("--id is required for delete")
        path, _ = find_record_by_id(args.target_type, args.record_id)
        records = load_records_with_raw(path)
        before = len(records)
        records = [item for item in records if not (item.get("data") and item["data"].get("id") == args.record_id)]
        if len(records) == before:
            raise SystemExit(f"record id not found: {args.record_id}")
        write_records(path, records)

    elif args.record_type == "knowledge":
        record = {
            "title": args.title,
            "summary": args.summary,
            "problem": args.problem,
            "symptom": args.symptom,
            "root_cause": args.root_cause,
            "solution": args.solution,
            "environment": args.environment,
            "tags": parse_list(args.tags),
            "examples": parse_list(args.examples),
        }
        record = {k: v for k, v in record.items() if v not in (None, "", [])}
        record["timestamp"] = timestamp
        if args.module:
            record["module"] = args.module
        if args.source:
            record["source"] = args.source
        if related_files:
            record["related_files"] = related_files
        record_id = args.record_id or generate_id()
        record["id"] = record_id
        if args.extra:
            record.update(json.loads(args.extra))
        append_jsonl(os.path.join("workspace", "records", "knowledge", "knowledge.jsonl"), record)

        auto_record = True
        if args.no_auto_record:
            auto_record = False
        elif args.auto_record:
            auto_record = True
        if auto_record:
            desc_seed = args.title or args.summary or args.problem or "未命名"
            description = f"新增 knowledge：{desc_seed}"
            lifelog_entry = build_lifelog_entry(
                description=description,
                timestamp=timestamp,
                module=args.module or "work",
                skill_name="recorder",
                source=args.source or "conversation",
                status="completed",
                related_files=["workspace/records/knowledge/knowledge.jsonl"],
            )
            append_jsonl(get_lifelog_path(timestamp), lifelog_entry)

    elif args.record_type == "news":
        record = {
            "title": args.title,
            "summary": args.summary,
            "tags": parse_list(args.tags),
        }
        record = {k: v for k, v in record.items() if v not in (None, "", [])}
        record["timestamp"] = timestamp
        record["module"] = args.module or "news"
        if args.source:
            record["source"] = args.source
        if related_files:
            record["related_files"] = related_files
        record_id = args.record_id or generate_id()
        record["id"] = record_id
        if args.extra:
            record.update(json.loads(args.extra))
        append_jsonl(os.path.join("workspace", "records", "news", "news.jsonl"), record)

        auto_record = True
        if args.no_auto_record:
            auto_record = False
        elif args.auto_record:
            auto_record = True
        if auto_record:
            desc_seed = args.title or args.summary or "未命名"
            description = f"新增 news：{desc_seed}"
            lifelog_entry = build_lifelog_entry(
                description=description,
                timestamp=timestamp,
                module=args.module or "news",
                skill_name="recorder",
                source=args.source or "conversation",
                status="completed",
                related_files=["workspace/records/news/news.jsonl"],
            )
            append_jsonl(get_lifelog_path(timestamp), lifelog_entry)

    elif args.record_type == "lifelog":
        if not args.description:
            raise SystemExit("--description is required for lifelog")
        entry = build_lifelog_entry(
            description=args.description,
            timestamp=timestamp,
            module=args.module,
            skill_name="recorder",
            source=args.source,
            status=args.status,
            related_files=related_files,
        )
        if args.record_id:
            entry["id"] = args.record_id
        if args.extra:
            entry.update(json.loads(args.extra))
        append_jsonl(get_lifelog_path(timestamp), entry)

    elif args.record_type == "memory":
        record = {
            "id": args.record_id or generate_id(),
            "timestamp": timestamp,
            "note": args.note or args.summary or args.title,
            "type": "memory",
        }
        if args.module:
            record["module"] = args.module
        if args.source:
            record["source"] = args.source
        if related_files:
            record["related_files"] = related_files
        if args.extra:
            record.update(json.loads(args.extra))
        append_jsonl(os.path.join("workspace", "records", "memory", "memory.jsonl"), record)

    else:  # tasks
        task_status = args.status or "pending"
        if task_status == "completed":
            task_status = "done"
        if task_status == "pending" and args.completed_at:
            task_status = "done"
        record = {
            "id": args.record_id,
            "title": args.title,
            "details": args.details,
            "status": task_status,
            "priority": args.priority or "medium",
            "module": args.module or "work",
            "created_at": timestamp,
            "completed_at": args.completed_at,
            "due_time": args.due_time,
            "source": args.source or "conversation",
        }
        record = {k: v for k, v in record.items() if v not in (None, "")}
        if not record.get("id"):
            record["id"] = generate_id()
        if related_files:
            record["related_files"] = related_files
        if args.extra:
            record.update(json.loads(args.extra))
        append_jsonl(os.path.join("workspace", "records", "tasks", "tasks.jsonl"), record)


if __name__ == "__main__":
    main()
