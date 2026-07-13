"""
Domain reconnaissance module for ReconLite.

Performs DNS resolution and record lookups using Python's standard library
socket module. Optionally supports dnspython for accurate record extraction.
Supports A, AAAA, MX, NS, CNAME, TXT, and SOA record resolution.
"""

import socket
import time
from typing import Dict, List, Optional

# Optional dnspython support for accurate DNS resolution
try:
    import dns.resolver
    import dns.name
    import dns.rdatatype
    import dns.exception
    HAS_DNSPYTHON = True
except ImportError:
    dns = None  # type: ignore
    HAS_DNSPYTHON = False


def resolve_domain(domain: str) -> dict:
    """
    Resolve domain information including IP addresses and DNS records.

    Uses socket.getaddrinfo() for basic resolution and socket.gethostbyname_ex()
    for alias/record extraction. Attempts to gather MX, NS, CNAME, and TXT records.
    If dnspython is available, uses it for accurate record extraction.

    Args:
        domain: The domain name to resolve (e.g., 'example.com').

    Returns:
        A dictionary containing:
        - domain: The queried domain
        - ip_addresses: List of IPv4 and IPv6 addresses found
        - aliases: Hostname aliases from gethostbyname_ex
        - mx_records: List of MX (mail exchange) records
        - ns_records: List of NS (name server) records
        - cname_records: List of CNAME (canonical name) records
        - txt_records: List of TXT records
        - soa_records: List of SOA (start of authority) records
        - timestamp: Unix timestamp of when the lookup was performed
    """
    result: Dict[str, object] = {
        "domain": domain,
        "ip_addresses": [],
        "aliases": [],
        "mx_records": [],
        "ns_records": [],
        "cname_records": [],
        "txt_records": [],
        "soa_records": [],
        "timestamp": int(time.time()),
    }

    # Use dnspython if available for accurate resolution
    if HAS_DNSPYTHON:
        _resolve_with_dnspython(domain, result)
    else:
        # Fall back to socket-based heuristic resolution
        _resolve_with_socket(domain, result)

    return result


def _resolve_with_socket(domain: str, result: Dict[str, object]) -> None:
    """
    Resolve domain using Python's standard library socket module.

    Uses heuristic-based approaches for MX, NS, TXT record discovery.

    Args:
        domain: The domain name to resolve.
        result: Dictionary to populate with resolution results.
    """
    # --- A and AAAA record resolution via getaddrinfo ---
    try:
        addr_info = socket.getaddrinfo(domain, None)
        seen_ips: set = set()
        for info in addr_info:
            ip = info[4][0]
            canonname = info[3]
            if ip and ip not in seen_ips:
                seen_ips.add(ip)
                result["ip_addresses"].append(ip)
            if canonname:
                result["cname_records"].append(canonname)
    except socket.gaierror:
        pass
    except OSError:
        pass

    # --- Extract aliases via gethostbyname_ex ---
    try:
        hostname, aliases, ips = socket.gethostbyname_ex(domain)
        result["aliases"] = aliases if aliases else []
        for ip in ips:
            if ip not in result["ip_addresses"]:
                result["ip_addresses"].append(ip)
    except socket.gaierror:
        pass
    except OSError:
        pass

    # --- Attempt MX record resolution ---
    try:
        mx_found = _try_mx_lookup(domain)
        if mx_found:
            result["mx_records"] = mx_found
    except Exception:
        pass

    # --- Attempt NS record resolution ---
    try:
        ns_found = _try_ns_lookup(domain)
        if ns_found:
            result["ns_records"] = ns_found
    except Exception:
        pass

    # --- Attempt TXT record resolution ---
    try:
        txt_found = _try_txt_lookup(domain)
        if txt_found:
            result["txt_records"] = txt_found
    except Exception:
        pass

    # Deduplicate CNAME records
    if result["cname_records"]:
        result["cname_records"] = list(dict.fromkeys(result["cname_records"]))


