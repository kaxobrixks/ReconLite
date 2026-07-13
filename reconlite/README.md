# ReconLite

**Lightweight OSINT Reconnaissance Tool** — Domain scanning, username checking, and report generation with a zero-friction, plugin-extensible CLI.

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status: Beta](https://img.shields.io/badge/status-beta-orange.svg)]()

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Domain Reconnaissance](#domain-reconnaissance)
  - [Username Availability Checking](#username-availability-checking)
  - [Report Viewing](#report-viewing)
  - [Plugin Discovery](#plugin-discovery)
  - [CLI Reference](#cli-reference)
- [Configuration](#configuration)
- [Plugin System](#plugin-system)
- [Project Structure](#project-structure)
- [Output Formats](#output-formats)
- [Contributing](#contributing)
- [Changelog](#changelog)
- [License](#license)

---

## Overview

ReconLite is a lightweight, command-line OSINT (Open Source Intelligence) reconnaissance tool written in Python. It performs two primary types of reconnaissance:

1. **Domain Reconnaissance** — Resolves DNS records (A, AAAA, MX, NS, CNAME, TXT, SOA) using Python's standard library, with optional enhanced resolution via the `dnspython` library.
2. **Username Availability Checking** — Checks whether a given username exists across multiple public websites (GitHub, Twitter/X, Instagram, Reddit, TikTok, etc.) using concurrent HTTP HEAD/GET requests.

All findings are automatically saved as timestamped JSON and Markdown reports in a configurable `reports/` directory.

---

## Features

- **Domain DNS Resolution**
  - A / AAAA (IPv4 / IPv6) record lookups
  - MX (Mail Exchange) records
  - NS (Name Server) records
  - CNAME (Canonical Name) records
  - TXT records
  - SOA (Start of Authority) records via dnspython
  - Graceful fallback to socket-based resolution when dnspython is unavailable

- **Username Availability Checking**
  - Checks 10 built-in platforms: GitHub, Twitter/X, Instagram, Reddit, TikTok, Pinterest, LinkedIn, YouTube, Twitch, Flickr
  - Concurrent multi-threaded checking via `ThreadPoolExecutor` (5–7× faster than sequential)
  - HEAD request with automatic GET fallback for reliable detection
  - Custom user-agent string mimicking modern browsers
  - Configurable site lists via YAML/JSON files

- **Report Generation**
  - JSON reports (machine-readable) with pretty-printing
  - Markdown reports (human-readable) with structured sections
  - Timestamped filenames (`recon_YYYYMMDD_HHMMSS.json` / `.md`)
  - Automatic report directory creation
  - Latest report display from CLI

- **Plugin System**
  - Abstract base classes: `ReconLitePlugin`, `CheckerPlugin`, `EnricherPlugin`, `FormatterPlugin`
  - Create custom checkers, data enrichers, or report formatters
  - Discover installed plugins via `--list-plugins`

- **Configuration System**
  - Multi-source configuration: defaults + user config file + environment variables
  - Config locations: `%APPDATA%/reconlite/config.yaml` (Windows), `~/.config/reconlite/config.yaml` (Linux/Mac), `./config/config.yaml` (project-local)
  - Environment variable overrides (e.g., `RECONLITE_GENERAL_TIMEOUT=30`)
  - YAML and JSON config file support

- **Zero-Friction Dependencies**
  - Core functionality requires **no third-party packages** — pure Python standard library
  - Optional `dnspython` for enhanced DNS resolution
  - Optional `pyyaml` for YAML config files

---

## Installation

### Prerequisites

- **Python 3.7+** (tested on Python 3.7 through 3.12)
- pip (Python package manager)

### Step 1: Clone or Extract

```bash
# Clone the repository
git clone https://github.com/yourusername/reconlite.git
cd reconlite

# OR extract from archive
tar -xzf reconlite.tar.gz
cd reconlite
```

### Step 2: Install Dependencies (Optional)

ReconLite works with **zero dependencies** using only the Python standard library. For enhanced features, install optional packages:

```bash
# Core optional: dnspython for accurate DNS resolution
pip install dnspython

# Config optional: pyyaml for YAML configuration files
pip install pyyaml

# UI optional: tqdm for progress bars
pip install tqdm

# Install all optional dependencies
pip install dnspython pyyaml tqdm
```

### Step 3: Verify Installation

```bash
python main.py --version
```

Expected output:
```
ReconLite v1.1.0
```

---

## Quick Start

Run your first reconnaissance in under a minute:

```bash
# Domain reconnaissance
python main.py --domain example.com

# Username availability check
python main.py --username targetuser

# View the latest report
python main.py --report latest
```

Reports are saved in the `reports/` directory as timestamped JSON and Markdown files.

---

## Usage

### Domain Reconnaissance

Perform DNS reconnaissance on a domain:

```bash
python main.py --domain example.com
```

Output:
```
[+] Running domain reconnaissance for: example.com

[*] Domain: example.com
[*] IP Addresses: 93.184.216.34
[*] Aliases: None found
[*] MX Records: 10 mail.example.com
[*] NS Records: a.iana-servers.net, b.iana-servers.net
[*] CNAME Records: None found
[*] TXT Records: v=spf1 -all

[+] JSON report saved to: reports/recon_20260713_120000.json
[+] Markdown report saved to: reports/recon_20260713_120000.md

[+] Domain reconnaissance complete.
```

### Username Availability Checking

Check a username across 10 platforms:

```bash
python main.py --username targetuser
```

Output:
```
[+] Running username availability check for: targetuser

[*] Username: targetuser
[*] Found on 3/10 sites

[+] Found profiles:
    [+] GitHub: https://github.com/targetuser (HTTP 200)
    [+] Reddit: https://www.reddit.com/user/targetuser (HTTP 200)
    [+] Twitch: https://www.twitch.tv/targetuser (HTTP 200)

[-] Not found on:
    [-] Twitter/X: https://twitter.com/targetuser (HTTP 404)
    [-] Instagram: https://www.instagram.com/targetuser (HTTP 404)
    ...

[+] JSON report saved to: reports/recon_20260713_120500.json
[+] Markdown report saved to: reports/recon_20260713_120500.md

[+] Username reconnaissance complete.
```

### Report Viewing

Display the most recently generated report:

```bash
python main.py --report latest
```

### Plugin Discovery

List all discovered plugins:

```bash
python main.py --list-plugins
```

### CLI Reference

```
usage: main.py [-h] [--domain DOMAIN] [--username USERNAME]
               [--report {LATEST,path}] [--reports-dir DIR]
               [--list-plugins] [--version]
```

| Flag | Description | Example |
|------|-------------|---------|
| `--domain DOMAIN` | Run domain DNS reconnaissance | `--domain example.com` |
| `--username USERNAME` | Check username availability | `--username targetuser` |
| `--report {LATEST,path}` | Display latest or specific report | `--report latest` |
| `--reports-dir DIR` | Override reports output directory | `--reports-dir ./my_reports` |
| `--list-plugins` | List discovered plugins | `--list-plugins` |
| `--version` | Display version information | `--version` |
| `-h, --help` | Show help message | `-h` |

---

## Configuration

### Config File Locations

ReconLite searches for configuration files in the following order:

1. **User config (Windows):** `%APPDATA%/reconlite/config.yaml`
2. **User config (Linux/Mac):** `~/.config/reconlite/config.yaml`
3. **Project-local:** `./config/config.yaml`

### Default Configuration

```yaml
# config/default.yaml

general:
  reports_dir: "./reports"
  timeout: 10
  max_workers: 5
  log_level: "INFO"

username_check:
  sites_file: null          # null = use built-in sites; set path to custom list
  rate_limit_delay: 0.0
  follow_redirects: true
  max_workers: 5
  timeout: 10

dns:
  use_dnspython: false      # Set true for enhanced DNS resolution
  timeout: 5
  servers: []               # Empty = use system DNS

reporting:
  formats:
    - json
    - markdown
  include_raw: false
```

### Environment Variable Overrides

All configuration values can be overridden via environment variables using the pattern `RECONLITE_<SECTION>_<KEY>`:

```bash
# Override timeout to 30 seconds
export RECONLITE_GENERAL_TIMEOUT=30

# Override max workers
export RECONLITE_USERNAME_CHECK_MAX_WORKERS=10

# Override reports directory
export RECONLITE_GENERAL_REPORTS_DIR=./custom_reports
```

### Custom Site Lists

Create a custom sites file (YAML or JSON) to add platforms for username checking:

```yaml
# config/custom_sites.yaml
MySite: "https://mysite.com/users/{username}"
Forum: "https://forum.example.com/member/{username}"
```

Reference it in your config:

```yaml
username_check:
  sites_file: "./config/custom_sites.yaml"
```

---

## Plugin System

ReconLite supports a plugin architecture for extending functionality. All plugins inherit from the abstract `ReconLitePlugin` base class defined in [`plugins/base.py`](plugins/base.py).

### Plugin Types

| Type | Class | Purpose |
|------|-------|---------|
| **Checker** | `CheckerPlugin` | Check targets (usernames/domains) against services |
| **Enricher** | `EnricherPlugin` | Add data to existing reconnaissance results |
| **Formatter** | `FormatterPlugin` | Generate custom report formats |

### Creating a Custom Plugin

```python
# plugins/my_checker.py
from plugins.base import CheckerPlugin


class MyCustomChecker(CheckerPlugin):
    @property
    def plugin_name(self) -> str:
        return "my_custom_checker"

    @property
    def plugin_version(self) -> str:
        return "1.0.0"

    @property
    def plugin_author(self) -> str:
        return "Your Name"

    @property
    def plugin_description(self) -> str:
        return "Checks username on my custom platform"

    def check(self, target: str, **kwargs) -> list:
        url = f"https://mysite.com/{target}"
        # Perform HTTP check and return results
        return [{
            "site": "MySite",
            "url": url,
            "status": 200,
            "found": True,
            "timestamp": 0,
        }]
```

### Plugin Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `plugin_name` | `str` | Yes | Unique identifier for the plugin |
| `plugin_version` | `str` | Yes | Semantic version string (e.g., `1.0.0`) |
| `plugin_description` | `str` | No | Human-readable description |
| `plugin_author` | `str` | No | Author name |

### Plugin Methods

| Method | Description |
|--------|-------------|
| `is_enabled(config)` | Check if plugin should be active based on config |
| `validate_input(data)` | Validate input data, return list of error messages |
| `execute(*args, **kwargs)` | Main execution method (delegates to `check()`, `enrich()`, or `format()`) |

---

## Project Structure

```
reconlite/
├── main.py                     # CLI entry point and argument parsing
├── config.py                   # Configuration loading (YAML/JSON/env)
├── requirements.txt            # Optional dependency specifications
├── CHANGELOG.md                # Version history and release notes
├── README.md                   # This file
├── ARCHITECT_PLAN.md           # Architecture design document
├── UPGRADE_PLAN.md             # Upgrade roadmap
├── config/
│   ├── default.yaml            # Default configuration template
│   └── default_sites.yaml      # Default site list for username checks
├── modules/
│   ├── domain.py               # Domain DNS resolution module
│   ├── username.py             # Username availability checker module
│   └── report.py               # JSON and Markdown report generation
├── plugins/
│   └── base.py                 # Abstract plugin base classes
└── reports/                    # Generated reports (created automatically)
    ├── recon_YYYYMMDD_HHMMSS.json
    └── recon_YYYYMMDD_HHMMSS.md
```

### Module Descriptions

| Module | Purpose |
|--------|---------|
| [`main.py`](main.py) | CLI interface, argument parsing, orchestration |
| [`config.py`](config.py) | Multi-source configuration loading and merging |
| [`modules/domain.py`](modules/domain.py) | DNS record resolution (socket + dnspython) |
| [`modules/username.py`](modules/username.py) | Concurrent username availability checking |
| [`modules/report.py`](modules/report.py) | JSON and Markdown report generation |
| [`plugins/base.py`](plugins/base.py) | Abstract plugin base classes |

---

## Output Formats

### JSON Report

Timestamped JSON files contain structured reconnaissance data:

```json
{
  "domain": "example.com",
  "ip_addresses": [
    "93.184.216.34"
  ],
  "aliases": [],
  "mx_records": [
    "10 mail.example.com"
  ],
  "ns_records": [
    "a.iana-servers.net",
    "b.iana-servers.net"
  ],
  "cname_records": [],
  "txt_records": [
    "v=spf1 -all"
  ],
  "timestamp": 1720876800
}
```

### Markdown Report

Human-readable Markdown reports with structured sections:

```markdown
# ReconLite Reconnaissance Report

**Generated:** 2026-07-13 12:00:00 UTC

---

## Domain Information

**Domain:** `example.com`

### IP Addresses (A/AAAA Records)

- `93.184.216.34`

### MX Records (Mail Exchange)

- `10 mail.example.com`
```

---

## Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/my-feature`)
3. **Commit** your changes (`git commit -am 'Add my feature'`)
4. **Push** to the branch (`git push origin feature/my-feature`)
5. **Open** a Pull Request

### Development Setup

```bash
git clone https://github.com/yourusername/reconlite.git
cd reconlite
pip install dnspython pyyaml
python main.py --help
```

### Adding a Plugin

1. Create a new file in the `plugins/` directory
2. Inherit from the appropriate base class (`CheckerPlugin`, `EnricherPlugin`, or `FormatterPlugin`)
3. Implement all abstract methods
4. Test with `python main.py --list-plugins`

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the complete version history and release notes.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

*ReconLite v1.1.0 — Built with Python 3.7+*
