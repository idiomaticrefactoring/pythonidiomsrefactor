# -*- coding: utf-8 -*-
"""
Global configuration management for Ridiom.
"""

import os
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import toml


@dataclass
class Config:
    """
    Global configuration container.

    This class holds all configuration from ridiom.toml and provides
    convenient accessors for different parts of the config.
    """

    # Global settings
    include: List[str] = field(default_factory=lambda: ["."])
    exclude: List[str] = field(default_factory=list)
    enable_noqa: bool = True

    # Core transformation settings
    mode: str = "refactor"  # "refactor" or "explain"

    # Rules configuration
    select: List[str] = field(default_factory=list)
    ignore: List[str] = field(default_factory=list)
    rules_config: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # Output configuration
    output_file: str = "ridiom-report.json"

    # Raw config dict for advanced access
    _raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    def get_rule_config(self, rule_name: str) -> Dict[str, Any]:
        """Get configuration for a specific rule."""
        return self.rules_config.get(rule_name, {})

    def is_rule_enabled(self, rule_name: str) -> bool:
        """Check if a rule is enabled based on select/ignore lists."""
        if rule_name in self.ignore:
            return False
        if not self.select or "All" in self.select:
            return True
        return rule_name in self.select


def load_config(config_path: str = "ridiom.toml") -> Config:
    """
    Load configuration from a TOML file.

    Args:
        config_path: Path to the ridiom.toml file

    Returns:
        Config object with parsed settings

    Raises:
        RuntimeError: If the config file is malformed
    """
    if not os.path.exists(config_path):
        return Config()

    try:
        raw = toml.load(config_path)
    except Exception as e:
        raise RuntimeError(f"配置文件损坏: {e}") from e

    ridiom_conf = raw.get("ridiom", {})
    rules_conf = ridiom_conf.get("rules", {})
    output_conf = ridiom_conf.get("output", {})

    # Extract rule-specific configs (nested tables like [ridiom.rules.list-comprehension])
    rules_config = {}
    for key, value in rules_conf.items():
        if isinstance(value, dict):
            rules_config[key] = value

    return Config(
        include=ridiom_conf.get("include", ["."]),
        exclude=ridiom_conf.get("exclude", []),
        enable_noqa=ridiom_conf.get("enable-noqa", True),
        mode=ridiom_conf.get("mode", "refactor"),
        select=rules_conf.get("select", []),
        ignore=rules_conf.get("ignore", []),
        rules_config=rules_config,
        output_file=output_conf.get("file", "ridiom-report.json"),
        _raw=raw,
    )


# Global config instance (lazily initialized)
_global_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global config instance."""
    global _global_config
    if _global_config is None:
        _global_config = load_config()
    return _global_config


def set_config(config: Config) -> None:
    """Set the global config instance."""
    global _global_config
    _global_config = config
