"""
ReconLite plugin system.

Provides extensibility through plugin entry points for:
- reconlite.checkers: Username/availability checkers
- reconlite.enrichers: Data enrichment modules
- reconlite.formatters: Report format generators

Usage:
    Plugins can be discovered automatically from the plugins/ directory
    or registered via entry points in pyproject.toml/setup.py.
"""

from plugins.base import ReconLitePlugin, CheckerPlugin

__all__ = ["ReconLitePlugin", "CheckerPlugin"]
