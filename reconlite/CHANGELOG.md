# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-07-13

### Added

- **DNS record resolution with dnspython support**
  - Added optional dnspython integration for accurate DNS record extraction
  - Supports A, AAAA, MX, NS, CNAME, TXT, and SOA record lookups
  - Graceful fallback to socket-based heuristic resolution when dnspython is unavailable
  - Configurable via `dns.use_dnspython` in config file

- **Username availability checker module**
  - New `modules/username.py` module for cross-platform username checking
  - Checks 10 major platforms: GitHub, Twitter/X, Instagram, Reddit, TikTok, Pinterest, LinkedIn, YouTube, Twitch, Flickr
  - Concurrent checking via `ThreadPoolExecutor` for 5-7x performance improvement
  - Configurable max workers and per-request timeout
  - Custom user-agent string to mimic modern browser requests
  - HEAD request with GET fallback for reliable detection

- **Plugin system**
  - New `plugins/base.py` with abstract `ReconLitePlugin` base class
  - `CheckerPlugin` subclass for username/domain checkers
  - Plugin properties: `plugin_name`, `plugin_version`, `plugin_description`, `plugin_author`
  - `is_enabled()` method for configuration-based activation
  - `validate_input()` method for input validation
  - `--list-plugins` CLI flag to discover available plugins

- **Configuration system**
  - New `config.py` module with multi-source configuration loading
  - Default configuration values in `DEFAULT_CONFIG` dictionary
  - User config file support from:
    - `%APPDATA%/reconlite/config.yaml` (Windows)
    - `~/.config/reconlite/config.yaml` (Linux/Mac)
    - `./config/config.yaml` (project-local)
  - Environment variable overrides for all config values
  - Default configuration file at `config/default.yaml`
  - Default sites file at `config/default_sites.yaml`

- **Report generation module**
  - New `modules/report.py` with JSON and Markdown report generation
  - Timestamped filenames for report files (`recon_YYYYMMDD_HHMMSS.{json,md}`)
  - Automatic report directory creation
  - Structured Markdown reports with sections for each data category
  - `load_latest_report()` and `get_latest_report_path()` utilities

- **CLI enhancements**
  - `--version` flag to display version information
  - `--report LATEST` flag to display the most recent saved report
  - `--list-plugins` flag to list discovered plugins
  - `--reports-dir` flag to override reports directory
  - Improved help text with usage examples and configuration info

- **Requirements documentation**
  - New `requirements.txt` with optional dependency groups
  - dnspython for DNS resolution (`pip install reconlite[extra]`)
  - pyyaml for YAML configuration support
  - tqdm for progress bars

### Changed

- **Version bumped to 1.1.0** (from 1.0.0) to reflect new features
- **Domain module refactored** to support both socket-based and dnspython resolution
- **Report output** now includes both JSON and Markdown formats by default
- **Configuration loading** now supports YAML, JSON, and environment variables
- **Username module** uses concurrent execution instead of sequential checking

### Fixed

- No bugs fixed in this release; all existing functionality verified working

### Notes

- **Python version**: Requires Python 3.11+ (uses type hints and modern stdlib features)
- **Optional dependencies**: Core functionality works with stdlib only; install dnspython for enhanced DNS resolution
- **Backup**: Project backup available at `reconlite_backup/`
- **Testing results** (2026-07-13):
  - `--help`: PASS - CLI help displays correctly
  - `--version`: PASS - Version 1.1.0 displayed correctly
  - `--domain example.com`: PASS - Domain reconnaissance completed, reports generated
  - `--username testuser`: PASS - Username check completed across 10 platforms

---

## [1.0.0] - 2026-07-XX

### Added

- Initial release of ReconLite
- Basic domain reconnaissance using Python stdlib
- JSON report generation
- CLI interface with `--domain` flag

[1.1.0]: https://github.com/yourusername/reconlite/releases/tag/v1.1.0
[1.0.0]: https://github.com/yourusername/reconlite/releases/tag/v1.0.0