def _resolve_with_dnspython(domain: str, result: Dict[str, object]) -> None:
    """
    Resolve domain using dnspython library for accurate record extraction.

    Args:
        domain: The domain name to resolve.
        result: Dictionary to populate with resolution results.
    """
    # --- A and AAAA record resolution ---
    try:
        for rdatatype_str, rdatatype in [("A", dns.rdatatype.A), ("AAAA", dns.rdatatype.AAAA)]:
            try:
                answers = dns.resolver.resolve(domain, rdatatype)
                for ans in answers:
                    ip = str(ans)
                    if rdatatype_str == "A" and ip not in result["ip_addresses"]:
                        result["ip_addresses"].append(ip)
                    elif rdatatype_str == "AAAA":
                        if ip not in result["ip_addresses"]:
                            result["ip_addresses"].append(ip)
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
                pass
    except Exception:
        pass

    # --- CNAME resolution ---
    try:
        answers = dns.resolver.resolve(domain, dns.rdatatype.CNAME)
        for ans in answers:
            cname = str(ans.target).rstrip('.')
            if cname and cname not in result["cname_records"]:
                result["cname_records"].append(cname)
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
        pass

    # --- MX record resolution ---
    try:
        answers = dns.resolver.resolve(domain, dns.rdatatype.MX)
        mx_entries = []
        for ans in answers:
            priority = ans.preference
            exchange = str(ans.exchange).rstrip('.')
            mx_entries.append(f"{priority} {exchange}")
        result["mx_records"] = mx_entries
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
        pass

    # --- NS record resolution ---
    try:
        answers = dns.resolver.resolve(domain, dns.rdatatype.NS)
        ns_entries = []
        for ans in answers:
            ns_server = str(ans.target).rstrip('.')
            if ns_server:
                ns_entries.append(ns_server)
        result["ns_records"] = ns_entries
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
        pass

    # --- TXT record resolution ---
    try:
        answers = dns.resolver.resolve(domain, dns.rdatatype.TXT)
        txt_entries = []
        for ans in answers:
            for txt_data in ans.strings:
                try:
                    txt_str = txt_data.decode('utf-8')
                    if txt_str:
                        txt_entries.append(txt_str)
                except (UnicodeDecodeError, AttributeError):
                    pass
        result["txt_records"] = txt_entries
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
        pass

    # --- SOA record resolution ---
    try:
        answers = dns.resolver.resolve(domain, dns.rdatatype.SOA)
        soa_entries = []
        for ans in answers:
            soa_str = (
                f"mname={str(ans.mname).rstrip('.')}, "
                f"rname={str(ans.rname).rstrip('.')}, "
                f"serial={ans.serial}, "
                f"refresh={ans.refresh}, "
                f"retry={ans.retry}, "
                f"expire={ans.expire}, "
                f"minimum={ans.minimum}"
            )
            soa_entries.append(soa_str)
        result["soa_records"] = soa_entries
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
        pass

    # --- Extract aliases from CNAME chain ---
    if result["cname_records"]:
        result["aliases"] = list(result["cname_records"])


def _try_mx_lookup(domain: str) -> List[str]:
    """
    Attempt to find MX records by querying common mail server patterns.

    Tries to resolve mail.{domain}, mx1.{domain}, mx2.{domain}, etc.
    Returns list of successfully resolved mail server hostnames.

    Args:
        domain: The domain name to check.

    Returns:
        List of MX server hostnames found.
    """
    mx_candidates = [
        f"mail.{domain}",
        f"mx1.{domain}",
        f"mx2.{domain}",
        f"smtp.{domain}",
    ]
    mx_found: List[str] = []
    for candidate in mx_candidates:
        try:
            socket.gethostbyname(candidate)
            mx_found.append(candidate)
        except socket.gaierror:
            continue
    return mx_found


def _try_ns_lookup(domain: str) -> List[str]:
    """
    Attempt to find NS records by resolving common name server patterns.

    Tries ns1.{domain}, ns2.{domain}, dns1.{domain}, etc.

    Args:
        domain: The domain name to check.

    Returns:
        List of NS server hostnames found.
    """
    ns_candidates = [
        f"ns1.{domain}",
        f"ns2.{domain}",
        f"dns1.{domain}",
        f"dns2.{domain}",
    ]
    ns_found: List[str] = []
    for candidate in ns_candidates:
        try:
            socket.gethostbyname(candidate)
            ns_found.append(candidate)
        except socket.gaierror:
            continue
    return ns_found


def _try_txt_lookup(domain: str) -> List[str]:
    """
    Attempt to find TXT records.

    Uses getaddrinfo with a special query to try extracting TXT-like information.
    Falls back to checking common TXT record patterns like SPF, DKIM, etc.

    Args:
        domain: The domain name to check.

    Returns:
        List of TXT record strings found.
    """
    txt_found: List[str] = []

    # Try to get additional info via getnameinfo (may return some text info)
    try:
        addr_info = socket.getaddrinfo(domain, None)
        for info in addr_info:
            canonname = info[3]
            if canonname and canonname != domain:
                txt_found.append(f"canonical: {canonname}")
    except Exception:
        pass

    # Try common TXT record hostnames (SPF, DKIM, etc.)
    txt_candidates = [
        f"_spf.{domain}",
        f"default._domainkey.{domain}",
    ]
    for candidate in txt_candidates:
        try:
            socket.gethostbyname(candidate)
            txt_found.append(f"record exists: {candidate}")
        except socket.gaierror:
            continue

    return txt_found
