"""
Base plugin classes for ReconLite.

Defines the plugin interface that all ReconLite plugins must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class ReconLitePlugin(ABC):
    """
    Base class for all ReconLite plugins.

    All plugins must implement:
    - plugin_name: Unique identifier
    - plugin_version: Semantic version string
    - plugin_description: Human-readable description
    - execute(): Main plugin execution method
    """

    @property
    @abstractmethod
    def plugin_name(self) -> str:
        """Unique name for this plugin."""
        pass

    @property
    @abstractmethod
    def plugin_version(self) -> str:
        """Semantic version string (e.g., '1.0.0')."""
        pass

    @property
    def plugin_description(self) -> str:
        """Human-readable description of the plugin."""
        return f"Plugin: {self.plugin_name}"

    @property
    def plugin_author(self) -> str:
        """Author name."""
        return "Unknown"

    def is_enabled(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Check if the plugin should be enabled based on configuration.

        Args:
            config: Plugin configuration dictionary.

        Returns:
            True if the plugin should be active.
        """
        if config is None:
            return True
        return config.get("enabled", True)

    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """
        Execute the plugin's main functionality.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            Plugin result (implementation-specific).
        """
        pass

    def validate_input(self, data: Dict[str, Any]) -> List[str]:
        """
        Validate input data for the plugin.

        Args:
            data: Input data dictionary.

        Returns:
            List of validation error messages (empty if valid).
        """
        return []


class CheckerPlugin(ReconLitePlugin):
    """
    Plugin base class for username/domain checkers.

    Checker plugins perform reconnaissance checks against external
    services and return structured results.
    """

    @property
    def plugin_description(self) -> str:
        return f"Checker plugin: {self.plugin_name}"

    @abstractmethod
    def check(self, target: str, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Check a target against the service this plugin monitors.

        Args:
            target: The username or domain to check.
            **kwargs: Additional options (timeout, headers, etc.).

        Returns:
            List of result dictionaries with keys:
            - site: Service name
            - url: Profile URL
            - status: HTTP status or result code
            - found: Boolean indicating existence
            - timestamp: Unix timestamp
        """
        pass

    def execute(self, target: str, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Execute the checker plugin.

        Args:
            target: The username or domain to check.
            **kwargs: Additional options.

        Returns:
            List of result dictionaries.
        """
        return self.check(target, **kwargs)


class EnricherPlugin(ReconLitePlugin):
    """
    Plugin base class for data enrichment.

    Enricher plugins take existing reconnaissance data and add
    additional information (e.g., geolocation, WHOIS, etc.).
    """

    @property
    def plugin_description(self) -> str:
        return f"Enricher plugin: {self.plugin_name}"

    @abstractmethod
    def enrich(self, data: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """
        Enrich reconnaissance data with additional information.

        Args:
            data: Existing reconnaissance data.
            **kwargs: Additional options.

        Returns:
            Enriched data dictionary.
        """
        pass

    def execute(self, data: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """
        Execute the enricher plugin.

        Args:
            data: Existing reconnaissance data.
            **kwargs: Additional options.

        Returns:
            Enriched data dictionary.
        """
        return self.enrich(data, **kwargs)


class FormatterPlugin(ReconLitePlugin):
    """
    Plugin base class for report formatters.

    Formatter plugins generate reports in custom formats.
    """

    @property
    def plugin_description(self) -> str:
        return f"Formatter plugin: {self.plugin_name}"

    @abstractmethod
    def format(self, data: Dict[str, Any], **kwargs: Any) -> str:
        """
        Format reconnaissance data into a report string.

        Args:
            data: Reconnaissance data to format.
            **kwargs: Additional options (title, author, etc.).

        Returns:
            Formatted report string.
        """
        pass

    def execute(self, data: Dict[str, Any], **kwargs: Any) -> str:
        """
        Execute the formatter plugin.

        Args:
            data: Reconnaissance data to format.
            **kwargs: Additional options.

        Returns:
            Formatted report string.
        """
        return self.format(data, **kwargs)


def discover_plugins(plugins_dir: Optional[str] = None) -> List[ReconLitePlugin]:
    """
    Discover plugins in the specified directory.

    Looks for Python files that define classes inheriting from
    ReconLitePlugin base classes.

    Args:
        plugins_dir: Path to plugins directory. If None, uses default.

    Returns:
        List of discovered plugin instances.
    """
    import importlib.util
    import os

    if plugins_dir is None:
        # Default to plugins directory relative to this file
        plugins_dir = os.path.join(os.path.dirname(__file__))

    plugins: List[ReconLitePlugin] = []
    plugins_path = os.path.expanduser(plugins_dir)

    if not os.path.isdir(plugins_path):
        return plugins

    for filename in os.listdir(plugins_path):
        if filename.endswith(".py") and not filename.startswith("_"):
            filepath = os.path.join(plugins_path, filename)
            try:
                spec = importlib.util.spec_from_file_location(f"plugin_{filename}", filepath)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Find all classes that inherit from ReconLitePlugin
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (
                            isinstance(attr, type)
                            and issubclass(attr, ReconLitePlugin)
                            and attr is not ReconLitePlugin
                            and attr is not CheckerPlugin
                            and attr is not EnricherPlugin
                            and attr is not FormatterPlugin
                        ):
                            try:
                                plugin_instance = attr()
                                plugins.append(plugin_instance)
                            except Exception:
                                pass
            except Exception:
                # Skip plugins that fail to load
                pass

    return plugins
