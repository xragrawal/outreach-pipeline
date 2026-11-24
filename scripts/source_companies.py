#!/usr/bin/env python3
"""Find candidate companies for a run and write its source CSV.

The worker searches Exa through the zero-config Agent Reach MCP command. It
builds search queries from the run's weighted taxonomy and value proposition.
It keeps company websites, removes common content sites, and merges manual CSV
rows with the new web results.

Usage
-----
    python3 scripts/source_companies.py --run runs/acme
"""

import argparse
import csv
import json
import re
import shutil
import subprocess
import tempfile
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


BASE = Path(__file__).resolve().parent.parent

DEFAULT_COLUMNS = {
    "id": "company",
    "url": "url",
    "segment": "segment",
    "category": "category",
    "summary": "service_summary",
    "services": "services",
    "sales_route": "sales_route",
    "evidence_type": "evidence_type",
    "headcount": "headcount",
}

DEFAULT_SOURCING = {
    "provider": "exa",
    "max_companies": 30,
    "results_per_query": 8,
    "query_count": 4,
    "timeout_seconds": 30,
    "search_retries": 3,
    "fetch_details": True,
    "detail_timeout_seconds": 12,
    "queries": [],
}

EXCLUDED_DOMAINS = {
    "alternativeto.net", "appsource.microsoft.com", "bloomberg.com",
    "businessinsider.com", "capterra.com", "cbinsights.com", "coindesk.com",
    "coinmarketcap.com", "crunchbase.com", "facebook.com", "forbes.com",
    "g2.com", "gartner.com", "github.com", "glassdoor.com", "instagram.com",
    "linkedin.com", "luma.com", "medium.com", "producthunt.com", "reddit.com",
    "rootdata.com", "solutionsreview.com", "sourceforge.net", "substack.com",
    "t.me", "techcrunch.com", "theblock.co", "tracxn.com", "trustpilot.com", "twitter.com",
    "wikipedia.org", "x.com", "youtube.com",
}

GENERATED_EVIDENCE = {"company_website", "exa_web_search"}

STOP_WORDS = {
    "a", "an", "and", "as", "at", "by", "for", "from", "in", "into",
    "of", "on", "or", "the", "through", "to", "with", "controlled",
    "dynamic", "real", "time",
}

GENERIC_TITLES = {
    "about", "documentation", "home", "introduction", "overview",
    "platform", "trade perpetuals", "welcome",
}

COMPOUND_SUFFIXES = {
    "co.uk", "com.au", "com.br", "com.sg", "co.in", "co.jp", "co.nz",
    "com.cn", "com.hk", "com.mx", "com.tr", "co.za",
}


def read_csv(path):
    if not path.exists():
        return [], []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader)


def load_run(run_dir):
    run = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    with (run_dir / "taxonomy.csv").open(encoding="utf-8-sig", newline="") as handle:
        taxonomy = list(csv.DictReader(handle))
    taxonomy = [row for row in taxonomy if (row.get("tag") or "").strip()]
    if not taxonomy:
        raise SystemExit("taxonomy.csv has no capability rows")
    return run, taxonomy


