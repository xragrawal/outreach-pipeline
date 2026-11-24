#!/usr/bin/env python3
"""Enrich the shortlist with personal contacts from Hunter.

Rule: personal addresses only. A shared inbox (info@, hello@, partnerships@)
is never written to contact_email. Such a company gets hunter_status=generic_only
and an empty address, so the gap stays visible.

The key is read from ~/.hermes/.env or HUNTER_API_KEY. It is never printed,
passed as an argument, or written to an artifact.

Every raw response is cached per domain before it is parsed, so a rerun spends
no new credits.
"""

import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

BASE = Path(__file__).resolve().parent
CSV_PATH = BASE / "similarity-ranking-reachable.csv"
CACHE = BASE / "hunter-cache"
OUT_CSV = BASE / "similarity-ranking-contacts.csv"
ACCOUNT_JSON = BASE / "hunter-account.json"

API = "https://api.hunter.io/v2"

# Local parts that mark a shared or role inbox. Never treated as a person.
GENERIC_LOCAL = {
    "info", "hello", "contact", "support", "help", "helpdesk", "sales", "admin",
    "administrator", "team", "hi", "hey", "enquiries", "enquiry", "inquiries",
    "inquiry", "partnerships", "partners", "business", "bd", "press", "media",
    "jobs", "careers", "recruiting", "privacy", "legal", "billing", "accounts",
    "accounting", "finance", "marketing", "hr", "people", "office", "mail",
    "email", "connect", "grow", "founders", "founder", "noreply", "no-reply",
    "donotreply", "security", "abuse", "postmaster", "webmaster", "dev", "devs",
    "developers", "engineering", "api", "ops", "community", "social", "feedback",
    "success", "customers", "clients", "orders", "service", "services", "general",
}

# Titles that suggest someone who can answer a partnership or supply question.
DECISION_HINTS = (
    "founder", "co-founder", "cofounder", "ceo", "cto", "coo", "cpo", "cro",
    "chief", "president", "owner", "partner", "head of", "vp ", "vice president",
    "director", "lead", "manager", "business development", "partnerships",
)


def load_key():
    key = os.environ.get("HUNTER_API_KEY", "").strip()
    if key:
        return key
    env = Path.home() / ".hermes" / ".env"
    if env.exists():
        for line in env.read_text(errors="ignore").splitlines():
            line = line.strip()
            if line.startswith("HUNTER_API_KEY"):
                _, _, val = line.partition("=")
                return val.strip().strip("'\"")
    return ""


def call(path, params, key):
    params = dict(params, api_key=key)
    url = f"{API}/{path}?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode()), None
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="ignore")
        try:
            payload = json.loads(body)
        except Exception:
            payload = {"raw": body[:500]}
        return None, (e.code, payload)
    except Exception as e:  # network, timeout, dns
        return None, (0, {"error": type(e).__name__})


def is_generic(email, entry):
    """True when the address is a shared inbox, not one person."""
    if entry.get("type") == "generic":
        return True
    local = email.split("@", 1)[0].lower()
    local = re.split(r"[+._-]", local)[0]
    return local in GENERIC_LOCAL


def has_identity(entry):
    """Hunter must name a person, not just return a mailbox."""
    first = (entry.get("first_name") or "").strip()
    last = (entry.get("last_name") or "").strip()
    position = (entry.get("position") or "").strip()
    return bool(first or last) and bool(position)


