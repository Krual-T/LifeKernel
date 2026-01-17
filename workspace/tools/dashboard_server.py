#!/usr/bin/env python
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[1]


class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Serve files from workspace root
        rel = path.lstrip("/")
        return str(ROOT / rel)

    def do_GET(self):
        if self.path.startswith("/api/lifelog"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            entries = []
            lifelog_root = ROOT / "lifelog"
            if lifelog_root.exists():
                for p in lifelog_root.rglob("*.jsonl"):
                    try:
                        for line in p.read_text(encoding="utf-8").splitlines():
                            if not line.strip():
                                continue
                            entries.append(json.loads(line))
                    except Exception:
                        continue
            self.wfile.write(json.dumps(entries, ensure_ascii=False).encode("utf-8"))
            return
        return super().do_GET()


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 8000), Handler)
    print("Serving on http://localhost:8000/tools/jsonl_viewer.html")
    server.serve_forever()


if __name__ == "__main__":
    main()
