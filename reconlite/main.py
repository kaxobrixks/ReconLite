#!/usr/bin/env python3
"""
ReconLite - Lightweight OSINT reconnaissance tool.

A CLI-driven tool for performing local reconnaissance on domains and usernames.
Uses only Python standard library - no third-party dependencies required.

Usage:
    python main.py --domain example.com
    python main.py --username targetname
    python main.py --report latest
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Add parent directory to path for module imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from modules.domain import resolve_domain
from modules.username import check_username
from modules.report import (
    save_json_report,
    generate_markdown_report,
    load_latest_report,
    get_latest_report_path,
)
from config import get_config, load_sites

# ReconLite version
__version__ = "1.1.0"


def run_domain_recon(domain: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Run domain reconnaissance and save reports.

    Args:
        domain: The domain to analyze.
        config: Optional configuration dictionary.

    Returns:
        The reconnaissance data dictionary.
    """
    print(f"[+] Running domain reconnaissance for: {domain}")
    print()

    # Run domain module
    data = resolve_domain(domain)

    # Print results to console
    print(f"[*] Domain: {data['domain']}")
    print(f"[*] IP Addresses: {', '.join(data['ip_addresses']) if data['ip_addresses'] else 'None found'}")
    print(f"[*] Aliases: {', '.join(data['aliases']) if data['aliases'] else 'None found'}")
    print(f"[*] MX Records: {', '.join(data['mx_records']) if data['mx_records'] else 'None found'}")
    print(f"[*] NS Records: {', '.join(data['ns_records']) if data['ns_records'] else 'None found'}")
    print(f"[*] CNAME Records: {', '.join(data['cname_records']) if data['cname_records'] else 'None found'}")
    print(f"[*] TXT Records: {', '.join(data['txt_records']) if data['txt_records'] else 'None found'}")

    # Show SOA records if available (dnspython feature)
    soa_records = data.get('soa_records', [])
    if soa_records:
        print(f"[*] SOA Records: {', '.join(soa_records)}")

    print()

    # Save reports
    reports_dir = (config or {}).get("general", {}).get("reports_dir", "reports")
    json_path = save_json_report(data, reports_dir)
    print(f"[+] JSON report saved to: {json_path}")

    md_path = generate_markdown_report(data, reports_dir)
    print(f"[+] Markdown report saved to: {md_path}")
    print()
    print("[+] Domain reconnaissance complete.")

    return data


