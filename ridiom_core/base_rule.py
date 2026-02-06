# -*- coding: utf-8 -*-
"""
Base class for all idiom rules.

Supports both legacy single-method rules and new modular rules.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class Match:
    """
    Represents a detected code pattern.

    Attributes:
        node: The AST node or code fragment
        context: Contextual info (class_name, method_name, has_if, etc.)
        old_code: Original code string
        lineno: Line number ranges
    """

    node: Any
    context: Dict[str, Any]
    old_code: str
    lineno: List[List[int]] = field(default_factory=list)


@dataclass
class RuleResult:
    """
    Unified result format for all rules.

    Attributes:
        idiom_name: Human-readable name of the idiom (e.g., "List Comprehension")
        class_name: Name of the class containing the code, or "NULL" if top-level
        method_name: Name of the method/function containing the code
        old_code: Original code snippet
        new_code: Transformed code snippet
        lineno: Line number ranges as [[start, end], ...]
    """

    idiom_name: str
    class_name: str
    method_name: str
    old_code: str
    new_code: str
    lineno: List[List[int]] = field(default_factory=list)


class BaseRule(ABC):
    """
    Abstract base class for all idiom rules.

    Supports two implementation patterns:

    1. Legacy pattern (override match() only):
       - Simple rules that handle everything in match()

    2. Modular pattern (override detect/transform methods):
       - should_transform(): Config-based filtering
       - detect_refactor() / detect_explain(): Mode-specific detection
       - transform_refactor() / transform_explain(): Mode-specific transformation
    """

    # Rule identifier (used in ridiom.toml and for display)
    name: str = ""

    # Mode this rule applies to: "refactor", "explain", or "both"
    mode: str = "both"

    # ==========================================
    # Core Abstract Method (Legacy Pattern)
    # ==========================================

    @abstractmethod
    def match(
        self, content: str, config: Optional[Dict[str, Any]] = None
    ) -> List[RuleResult]:
        """
        Find all matches in the given code content.

        Args:
            content: Source code as a string
            config: Rule-specific configuration from ridiom.toml

        Returns:
            List of RuleResult objects representing detected patterns
        """
        pass

    # ==========================================
    # Modular Pattern Methods (Optional Override)
    # ==========================================

    def should_transform(
        self, context: Dict[str, Any], config: Dict[str, Any], mode: str
    ) -> bool:
        """
        Check if transformation should proceed based on config.

        Override this to implement fine-grained config checking
        (replaces config_checker.py logic).

        Args:
            context: Detection context (has_if, operand_count, etc.)
            config: Rule-specific config from ridiom.toml
            mode: "refactor" or "explain"

        Returns:
            True if transformation should proceed
        """
        return True

    def detect_refactor(self, content: str, config: Dict[str, Any]) -> List[Match]:
        """
        Detect non-idiomatic code patterns for refactoring.

        Override in modular rules.
        """
        return []

    def detect_explain(self, content: str, config: Dict[str, Any]) -> List[Match]:
        """
        Detect idiomatic code patterns for explanation.

        Override in modular rules.
        """
        return []

    def transform_refactor(self, match: Match, config: Dict[str, Any]) -> str:
        """
        Transform non-idiomatic code to idiomatic code.

        Override in modular rules.
        """
        return match.old_code

    def transform_explain(self, match: Match, config: Dict[str, Any]) -> str:
        """
        Transform idiomatic code to non-idiomatic code.

        Override in modular rules.
        """
        return match.old_code

    # ==========================================
    # Utility Methods
    # ==========================================

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name='{self.name}' mode='{self.mode}'>"
