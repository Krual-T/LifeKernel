import argparse
import json
import os
from typing import Any
import uuid
from datetime import datetime


SCHEMA_PATH = os.path.join(".codex", "schema.json")


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


def load_schema() -> dict:
    if not os.path.exists(SCHEMA_PATH):
        raise SystemExit(f"schema not found: {SCHEMA_PATH}")
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_content(record_type: str, record: dict) -> str:
    if record_type == "knowledge":
        return record.get("title") or record.get("summary") or record.get("solution") or record.get("problem") or "未命名"
    if record_type == "news":
        return record.get("title") or record.get("summary") or "未命名"
    if record_type == "lifelog":
        return record.get("action") or record.get("description") or "未命名"
    if record_type == "agent_kernel_memory":
        return record.get("note") or record.get("summary") or record.get("title") or "未命名"
    if record_type == "tasks":
        return record.get("title") or record.get("details") or "未命名任务"
    return "未命名"


def validate_record(record: dict, record_type: str, schema: dict) -> None:
    if record_type not in schema.get("types", {}):
        raise SystemExit(f"schema missing record type: {record_type}")
    required = schema.get("common", {}).get("required", []) + schema["types"][record_type].get("required", [])
    for field in required:
        value = record.get(field)
        if value in (None, "", []):
            raise SystemExit(f"missing required field: {field}")
    enums = schema.get("enums", {})
    for field, allowed in enums.items():
        if field in record and record[field] not in allowed:
            raise SystemExit(f"invalid enum value for {field}: {record[field]}")


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
    if record_type == "agent_kernel_memory":
        return os.path.join("workspace", "records", "agent_kernel_memory", "agent_kernel_memory.jsonl")
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
                records.append({"raw": raw, "data": None, "dirty": False})
                continue
            records.append({"raw": raw, "data": data, "dirty": False})
    return records


def write_records(path: str, records: list) -> None:
    ensure_dir(path)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for item in records:
            data = item.get("data")
            raw = item.get("raw")
            if data is not None:
                if item.get("dirty"):
                    f.write(json.dumps(data, ensure_ascii=False) + "\n")
                elif raw:
                    f.write(raw + "\n")
                else:
                    f.write(json.dumps(data, ensure_ascii=False) + "\n")
            elif raw:
                f.write(raw + "\n")


def build_lifelog_entry(description: str, timestamp: str, module: str, skill_name: str,
                         source: str, status: str, related_files: list) -> dict:
    entry: dict[str, Any] = {
        "id": generate_id(),
        "timestamp": timestamp,
        "module": module or "work",
        "skill_name": skill_name or "recorder",
        "source": source or "conversation",
        "description": description,
        "action": description,
        "status": status or "done",
    }
    entry["type"] = "lifelog"
    entry["content"] = description
    if related_files:
        entry["related_files"] = related_files
    return entry


def normalize_task_status(value: str | None) -> str:
    if not value:
        return "todo"
    lowered = value.lower()
    if lowered in ("todo", "pending"):
        return "todo"
    if lowered in ("doing", "in_progress", "in-progress"):
        return "doing"
    if lowered in ("done", "completed", "complete"):
        return "done"
    return "todo"


def normalize_priority(value: str | None) -> str:
    if not value:
        return "P2"
    upper = value.upper()
    if upper in ("P0", "P1", "P2", "P3"):
        return upper
    if value.lower() == "high":
        return "P1"
    if value.lower() == "medium":
        return "P2"
    if value.lower() == "low":
        return "P3"
    return "P2"


