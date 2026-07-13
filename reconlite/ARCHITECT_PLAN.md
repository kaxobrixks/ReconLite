# ReconLite Technical Plan

## 1. Technical Overview

ReconLite is a lightweight, standard-library-only Python OSINT tool that performs local reconnaissance on domains and usernames. It uses CLI-driven commands to gather publicly available information and outputs timestamped JSON and Markdown reports.

**Design Philosophy:** Simplicity, portability, and zero dependencies. Every feature relies exclusively on Python's standard library.

## 2. File Structure

```
reconlite/
├── main.py              # CLI entry point with argparse
├── modules/
│   ├── domain.py        # DNS lookup and domain reconnaissance
│   ├── username.py      # Username availability checker across public sites
│   └── report.py        # JSON and Markdown report generation
├── reports/             # Timestamped JSON report storage
└── README.md            # Usage documentation
```

The `modules/` directory encapsulates all business logic. The `reports/` directory is created at runtime and holds generated artifacts. No external configuration files are needed; site lists are embedded in `username.py`.

## 3. Module Descriptions

### 3.1 Domain Module (`domain.py`)

Accepts a domain string via CLI argument and performs DNS resolution using the `socket` module.

**Functions:**
- `resolve_ip(domain)` -- Returns A (IPv4) and AAAA (IPv6) records via `socket.getaddrinfo()` and `socket.gethostbyname_ex()`.
- `get_dns_records(domain)` -- Uses `socket.getmxlist()`-like logic and `socket.gethostbyname_ex()` to extract MX, NS, CNAME, and TXT records. For TXT records, falls back to `socket.getnameinfo()` where applicable.
- `run(domain)` -- Orchestrates lookups and returns a structured dictionary.

**Output Schema:**
```json
{
  "domain": "example.com",
  "a_records": ["93.184.216.34"],
  "aaaa_records": [],
  "mx_records": ["mail.example.com"],
  "ns_records": ["ns1.example.com"],
  "cname_records": [],
  "txt_records": []
}
```

### 3.2 Username Module (`username.py`)

Accepts a username and checks its availability across a configurable list of public websites.

**Configuration:**
Site list is defined as a Python dictionary at the top of the module:
```python
SITES = {
    "github": "https://github.com/{username}",
    "reddit": "https://www.reddit.com/user/{username}",
    # ... additional sites
}
```

**Functions:**
- `check_site(url, username)` -- Sends an HTTP HEAD request via `urllib.request.Request` with a custom User-Agent. Falls back to GET if HEAD returns 405. Evaluates the status code: 200 means found, 404 means not found.
- `run(username)` -- Iterates over all sites, collects results, and returns a structured dictionary.

**Output Schema:**
```json
{
  "username": "targetname",
  "found": [
    {"site": "github", "url": "https://github.com/targetname", "status": 200}
  ],
  "not_found": [
    {"site": "reddit", "url": "https://www.reddit.com/user/targetname", "status": 404}
  ]
}
```

### 3.3 Report Module (`report.py`)

Handles persistence of findings in two formats: JSON (machine-readable) and Markdown (human-readable).

**Functions:**
- `save_json(data, output_dir="reports")` -- Writes findings to a timestamped JSON file using `json.dump()` and `pathlib.Path` for path construction. Filename format: `recon_<YYYYMMDD>_<HHMMSS>.json`.
- `generate_markdown(json_path, md_path)` -- Reads the JSON report and produces a formatted Markdown document using `pathlib.Path` for file I/O.
- `load_latest(reports_dir="reports")` -- Finds the most recent JSON file in the reports directory and returns its parsed content.

### 3.4 Main CLI (`main.py`)

Provides a unified command-line interface using `argparse`.

**Commands:**
```
python main.py --domain example.com
python main.py --username targetname
python main.py --report latest
```

**Flow:**
1. Parse arguments with `argparse`.
2. Dispatch to the appropriate module based on flags.
3. On successful data collection, call `report.save_json()` to persist findings.
4. Call `report.generate_markdown()` to produce a human-readable summary.
5. Print a confirmation message with file paths.

## 4. Design Decisions

| Decision | Rationale |
|----------|-----------|
| Standard library only | Zero dependencies; works on any Python 3.8+ installation |
| `socket` for DNS | Universal availability; no `dnspython` required |
| HTTP HEAD with GET fallback | Efficient existence checking; avoids downloading bodies |
| Timestamped filenames | Prevents overwrites; enables chronological report review |
| JSON + Markdown dual output | JSON for programmatic consumption; Markdown for quick human review |
| Embedded site config | Single-file portability; no external JSON/YAML config needed |
| `pathlib` over `os.path` | Modern, cross-platform path handling with cleaner syntax |

## 5. Error Handling

- DNS failures return empty lists with a warning message, not exceptions.
- HTTP checks catch `urllib.error.URLError` and `TimeoutError`, marking sites as unreachable.
- Report directory is created with `pathlib.Path.mkdir(exist_ok=True)` if it does not exist.
- `--report latest` validates that at least one report file exists before attempting to load.

## 6. Limitations

- DNS resolution is limited to what `socket` provides; no zone transfers, reverse DNS sweeps, or WHOIS.
- Username checks detect public profile existence only; no login-gated or JavaScript-rendered content is scraped.
- No rate limiting between site checks; rapid execution may trigger basic rate limits on some platforms.
