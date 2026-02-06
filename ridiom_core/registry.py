# -*- coding: utf-8 -*-
"""
Rule registry for automatic rule discovery and management.
"""

from typing import Dict, List, Type, Optional
from .base_rule import BaseRule


class RuleRegistry:
    """
    Central registry for all idiom rules.

    Rules register themselves using the @RuleRegistry.register decorator.
    The main application can then query rules by name or mode.
    """

    _rules: Dict[str, Type[BaseRule]] = {}

    @classmethod
    def register(cls, rule_class: Type[BaseRule]) -> Type[BaseRule]:
        """
        Decorator to register a rule class.

        Usage:
            @RuleRegistry.register
            class MyRule(BaseRule):
                name = "my-rule"
                ...
        """
        if not rule_class.name:
            raise ValueError(
                f"Rule class {rule_class.__name__} must define a 'name' attribute"
            )

        cls._rules[rule_class.name] = rule_class
        return rule_class

    @classmethod
    def get(cls, name: str) -> Optional[Type[BaseRule]]:
        """Get a rule class by its name."""
        return cls._rules.get(name)

    @classmethod
    def get_instance(cls, name: str) -> Optional[BaseRule]:
        """Get an instantiated rule by its name."""
        rule_class = cls.get(name)
        return rule_class() if rule_class else None

    @classmethod
    def all(cls, mode: Optional[str] = None) -> List[Type[BaseRule]]:
        """
        Get all registered rule classes.

        Args:
            mode: Optional filter by mode ("refactor", "explain", or None for all)

        Returns:
            List of rule classes matching the criteria
        """
        if mode:
            return [r for r in cls._rules.values() if r.mode in (mode, "both")]
        return list(cls._rules.values())

    @classmethod
    def all_instances(cls, mode: Optional[str] = None) -> List[BaseRule]:
        """Get instantiated rule objects, optionally filtered by mode."""
        return [r() for r in cls.all(mode)]

    @classmethod
    def names(cls) -> List[str]:
        """Get all registered rule names."""
        return list(cls._rules.keys())

    @classmethod
    def clear(cls) -> None:
        """Clear all registered rules (useful for testing)."""
        cls._rules.clear()