def clean_space(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def first_sentence(value, limit=180):
    text = clean_space(value)
    sentence = re.split(r"(?<=[.!?])\s+", text, maxsplit=1)[0]
    return sentence[:limit].rstrip(" ,.;:")


def weighted_tags(taxonomy):
    def weight(row):
        try:
            return float(row.get("weight") or 0)
        except ValueError:
            return 0

    return sorted(taxonomy, key=lambda row: (-weight(row), row["tag"].casefold()))


def build_queries(run, taxonomy, sourcing):
    configured = [clean_space(query) for query in sourcing.get("queries", []) if clean_space(query)]
    if configured:
        return [(query, []) for query in configured[:sourcing["query_count"]]]

    ordered = weighted_tags(taxonomy)
    core = [row["tag"] for row in ordered
            if str(row.get("core") or "").strip().lower() in {"1", "true", "yes"}]
    tags = [row["tag"] for row in ordered]
    subject = clean_space(run.get("subject"))
    value = first_sentence((run.get("brief") or {}).get("value_proposition"))

    bundles = []
    if core:
        bundles.append((f'companies similar to "{subject}" ' + " ".join(core[:2]), core[:2]))
    if value:
        bundles.append((f"{value} alternatives platforms official", tags[:3]))
    bundles.append((" ".join(tags[:3]) + " platform company official", tags[:3]))
    if len(tags) > 3:
        bundles.append((" ".join(tags[3:6]) + " platform company official", tags[3:6]))
    if len(tags) > 6:
        bundles.append((" ".join(tags[6:9]) + " platform company official", tags[6:9]))

    queries = []
    seen = set()
    for query, capabilities in bundles:
        query = clean_space(query)
        key = query.casefold()
        if query and key not in seen:
            seen.add(key)
            queries.append((query, capabilities))
    return queries[:sourcing["query_count"]]


def search_exa(query, count, timeout, retries=3):
    if not shutil.which("mcporter"):
        raise RuntimeError("mcporter is not installed. Install Agent Reach or import a candidate CSV.")
    command = [
        "mcporter", "call", "exa.web_search_exa",
        f"query={query}", f"numResults={count}",
    ]
    detail = ""
    for attempt in range(1, max(int(retries), 1) + 1):
        done = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        if not done.returncode:
            return parse_exa(done.stdout)
        detail = clean_space(done.stderr or done.stdout)
        if attempt < retries:
            time.sleep(attempt)
    raise RuntimeError(f"Exa search failed after {retries} attempts: {detail[:300]}")


def parse_exa(output):
    text = re.sub(r"\x1b\[[0-9;]*m", "", output)
    blocks = re.split(r"(?m)^---\s*$", text)
    results = []
    for block in blocks:
        title_match = re.search(r"(?m)^Title:\s*(.+)$", block)
        url_match = re.search(r"(?m)^URL:\s*(\S+)", block)
        if not title_match or not url_match:
            continue
        highlight_match = re.search(r"(?ms)^Highlights:\s*(.*)$", block)
        results.append({
            "title": clean_space(title_match.group(1)),
            "url": url_match.group(1).strip(),
            "summary": clean_space(highlight_match.group(1) if highlight_match else ""),
        })
    return results


class PageParser(HTMLParser):
    """Extract useful visible text and metadata without external packages."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.description = ""
        self.title = ""
        self.parts = []
        self._skip = 0
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        attrs = {key.lower(): value for key, value in attrs if key}
        if tag in {"script", "style", "svg", "noscript"}:
            self._skip += 1
        if tag == "title":
            self._in_title = True
        if tag == "meta":
            name = (attrs.get("name") or attrs.get("property") or "").lower()
            if name in {"description", "og:description", "twitter:description"}:
                value = clean_space(attrs.get("content"))
                if len(value) > len(self.description):
                    self.description = value

    def handle_endtag(self, tag):
        if tag in {"script", "style", "svg", "noscript"} and self._skip:
            self._skip -= 1
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._skip:
            return
        value = clean_space(data)
        if not value:
            return
        if self._in_title:
            self.title = clean_space(f"{self.title} {value}")
        self.parts.append(value)

    @property
    def text(self):
        return clean_space(" ".join(self.parts))


def fetch_page(url, timeout):
    """Fetch one company page. Use Jina Reader when the site blocks direct access."""
    attempts = [url, f"https://r.jina.ai/{url}"]
    last_error = None
    for target in attempts:
        try:
            request = Request(target, headers={
                "Accept": "text/html,text/plain;q=0.9,*/*;q=0.1",
                "User-Agent": "Mozilla/5.0 (compatible; outreach-pipeline/1.0)",
            })
            with urlopen(request, timeout=timeout) as response:
                content_type = response.headers.get_content_type()
                raw = response.read(1_500_000)
                charset = response.headers.get_content_charset() or "utf-8"
            text = raw.decode(charset, errors="replace")
            if target.startswith("https://r.jina.ai/") or content_type == "text/plain":
                return {"title": "", "description": "", "text": clean_space(text)}
            parser = PageParser()
            parser.feed(text)
            return {
                "title": parser.title,
                "description": parser.description,
                "text": parser.text,
            }
        except Exception as exc:  # Network failures use the Exa content instead.
            last_error = exc
    return {"title": "", "description": "", "text": "", "error": str(last_error or "fetch failed")}


def root_domain(url):
    try:
        host = (urlsplit(url).hostname or "").lower().strip(".")
    except ValueError:
        return ""
    if host.startswith("www."):
        host = host[4:]
    parts = host.split(".")
    if len(parts) <= 2:
        return host
    last_two = ".".join(parts[-2:])
    if last_two in COMPOUND_SUFFIXES and len(parts) >= 3:
        return ".".join(parts[-3:])
    return last_two


def domain_label(domain):
    label = domain.split(".")[0]
    words = re.split(r"[-_]", label)
    return " ".join(word.upper() if len(word) <= 3 else word.capitalize() for word in words)


def company_name(title, domain):
    candidate = re.split(r"\s+(?:\||—|–|-|:)\s+", title, maxsplit=1)[0]
    candidate = re.sub(r"^(?:what is|about)\s+", "", candidate, flags=re.I)
    candidate = clean_space(candidate).strip(" .,:;!?")
    if not candidate or candidate.casefold() in GENERIC_TITLES or len(candidate) > 60:
        return domain_label(domain)
    if len(candidate.split()) > 3:
        return domain_label(domain)
    return candidate


def tokens(value):
    words = re.findall(r"[a-z0-9]+", str(value or "").lower().replace("non-custodial", "noncustodial"))
    return {word for word in words if word not in STOP_WORDS and (len(word) > 2 or word in {"ai"})}


def matched_capabilities(result, taxonomy, query_capabilities):
    text = " ".join([
        result["title"], result["summary"], result["url"], result.get("page_text", ""),
    ])
    text_tokens = tokens(text)
    matches = []
    query_set = {name.casefold() for name in query_capabilities}
    for row in weighted_tags(taxonomy):
        tag = row["tag"].strip()
        tag_tokens = tokens(tag)
        overlap = len(tag_tokens & text_tokens)
        threshold = 1 if len(tag_tokens) <= 2 else 2
        if tag.casefold() in text.casefold():
            matches.append(tag)
        elif overlap >= threshold and overlap / max(len(tag_tokens), 1) >= 0.34:
            matches.append(tag)
        elif tag.casefold() in query_set and overlap >= 1:
            matches.append(tag)
    return matches


def clean_summary(value, limit=700):
    text = re.sub(r"[#*_`>|]+", " ", value or "")
    text = clean_space(text)
    return text[:limit].rstrip()


def best_summary(result):
    page_description = clean_summary(result.get("page_description", ""))
    if len(page_description) >= 40:
        return page_description
    page_text = clean_summary(result.get("page_text", ""))
    if len(page_text) >= 80:
        return page_text
    return clean_summary(result["summary"])


def result_to_row(result, capabilities, cols):
    domain = root_domain(result["url"])
    return {
        cols["id"]: company_name(result["title"], domain),
        cols["url"]: f"https://{domain}/",
        cols["segment"]: "Similar company",
        cols["category"]: capabilities[0],
        cols["summary"]: best_summary(result),
        cols["services"]: "; ".join(capabilities),
        cols["sales_route"]: "Company website",
        cols["evidence_type"]: "company_website" if result.get("page_text") else "exa_web_search",
        cols["headcount"]: "",
    }


def merge_rows(existing, generated, cols, maximum):
    evidence_col = cols["evidence_type"]
    manual = [row for row in existing
              if clean_space(row.get(evidence_col)).casefold() not in GENERATED_EVIDENCE]
    merged = []
    seen = set()
    manual_kept = 0
    for index, row in enumerate(manual + generated):
        domain = root_domain(row.get(cols["url"], ""))
        company = clean_space(row.get(cols["id"], "")).casefold()
        key = domain or company
        if not key or key in seen:
            continue
        seen.add(key)
        merged.append(row)
        if index < len(manual):
            manual_kept += 1
    return merged[:manual_kept + maximum], manual_kept


def write_csv(path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, dir=path.parent,
                                     encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
        temp_path = Path(handle.name)
    temp_path.replace(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", required=True, help="run folder")
    args = parser.parse_args()

    run_dir = Path(args.run).resolve()
    run, taxonomy = load_run(run_dir)
    cols = {**DEFAULT_COLUMNS, **run.get("columns", {})}
    sourcing = {**DEFAULT_SOURCING, **run.get("sourcing", {})}
    provider = str(sourcing["provider"]).casefold()
    if provider != "exa":
        raise SystemExit(f"unsupported sourcing provider: {provider}")

    source_path = run_dir / run.get("source_csv", "universe.csv")
    existing_fields, existing_rows = read_csv(source_path)
    queries = build_queries(run, taxonomy, sourcing)
    subject_domain = root_domain(run.get("subject_url") or run.get("subject") or "")
    subject_label = subject_domain.split(".")[0].casefold()
    discoveries = {}
    errors = []

    print(f"  INFO  provider: Exa through Agent Reach")
    print(f"  INFO  queries: {len(queries)}")
    for index, (query, query_capabilities) in enumerate(queries, 1):
        print(f"  SEARCH {index}/{len(queries)} {query}")
        try:
            found = search_exa(
                query,
                int(sourcing["results_per_query"]),
                int(sourcing["timeout_seconds"]),
                int(sourcing["search_retries"]),
            )
        except (RuntimeError, subprocess.TimeoutExpired) as exc:
            errors.append(str(exc))
            print(f"  WARN  {exc}")
            continue
        print(f"  FOUND {len(found)} web results")
        for result in found:
            domain = root_domain(result["url"])
            if not domain or domain == subject_domain or domain in EXCLUDED_DOMAINS:
                continue
            result_text = clean_space(result["title"] + " " + result["summary"][:500]).casefold()
            if len(subject_label) >= 5 and subject_label in result_text:
                continue
            current = discoveries.get(domain)
            if current:
                current["summary"] = clean_space(current["summary"] + " " + result["summary"])
                current["query_capabilities"].update(query_capabilities)
                continue
            result["domain"] = domain
            result["query_capabilities"] = set(query_capabilities)
            discoveries[domain] = result

    generated = []
    candidates = list(discoveries.values())[:int(sourcing["max_companies"])]
    if sourcing.get("fetch_details"):
        print(f"  INFO  fetching details from {len(candidates)} company pages")
    for index, result in enumerate(candidates, 1):
        result["page_text"] = ""
        result["page_description"] = ""
        if sourcing.get("fetch_details"):
            print(f"  FETCH {index}/{len(candidates)} https://{result['domain']}/")
            page = fetch_page(result["url"], int(sourcing["detail_timeout_seconds"]))
            result["page_text"] = page.get("text", "")
            result["page_description"] = page.get("description", "")
            if page.get("title"):
                result["title"] = page["title"]
        capabilities = matched_capabilities(
            result, taxonomy, sorted(result["query_capabilities"]))
        if not capabilities:
            continue
        generated.append(result_to_row(result, capabilities, cols))

    merged, manual_count = merge_rows(
        existing_rows, generated, cols, int(sourcing["max_companies"]))
    if not merged:
        detail = errors[0] if errors else "search returned no relevant company websites"
        raise SystemExit(f"automatic sourcing found no candidates: {detail}")

    fields = list(existing_fields)
    for name in cols.values():
        if name not in fields:
            fields.append(name)
    write_csv(source_path, fields, merged)
    generated_count = len(merged) - manual_count
    print(f"  WRITE {source_path}")
    print(f"  INFO  {generated_count} web candidates, {manual_count} manual candidates")


if __name__ == "__main__":
    main()