def main() -> None:
    parser = argparse.ArgumentParser(description="Unified JSONL recorder")
    parser.add_argument("--record-type", required=True, choices=["knowledge", "news", "lifelog", "agent_kernel_memory", "tasks", "update", "delete"])
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
    parser.add_argument("--scope", default=None)

    parser.add_argument("--extra", default=None, help="Extra JSON string to merge into record")
    parser.add_argument("--target-type", default=None, choices=["knowledge", "news", "lifelog", "agent_kernel_memory", "tasks"])
    parser.add_argument("--key", dest="update_key", default=None)
    parser.add_argument("--value", dest="update_value", default=None)
    parser.add_argument("--value-json", dest="update_value_json", default=None)

    args = parser.parse_args()

    schema = load_schema()
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
                if "timestamp" not in data or not data.get("timestamp"):
                    data["timestamp"] = timestamp
                if "type" not in data or not data.get("type"):
                    data["type"] = args.target_type
                if "source" not in data or not data.get("source"):
                    data["source"] = args.source or "conversation"
                if "content" not in data or not data.get("content"):
                    data["content"] = normalize_content(args.target_type, data)
                if args.target_type == "lifelog":
                    if "action" not in data or not data.get("action"):
                        data["action"] = data.get("description") or data.get("content")
                if args.target_type == "agent_kernel_memory":
                    if "scope" not in data:
                        data["scope"] = "user"
                    if "deleted" not in data:
                        data["deleted"] = False
                if args.target_type == "tasks":
                    data["status"] = normalize_task_status(data.get("status"))
                    data["priority"] = normalize_priority(data.get("priority"))
                validate_record(data, args.target_type, schema)
                item["dirty"] = True
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
        if args.target_type == "agent_kernel_memory":
            records = load_records_with_raw(path)
            updated_any = False
            for item in records:
                data = item.get("data")
                if not data:
                    continue
                if data.get("id") == args.record_id:
                    data["deleted"] = True
                    if "timestamp" not in data or not data.get("timestamp"):
                        data["timestamp"] = timestamp
                    if "type" not in data or not data.get("type"):
                        data["type"] = "agent_kernel_memory"
                    if "source" not in data or not data.get("source"):
                        data["source"] = args.source or "conversation"
                    if "content" not in data or not data.get("content"):
                        data["content"] = normalize_content("agent_kernel_memory", data)
                    if "scope" not in data:
                        data["scope"] = "user"
                    validate_record(data, "agent_kernel_memory", schema)
                    item["dirty"] = True
                    updated_any = True
            if not updated_any:
                raise SystemExit(f"record id not found: {args.record_id}")
            write_records(path, records)
            return
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
        record["type"] = "knowledge"
        record["source"] = args.source or "conversation"
        record["content"] = normalize_content("knowledge", record)
        if args.module:
            record["module"] = args.module
        if related_files:
            record["related_files"] = related_files
        record_id = args.record_id or generate_id()
        record["id"] = record_id
        if args.extra:
            record.update(json.loads(args.extra))
        validate_record(record, "knowledge", schema)
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
                status="done",
                related_files=["workspace/records/knowledge/knowledge.jsonl"],
            )
            validate_record(lifelog_entry, "lifelog", schema)
            append_jsonl(get_lifelog_path(timestamp), lifelog_entry)

    elif args.record_type == "news":
        record = {
            "title": args.title,
            "summary": args.summary,
            "tags": parse_list(args.tags),
        }
        record = {k: v for k, v in record.items() if v not in (None, "", [])}
        record["timestamp"] = timestamp
        record["type"] = "news"
        record["module"] = args.module or "news"
        record["source"] = args.source or "conversation"
        record["content"] = normalize_content("news", record)
        if related_files:
            record["related_files"] = related_files
        record_id = args.record_id or generate_id()
        record["id"] = record_id
        if args.extra:
            record.update(json.loads(args.extra))
        validate_record(record, "news", schema)
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
                status="done",
                related_files=["workspace/records/news/news.jsonl"],
            )
            validate_record(lifelog_entry, "lifelog", schema)
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
        validate_record(entry, "lifelog", schema)
        append_jsonl(get_lifelog_path(timestamp), entry)

    elif args.record_type == "agent_kernel_memory":
        record = {
            "id": args.record_id or generate_id(),
            "timestamp": timestamp,
            "type": "agent_kernel_memory",
            "note": args.note or args.summary or args.title,
            "deleted": False,
            "scope": args.scope or "user",
        }
        if args.module:
            record["module"] = args.module
        record["source"] = args.source or "conversation"
        record["content"] = normalize_content("agent_kernel_memory", record)
        if related_files:
            record["related_files"] = related_files
        if args.extra:
            record.update(json.loads(args.extra))
        validate_record(record, "agent_kernel_memory", schema)
        append_jsonl(os.path.join("workspace", "records", "agent_kernel_memory", "agent_kernel_memory.jsonl"), record)

    else:  # tasks
        task_status = normalize_task_status(args.status)
        if task_status == "todo" and args.completed_at:
            task_status = "done"
        record = {
            "id": args.record_id,
            "type": "tasks",
            "title": args.title,
            "details": args.details,
            "status": task_status,
            "priority": normalize_priority(args.priority),
            "module": args.module or "work",
            "timestamp": timestamp,
            "completed_at": args.completed_at,
            "due": args.due_time,
            "source": args.source or "conversation",
        }
        record = {k: v for k, v in record.items() if v not in (None, "")}
        record["content"] = normalize_content("tasks", record)
        if not record.get("id"):
            record["id"] = generate_id()
        if related_files:
            record["related_files"] = related_files
        if args.extra:
            record.update(json.loads(args.extra))
        validate_record(record, "tasks", schema)
        append_jsonl(os.path.join("workspace", "records", "tasks", "tasks.jsonl"), record)


if __name__ == "__main__":
    main()