def pick(entries):
    """Best personal contact: seniority, then confidence, then a title hint."""
    people = []
    for e in entries:
        value = (e.get("value") or "").strip().lower()
        if not value or "@" not in value:
            continue
        if is_generic(value, e):
            continue
        if not has_identity(e):
            continue
        title = (e.get("position") or "").lower()
        hint = any(h in title for h in DECISION_HINTS)
        people.append((1 if hint else 0, e.get("confidence") or 0, value, e))
    if not people:
        return None
    people.sort(key=lambda t: (-t[0], -t[1], t[2]))
    return people[0][3]


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-score", type=float, default=None,
                    help="only enrich rows whose score is above this value")
    ap.add_argument("--only", type=str, default=None,
                    help="comma-separated company names to enrich")
    args = ap.parse_args()

    key = load_key()
    if not key:
        print("NO KEY: add HUNTER_API_KEY to ~/.hermes/.env and rerun.")
        return 1

    rows = list(csv.DictReader(open(CSV_PATH)))
    print(f"rows: {len(rows)}")

    selected = rows
    if args.only:
        wanted = {n.strip().lower() for n in args.only.split(",") if n.strip()}
        selected = [r for r in rows if r["company"].strip().lower() in wanted]
        print(f"selected by name: {len(selected)} of {len(wanted)} requested")
        missing = wanted - {r["company"].strip().lower() for r in selected}
        if missing:
            print("NOT IN CSV:", sorted(missing))
    elif args.min_score is not None:
        selected = [r for r in rows if float(r["score"]) > args.min_score]
        print(f"selected by score > {args.min_score}: {len(selected)}")

    acct, err = call("account", {}, key)
    if acct:
        d = acct.get("data", {})
        print(f"account plan: {d.get('plan_name')}")
        for k in ("searches", "verifications"):
            if k in d:
                v = d[k]
                print(f"  {k}: used {v.get('used')} of {v.get('available')}" if isinstance(v, dict) else f"  {k}: {v}")
        ACCOUNT_JSON.write_text(json.dumps(acct, indent=2))
    else:
        print(f"account check failed: {err}")
        return 1

    CACHE.mkdir(exist_ok=True)
    today = date.today().isoformat()

    results = []
    for i, r in enumerate(rows, 1):
        if r not in selected:
            row = dict(r)
            for c in ("contact_name", "contact_role", "contact_email",
                      "email_confidence", "email_source_url", "lookup_date"):
                row.setdefault(c, "")
            if not row.get("hunter_status"):
                row["hunter_status"] = "not_run"
            results.append(row)
            continue

        url = r["url"].strip()
        domain = re.sub(r"^www\.", "", urllib.parse.urlparse(
            url if url.startswith(("http://", "https://")) else "https://" + url).netloc.lower())

        cache_file = CACHE / f"{domain}.json"
        if cache_file.exists():
            payload = json.loads(cache_file.read_text())
            status = "cached"
        else:
            payload, err = call("domain-search", {"domain": domain, "limit": 10}, key)
            if payload is None and err[0] == 400:
                detail = json.dumps(err[1])
                if "pagination" in detail or "limited to" in detail:
                    payload, err = call("domain-search", {"domain": domain, "limit": 10}, key)
            if payload is None:
                code = err[0]
                status = "error"
                payload = {"_error": {"code": code, "detail": err[1]}}
            else:
                status = "fetched"
            cache_file.write_text(json.dumps(payload, indent=2))
            time.sleep(1.2)

        entries = (payload.get("data", {}) or {}).get("emails", []) if isinstance(payload, dict) else []
        chosen = pick(entries)

        row = dict(r)
        if chosen:
            first = (chosen.get("first_name") or "").strip()
            last = (chosen.get("last_name") or "").strip()
            row["contact_name"] = f"{first} {last}".strip()
            row["contact_role"] = (chosen.get("position") or "").strip()
            row["contact_email"] = (chosen.get("value") or "").strip().lower()
            row["email_confidence"] = chosen.get("confidence") or ""
            srcs = [s.get("uri") for s in (chosen.get("sources") or []) if s.get("uri")]
            row["email_source_url"] = srcs[0] if srcs else ""
            row["hunter_status"] = "found"
        else:
            row["contact_name"] = ""
            row["contact_role"] = ""
            row["contact_email"] = ""
            row["email_confidence"] = ""
            row["email_source_url"] = ""
            if entries:
                row["hunter_status"] = "generic_only"
            elif status == "error":
                row["hunter_status"] = "error"
            else:
                row["hunter_status"] = "not_found"
        row["lookup_date"] = today
        results.append(row)

        if i % 20 == 0 or i == len(rows):
            found = sum(1 for x in results if x["hunter_status"] == "found")
            print(f"  {i}/{len(rows)}  found {found}  ({status})")

    fields = list(rows[0].keys())
    for c in ("contact_name", "contact_role", "contact_email", "email_confidence",
              "email_source_url", "hunter_status", "lookup_date"):
        if c not in fields:
            fields.append(c)
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(results)

    acct2, _ = call("account", {}, key)
    if acct2:
        ACCOUNT_JSON.write_text(json.dumps(acct2, indent=2))

    counts = {}
    for x in results:
        counts[x["hunter_status"]] = counts.get(x["hunter_status"], 0) + 1
    print(f"\nwrote {OUT_CSV}")
    print("status:", counts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
