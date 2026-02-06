# -*- coding: utf-8 -*-
"""
List Comprehension Rule - Main rule class using modular pattern.

Supports both 'refactor' (for-loop → comprehension) and
'explain' (comprehension → for-loop) modes.
"""

from typing import List, Dict, Any, Optional

from ...base_rule import BaseRule, RuleResult, Match
from ...registry import RuleRegistry
from . import extractor
from . import refactor
from . import explain
from . import should_transform


@RuleRegistry.register
class ListComprehensionRule(BaseRule):
    """
    List Comprehension idiom detection and transformation.

    Uses the new modular pattern with separate extractor/transformer modules.
    """

    name = "list-comprehension"
    mode = "both"

    def should_transform(
        self, context: Dict[str, Any], config: Dict[str, Any], mode: str
    ) -> bool:
        """
        Check if transformation should proceed based on config.
        """
        return should_transform.check(context, config)

    def detect_refactor(self, content: str, config: Dict[str, Any]) -> List[Match]:
        """Detect non-idiomatic for-loop patterns."""
        return extractor.detect_refactor(content, config)

    def detect_explain(self, content: str, config: Dict[str, Any]) -> List[Match]:
        """Detect idiomatic list comprehension patterns."""
        return extractor.detect_explain(content, config)

    def transform_refactor(self, match: Match, config: Dict[str, Any]) -> str:
        """Transform for-loop to list comprehension."""
        return refactor.transform(match, config)

    def transform_explain(self, match: Match, config: Dict[str, Any]) -> str:
        """Transform list comprehension to for-loop."""
        return explain.transform(match, config)

    def match(
        self, content: str, config: Optional[Dict[str, Any]] = None
    ) -> List[RuleResult]:
        """
        Main entry point - find all matches and transform them.

        Uses the modular pattern: detect → filter → transform.
        """
        if config is None:
            config = {}

        current_mode = config.get("_mode", "refactor")
        results = []

        # Select detection method based on mode
        if current_mode == "explain":
            matches = self.detect_explain(content, config)
        else:
            matches = self.detect_refactor(content, config)

        # Process each match
        for m in matches:
            # Apply config-based filtering
            if not self.should_transform(m.context, config, current_mode):
                continue

            # Apply transformation
            if current_mode == "explain":
                new_code = self.transform_explain(m, config)
            else:
                new_code = self.transform_refactor(m, config)

            # Build result
            results.append(
                RuleResult(
                    idiom_name=self.name,
                    class_name=m.context.get("class_name", "NULL"),
                    method_name=m.context.get("method_name", "Global"),
                    old_code=m.old_code,
                    new_code=new_code,
                    lineno=m.lineno,
                )
            )

        return results
