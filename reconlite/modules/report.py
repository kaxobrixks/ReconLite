"""
Report generation module for ReconLite.

Handles persistence of reconnaissance findings in JSON (machine-readable)
and Markdown (human-readable) formats. Reports are timestamped and stored
in a configurable reports directory.
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


def _get_timestamp_filename(prefix: str = "recon") -> str:
    """
    Generate a timestamped filename for report storage.

    Format: {prefix}_YYYYMMDD_HHMMSS.{ext}

    Args:
        prefix: Filename prefix (default: 'recon').

    Returns:
        Timestamped filename string.
    """
    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{ts}"


def _ensure_reports_dir(reports_dir: str) -> Path:
    """
    Ensure the reports directory exists, creating it if necessary.

    Args:
        reports_dir: Path to the reports directory.

    Returns:
        Path object pointing to the reports directory.
    """
    path = Path(reports_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_json_report(data: Dict[str, Any], reports_dir: str = "reports") -> str:
    """
    Save reconnaissance data as a timestamped JSON file.

    Creates the reports directory if it doesn't exist. Writes the data
    as pretty-printed JSON with UTF-8 encoding.

    Args:
        data: Dictionary containing the reconnaissance findings.
        reports_dir: Directory to store reports in (default: 'reports').

    Returns:
        Absolute file path to the saved JSON report.

    Raises:
        OSError: If the report directory cannot be created or file cannot be written.
        TypeError: If data is not JSON-serializable.
    """
    filename = _get_timestamp_filename("recon") + ".json"
    reports_path = _ensure_reports_dir(reports_dir)
    file_path = reports_path / filename

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    return str(file_path)


def generate_markdown_report(data: Dict[str, Any], reports_dir: str = "reports") -> str:
    """
    Generate a human-readable Markdown report from reconnaissance data.

    Creates the reports directory if it doesn't exist. Produces a formatted
    Markdown document with sections for each data category.

    Args:
        data: Dictionary containing the reconnaissance findings.
        reports_dir: Directory to store reports in (default: 'reports').

    Returns:
        Absolute file path to the saved Markdown report.

    Raises:
        OSError: If the report directory cannot be created or file cannot be written.
    """
    filename = _get_timestamp_filename("recon") + ".md"
    reports_path = _ensure_reports_dir(reports_dir)
    file_path = reports_path / filename

    lines: list = []

    # Header
    lines.append("# ReconLite Reconnaissance Report")
    lines.append("")

    # Timestamp
    timestamp = data.get("timestamp", "N/A")
    if isinstance(timestamp, (int, float)):
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        timestamp_str = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    else:
        timestamp_str = str(timestamp)
    lines.append(f"**Generated:** {timestamp_str}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Domain section
    if "domain" in data:
        lines.append("## Domain Information")
        lines.append("")
        lines.append(f"**Domain:** `{data['domain']}`")
        lines.append("")

        # IP addresses
        ip_addresses = data.get("ip_addresses", [])
        lines.append("### IP Addresses (A/AAAA Records)")
        lines.append("")
        if ip_addresses:
            for ip in ip_addresses:
                lines.append(f"- `{ip}`")
        else:
            lines.append("- *No IP addresses resolved*")
        lines.append("")

        # Aliases
        aliases = data.get("aliases", [])
        lines.append("### Hostname Aliases")
        lines.append("")
        if aliases:
            for alias in aliases:
                lines.append(f"- `{alias}`")
        else:
            lines.append("- *No aliases found*")
        lines.append("")

        # MX records
        mx_records = data.get("mx_records", [])
        lines.append("### MX Records (Mail Exchange)")
        lines.append("")
        if mx_records:
            for mx in mx_records:
                lines.append(f"- `{mx}`")
        else:
            lines.append("- *No MX records found*")
        lines.append("")

        # NS records
        ns_records = data.get("ns_records", [])
        lines.append("### NS Records (Name Servers)")
        lines.append("")
        if ns_records:
            for ns in ns_records:
                lines.append(f"- `{ns}`")
        else:
            lines.append("- *No NS records found*")
        lines.append("")

        # CNAME records
        cname_records = data.get("cname_records", [])
        lines.append("### CNAME Records (Canonical Names)")
        lines.append("")
        if cname_records:
            for cname in cname_records:
                lines.append(f"- `{cname}`")
        else:
            lines.append("- *No CNAME records found*")
        lines.append("")

        # TXT records
        txt_records = data.get("txt_records", [])
        lines.append("### TXT Records")
        lines.append("")
        if txt_records:
            for txt in txt_records:
                lines.append(f"- `{txt}`")
        else:
            lines.append("- *No TXT records found*")
        lines.append("")

    # Username section
    if "username" in data or "results" in data:
        lines.append("## Username Availability")
        lines.append("")

        username = data.get("username", data.get("query", "N/A"))
        lines.append(f"**Username:** `{username}`")
        lines.append("")

        results = data.get("results", data.get("username_checks", []))
        if isinstance(results, list):
            found_count = sum(1 for r in results if r.get("found"))
            not_found_count = len(results) - found_count

            lines.append(f"**Found:** {found_count} | **Not Found:** {not_found_count}")
            lines.append("")

            # Table header
            lines.append("| Site | URL | Status | Found |")
            lines.append("|------|-----|--------|-------|")

            for r in results:
                site = r.get("site", "Unknown")
                url = r.get("url", "N/A")
                status = r.get("status", "N/A")
                found = "Yes" if r.get("found") else "No"
                lines.append(f"| {site} | {url} | {status} | {found} |")

            lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append("*Report generated by ReconLite - Standard library only, no dependencies.*")
    lines.append("")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return str(file_path)


def load_latest_report(reports_dir: str = "reports") -> Optional[Dict[str, Any]]:
    """
    Load the most recently created JSON report from the reports directory.

    Finds the JSON file with the latest timestamp in its filename and
    parses its contents.

    Args:
        reports_dir: Directory to search for reports (default: 'reports').

    Returns:
        Parsed JSON data as a dictionary, or None if no reports exist.
    """
    reports_path = Path(reports_dir)
    if not reports_path.exists():
        return None

    json_files = sorted(reports_path.glob("recon_*.json"))
    if not json_files:
        return None

    latest = json_files[-1]
    try:
        with open(latest, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def get_latest_report_path(reports_dir: str = "reports") -> Optional[str]:
    """
    Get the file path of the most recently created JSON report.

    Args:
        reports_dir: Directory to search for reports (default: 'reports').

    Returns:
        File path string, or None if no reports exist.
    """
    reports_path = Path(reports_dir)
    if not reports_path.exists():
        return None

    json_files = sorted(reports_path.glob("recon_*.json"))
    if not json_files:
        return None

    return str(json_files[-1])
