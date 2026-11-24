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
    python3 frontend/serve.py --run runs/acme
"""

import argparse
import csv
import datetime
import io
import json
import mimetypes
import re
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
RUN_TEMPLATE = ROOT / "pipeline" / "run.template.json"
RUNS = ROOT / "runs"

UNIVERSE_FIELDS = [
    "company", "url", "segment", "category", "service_summary", "services",
    "sales_route", "evidence_type", "headcount",
]

JOBS = {}
LOCK = threading.Lock()
CURRENT = {"id": None}
RUN_ARG = None
PAGE = BASE / ".serve.html"


# ---------------------------------------------------------------------------
# the pipeline
# ---------------------------------------------------------------------------

def load():
    cfg = json.loads(CONFIG.read_text())
    rel = RUN_ARG or cfg.get("run", ".")
    run_dir = Path(rel).resolve() if Path(rel).is_absolute() else (ROOT / rel).resolve()
    run = json.loads((run_dir / "run.json").read_text()) if (run_dir / "run.json").exists() else {}
    return cfg, run_dir, run


def state():
    cfg, run_dir, run = load()
    stages = []
    for s in cfg["stages"]:
        missing = [o for o in s.get("outputs", []) if not (run_dir / o).exists()]
        ready = stage_ready(s["id"], run_dir)
        stages.append({
            "id": s["id"],
            "name": s["name"],
            "ready": ready,
            "status": "ready" if ready else "waiting",
            "missing": missing,
            "credits": bool(s.get("requires_credits")),
        })
    try:
        rel = str(run_dir.relative_to(ROOT))
    except ValueError:
        rel = str(run_dir)
    return {"ok": True, "run": rel, "subject": run.get("subject", ""), "stages": stages}


def csv_rows(path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def stage_ready(stage_id, run_dir):
    """Return a useful UI state without running a gate."""
    if stage_id == 1:
        icp = run_dir / "icp.md"
        taxonomy = csv_rows(run_dir / "taxonomy.csv")
        return icp.exists() and "todo" not in icp.read_text(encoding="utf-8").lower() and len(taxonomy) >= 5
    if stage_id == 2:
        return bool(csv_rows(run_dir / "universe.csv"))
    if stage_id == 3:
        return (run_dir / "scoring-model.md").exists() and len(csv_rows(run_dir / "taxonomy.csv")) >= 5
    if stage_id == 4:
        return bool(csv_rows(run_dir / "similarity-ranking-reachable.csv"))
    if stage_id == 5:
        return bool(csv_rows(run_dir / "outreach.csv"))
    return False


def clean_text(value, label, required=True, limit=6000):
    text = str(value or "").strip()
    if required and not text:
        raise ValueError(f"{label} is required")
    if len(text) > limit:
        raise ValueError(f"{label} is too long")
    return text


def make_slug(value):
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        raise ValueError("company name must include a letter or number")
    return slug[:64]


def capability_lines(value):
    rows = []
    weights = {}
    for line in str(value or "").splitlines():
        raw = line.strip().lstrip("-• ").strip()
        if not raw:
            continue
        parts = [part.strip() for part in raw.rsplit("|", 1)]
        name = parts[0]
        try:
            weight = float(parts[1]) if len(parts) == 2 else 1.0
        except ValueError as exc:
            raise ValueError(f"capability {name!r} has an invalid weight") from exc
        if weight <= 0:
            raise ValueError(f"capability {name!r} must have a positive weight")
        if name and name.casefold() not in {row.casefold() for row in rows}:
            rows.append(name)
            weights[name] = weight
    if len(rows) < 5:
        raise ValueError("add at least five capabilities, one per line")
    if len(rows) > 40:
        raise ValueError("use no more than 40 capabilities")
    return rows, weights


def setup_run(payload):
    global RUN_ARG
    subject = clean_text(payload.get("subject"), "company name", limit=160)
    subject_url = clean_text(payload.get("subject_url"), "company website", required=False, limit=500)
    buyer = clean_text(payload.get("buyer"), "buyer", limit=2500)
    value = clean_text(payload.get("value_proposition"), "value proposition", limit=3500)
    anti = clean_text(payload.get("anti_icp"), "anti-ICP", limit=2500)
    evidence = clean_text(payload.get("evidence"), "evidence", required=False, limit=4000)
    capabilities, capability_weights = capability_lines(payload.get("capabilities"))
    core_names = {x.strip().casefold() for x in re.split(r"[,\n]", str(payload.get("core_capabilities") or "")) if x.strip()}
    core = [name for name in capabilities if name.casefold() in core_names]
    if not core:
        raise ValueError("mark at least one listed capability as core")

    slug = make_slug(payload.get("slug") or subject)
    run_dir = (RUNS / slug).resolve()
    if RUNS.resolve() not in run_dir.parents:
        raise ValueError("invalid run folder")
    if run_dir.exists():
        raise ValueError(f"a run named {slug!r} already exists")
    run_dir.mkdir(parents=True)

    today = datetime.date.today().isoformat()
    run = json.loads(RUN_TEMPLATE.read_text())
    run.update({
        "name": slug,
        "subject": subject,
        "subject_url": subject_url,
        "date": today,
        "brief": {
            "buyer": buyer,
            "value_proposition": value,
            "capabilities": capabilities,
            "capability_weights": capability_weights,
            "core_capabilities": core,
            "anti_icp": anti,
            "evidence": evidence,
        },
    })
    (run_dir / "run.json").write_text(json.dumps(run, indent=2) + "\n", encoding="utf-8")

    capability_text = "\n".join(f"- {name}" for name in capabilities)
    core_text = "\n".join(f"- {name}" for name in core)
    icp = f"""# ICP: {subject}