def run_username_recon(username: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Run username availability check and save reports.

    Args:
        username: The username to check across platforms.
        config: Optional configuration dictionary.

    Returns:
        The reconnaissance data dictionary.
    """
    print(f"[+] Running username availability check for: {username}")
    print()

    # Load configuration
    if config is None:
        config = get_config()

    username_config = config.get("username_check", {})

    # Load sites (custom or built-in)
    sites_file = username_config.get("sites_file")
    if sites_file:
        sites = load_sites(sites_file)
    else:
        from modules.username import SITES
        sites = SITES

    # Get concurrency settings
    max_workers = username_config.get("max_workers", 5)
    timeout = username_config.get("timeout", 10)

    # Run username module with concurrent checking
    results = check_username(username, sites=sites, max_workers=max_workers, timeout=timeout)

    # Compile results
    found_count = sum(1 for r in results if r.get("found"))
    not_found_count = len(results) - found_count

    data: Dict[str, Any] = {
        "username": username,
        "results": results,
        "timestamp": results[0]["timestamp"] if results else 0,
    }

    # Print results to console
    print(f"[*] Username: {username}")
    print(f"[*] Found on {found_count}/{len(results)} sites")
    print()

    if found_count > 0:
        print("[+] Found profiles:")
        for r in results:
            if r.get("found"):
                print(f"    [+] {r['site']}: {r['url']} (HTTP {r['status']})")
        print()

    if not_found_count > 0:
        print("[-] Not found on:")
        for r in results:
            if not r.get("found"):
                status_str = f" (HTTP {r['status']})" if r.get("status") else ""
                print(f"    [-] {r['site']}: {r['url']}{status_str}")
        print()

    # Save reports
    reports_dir = config.get("general", {}).get("reports_dir", "reports")
    json_path = save_json_report(data, reports_dir)
    print(f"[+] JSON report saved to: {json_path}")

    md_path = generate_markdown_report(data, reports_dir)
    print(f"[+] Markdown report saved to: {md_path}")
    print()
    print("[+] Username reconnaissance complete.")

    return data


def display_latest_report(reports_dir: str = "reports") -> None:
    """
    Display the latest saved report in the console.

    Args:
        reports_dir: Directory containing reports (default: 'reports').
    """
    latest_path = get_latest_report_path(reports_dir)

    if not latest_path:
        print("[-] No reports found. Run a reconnaissance first.")
        return

    print(f"[*] Loading latest report: {latest_path}")
    print()

    data = load_latest_report(reports_dir)
    if not data:
        print("[-] Failed to parse report file.")
        return

    # Display based on report type
    if "domain" in data:
        print("## Domain Reconnaissance Report")
        print(f"Domain: {data['domain']}")
        print()
        print(f"IP Addresses: {', '.join(data.get('ip_addresses', [])) or 'None'}")
        print(f"Aliases: {', '.join(data.get('aliases', [])) or 'None'}")
        print(f"MX Records: {', '.join(data.get('mx_records', [])) or 'None'}")
        print(f"NS Records: {', '.join(data.get('ns_records', [])) or 'None'}")
        print(f"CNAME Records: {', '.join(data.get('cname_records', [])) or 'None'}")
        print(f"TXT Records: {', '.join(data.get('txt_records', [])) or 'None'}")
    elif "username" in data or "results" in data:
        username = data.get("username", data.get("query", "N/A"))
        results = data.get("results", data.get("username_checks", []))

        print(f"## Username Availability Report")
        print(f"Username: {username}")
        print()

        if isinstance(results, list):
            found = [r for r in results if r.get("found")]
            not_found = [r for r in results if not r.get("found")]

            if found:
                print("Found on:")
                for r in found:
                    print(f"  [+] {r['site']}: {r['url']}")
            if not_found:
                print("Not found on:")
                for r in not_found:
                    print(f"  [-] {r['site']}: {r['url']}")

    print()
    print(f"[+] Report loaded from: {latest_path}")


def list_plugins() -> None:
    """List all discovered plugins."""
    try:
        from plugins import discover_plugins
        plugins = discover_plugins()
        if not plugins:
            print("No plugins discovered.")
            return

        print(f"Discovered {len(plugins)} plugin(s):")
        for plugin in plugins:
            print(f"  - {plugin.plugin_name} v{plugin.plugin_version}")
            print(f"    {plugin.plugin_description}")
            print(f"    Author: {plugin.plugin_author}")
            print()
    except ImportError:
        print("Plugin system not available.")


def main() -> None:
    """Main entry point for ReconLite CLI."""
    parser = argparse.ArgumentParser(
        prog="reconlite",
        description="ReconLite - Lightweight OSINT reconnaissance tool (stdlib only)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --domain example.com
  python main.py --username targetname
  python main.py --report latest
  python main.py --list-plugins

Configuration:
  Config files are loaded from:
    - %APPDATA%/reconlite/config.yaml (Windows)
    - ~/.config/reconlite/config.yaml (Linux/Mac)
    - ./config/config.yaml (project-local)

  Environment variables can override config:
    RECONLITE_GENERAL_TIMEOUT=30
    RECONLITE_USERNAME_CHECK_MAX_WORKERS=10
        """,
    )

    # Reconnaissance options (mutually exclusive)
    recon_group = parser.add_mutually_exclusive_group(required=True)
    recon_group.add_argument(
        "--domain",
        type=str,
        help="Run domain reconnaissance on the specified domain",
    )
    recon_group.add_argument(
        "--username",
        type=str,
        help="Run username availability check for the specified username",
    )
    recon_group.add_argument(
        "--report",
        type=str,
        metavar="LATEST",
        help="Display the latest saved report (use 'latest')",
    )

    parser.add_argument(
        "--reports-dir",
        type=str,
        default="reports",
        help="Directory to store reports (default: reports)",
    )
    parser.add_argument(
        "--list-plugins",
        action="store_true",
        help="List all discovered plugins",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show program version and exit",
    )

    args = parser.parse_args()

    # Load configuration
    config = get_config()

    try:
        if args.list_plugins:
            list_plugins()
        elif args.domain:
            run_domain_recon(args.domain, config)
        elif args.username:
            run_username_recon(args.username, config)
        elif args.report == "latest":
            display_latest_report(args.reports_dir)
        else:
            parser.print_help()
    except KeyboardInterrupt:
        print("\n[-] Interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[-] Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
