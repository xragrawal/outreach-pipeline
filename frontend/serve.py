#!/usr/bin/env python3
"""Serve the pipeline page and run its stages on request.

The page is static. This server adds two things. It serves the folder, and it
runs one pipeline stage at a time when the page asks.

It binds to 127.0.0.1 only. It runs a fixed command list, so it cannot run
anything else.

Usage
-----
    python3 frontend/serve.py
    python3 frontend/serve.py --port 9000
    python3 frontend/serve.py --no-open
"""

import argparse
import json
import mimetypes
import subprocess
import sys
import threading
import uuid
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
CONFIG = ROOT / "pipeline" / "pipeline.json"

JOBS = {}
LOCK = threading.Lock()
CURRENT = {"id": None}


# ---------------------------------------------------------------------------
# the pipeline
# ---------------------------------------------------------------------------

def load():
    cfg = json.loads(CONFIG.read_text())
    run_dir = (ROOT / cfg.get("run", ".")).resolve()
    run = json.loads((run_dir / "run.json").read_text()) if (run_dir / "run.json").exists() else {}
    return cfg, run_dir, run


def state():
    cfg, run_dir, run = load()
    stages = []
    for s in cfg["stages"]:
        missing = [o for o in s.get("outputs", []) if not (run_dir / o).exists()]
        stages.append({
            "id": s["id"],
            "name": s["name"],
            "ready": not missing,
            "missing": missing,
            "credits": bool(s.get("requires_credits")),
        })
    return {"ok": True, "run": str(run_dir.relative_to(ROOT)), "subject": run.get("subject", ""),
            "stages": stages}


def command_for(stage_id, confirm_credits):
    cfg, run_dir, _ = load()
    stage = next((s for s in cfg["stages"] if str(s["id"]) == str(stage_id)), None)
    if stage is None:
        return None, "no such stage"
    if stage.get("requires_credits") and not confirm_credits:
        return None, "this stage spends API credits. Tick the confirm box."
    cmd = [sys.executable, "-u", "pipeline/run_pipeline.py", "--run", str(run_dir),
           "--stage", str(stage["id"])]
    if confirm_credits:
        cmd.append("--confirm-credits")
    return cmd, None


def run_job(job_id, cmd):
    job = JOBS[job_id]
    try:
        proc = subprocess.Popen(cmd, cwd=ROOT, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in proc.stdout:
            with LOCK:
                job["output"] += line
        code = proc.wait()
    except Exception as exc:  # noqa: BLE001 - report it, do not crash the server
        with LOCK:
            job["output"] += f"server error: {exc}\n"
        code = 1
    with LOCK:
        job["code"] = code
        job["state"] = "done"
        CURRENT["id"] = None


# ---------------------------------------------------------------------------
# http
# ---------------------------------------------------------------------------

class Handler(BaseHTTPRequestHandler):
    server_version = "pipeline-page"

    def log_message(self, fmt, *args):
        if "/api/" in (args[0] if args else ""):
            sys.stderr.write(f"  {args[0]} {args[1]}\n")

    def send_json(self, code, payload):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, path):
        if not path.exists() or not path.is_file():
            self.send_json(404, {"error": "not found"})
            return
        body = path.read_bytes()
        ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/api/state":
            self.send_json(200, state())
            return
        if path == "/api/job":
            job_id = self.path.split("id=", 1)[-1] if "id=" in self.path else ""
            with LOCK:
                job = JOBS.get(job_id)
                snapshot = dict(job) if job else None
            if not snapshot:
                self.send_json(404, {"error": "no such job"})
                return
            self.send_json(200, snapshot)
            return
        if path in ("/", ""):
            self.send_file(BASE / "index.html")
            return
        # only files inside frontend/
        target = (BASE / path.lstrip("/")).resolve()
        if BASE not in target.parents and target != BASE:
            self.send_json(403, {"error": "outside the page folder"})
            return
        self.send_file(target)

    def do_POST(self):
        if self.path.split("?", 1)[0] != "/api/run":
            self.send_json(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self.send_json(400, {"error": "bad json"})
            return

        with LOCK:
            busy = CURRENT["id"] is not None
        if busy:
            self.send_json(409, {"error": "a stage is already running"})
            return

        cmd, err = command_for(body.get("stage"), bool(body.get("confirm_credits")))
        if err:
            self.send_json(400, {"error": err})
            return

        job_id = uuid.uuid4().hex[:12]
        with LOCK:
            JOBS[job_id] = {"id": job_id, "stage": body.get("stage"), "state": "running",
                            "code": None, "output": "", "cmd": " ".join(cmd[2:])}
            CURRENT["id"] = job_id
        threading.Thread(target=run_job, args=(job_id, cmd), daemon=True).start()
        self.send_json(202, {"job": job_id})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8787)
    ap.add_argument("--no-open", action="store_true")
    args = ap.parse_args()

    cfg, run_dir, run = load()
    url = f"http://127.0.0.1:{args.port}/"
    print(f"page  : {url}")
    print(f"run   : {run_dir}")
    print(f"subject: {run.get('subject', '-')}")
    print("press Ctrl+C to stop")
    if not args.no_open:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nstopped")