## Buyer

{buyer}

## Value proposition

{value}

## Capability surface

{capability_text}

## Weights

Each capability uses the weight entered during setup. Core capabilities define the Tier 1 floor.

## Core capabilities

{core_text}

## Anti-ICP

{anti}

## Evidence

{evidence or "No external evidence was recorded during setup."}
"""
    (run_dir / "icp.md").write_text(icp, encoding="utf-8")

    with (run_dir / "taxonomy.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["tag", "weight", "core", "regex"])
        writer.writeheader()
        for name in capabilities:
            words = re.escape(name).replace(r"\ ", r"\s+")
            writer.writerow({
                "tag": name,
                "weight": f"{capability_weights[name]:g}",
                "core": "yes" if name in core else "no",
                "regex": f"(?i)\\b{words}\\b",
            })

    model = f"""# Scoring model: {subject}

| Field | Value |
|---|---|
| Terms | capability 0.88, delivery 0.07, buyer 0.05 |
| Tier 1 | match index 55 or more, 2 or more core hits |
| Tier 2 | match index 18 or more, 1 or more core hit |
| Tier 3 | everything else |

Capability overlap carries most weight because this run finds companies that sell similar services.
"""
    (run_dir / "scoring-model.md").write_text(model, encoding="utf-8")
    (run_dir / "universe.csv").write_text(",".join(UNIVERSE_FIELDS) + "\n", encoding="utf-8")

    with LOCK:
        RUN_ARG = str(run_dir)
    build_page(run_dir)
    return run_dir


def import_candidates(payload):
    _, run_dir, run = load()
    raw = clean_text(payload.get("csv"), "candidate CSV", limit=750000)
    reader = csv.DictReader(io.StringIO(raw))
    fields = reader.fieldnames or []
    columns = run.get("columns") or {}
    required = [columns.get("id", "company"), columns.get("category", "category"),
                columns.get("summary", "service_summary"), columns.get("services", "services")]
    missing = [name for name in required if name not in fields]
    if missing:
        raise ValueError("candidate CSV lacks columns: " + ", ".join(missing))
    rows = [{key: (value or "").strip() for key, value in row.items()} for row in reader]
    rows = [row for row in rows if row.get(required[0])]
    if not rows:
        raise ValueError("candidate CSV has no company rows")
    with (run_dir / "universe.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    build_page(run_dir)
    return len(rows)


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
    if code == 0:
        # rebuild first, so a reload right after "done" reads the new figures
        build_page(load()[1])
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
            self.send_file(PAGE if PAGE.exists() else BASE / "index.html")
            return
        # only files inside frontend/
        target = (BASE / path.lstrip("/")).resolve()
        if BASE not in target.parents and target != BASE:
            self.send_json(403, {"error": "outside the page folder"})
            return
        self.send_file(target)

    def do_POST(self):
        route = self.path.split("?", 1)[0]
        if route not in ("/api/run", "/api/setup", "/api/candidates"):
            self.send_json(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length") or 0)
        if length > 800000:
            self.send_json(413, {"error": "request is too large"})
            return
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

        if route == "/api/setup":
            try:
                run_dir = setup_run(body)
            except (ValueError, OSError) as exc:
                self.send_json(400, {"error": str(exc)})
                return
            self.send_json(201, {"ok": True, "run": str(run_dir.relative_to(ROOT))})
            return

        if route == "/api/candidates":
            try:
                count = import_candidates(body)
            except (ValueError, OSError, csv.Error) as exc:
                self.send_json(400, {"error": str(exc)})
                return
            self.send_json(200, {"ok": True, "rows": count})
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


def build_page(run_dir):
    """Read the run into a private page. A half-finished run may fail; say so and go on."""
    cmd = [sys.executable, "-u", "frontend/build.py", "--run", str(run_dir),
           "--out", str(PAGE)]
    done = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if done.returncode != 0:
        print("page  : build failed, serving the page as it is")
        print("        " + (done.stderr or done.stdout).strip().splitlines()[-1])
        return
    print("page  : built from the run")


def main():
    global RUN_ARG
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8787)
    ap.add_argument("--no-open", action="store_true")
    ap.add_argument("--run", default=None, help="run folder (default: pipeline.json)")
    args = ap.parse_args()
    RUN_ARG = args.run

    cfg, run_dir, run = load()
    url = f"http://127.0.0.1:{args.port}/"
    print(f"page  : {url}", flush=True)
    build_page(run_dir)
    print(f"run   : {run_dir}", flush=True)
    print(f"subject: {run.get('subject', '-')}", flush=True)
    print("press Ctrl+C to stop", flush=True)
    if not args.no_open:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nstopped")
