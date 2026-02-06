# -*- coding: utf-8 -*-
"""Star in Func Call Rule - Main rule class."""

from typing import List, Dict, Any, Optional
from ...base_rule import BaseRule, RuleResult, Match
from ...registry import RuleRegistry
from . import extractor, refactor, explain, should_transform


@RuleRegistry.register
class StarInFuncCallRule(BaseRule):
    name = "star-in-func-call"
    mode = "both"

    def should_transform(
        self, context: Dict[str, Any], config: Dict[str, Any], mode: str
    ) -> bool:
        return should_transform.check(context, config)

    def detect_refactor(self, content: str, config: Dict[str, Any]) -> List[Match]:
        return extractor.detect_refactor(content, config)

    def detect_explain(self, content: str, config: Dict[str, Any]) -> List[Match]:
        return extractor.detect_explain(content, config)

    def transform_refactor(self, match: Match, config: Dict[str, Any]) -> str:
        return refactor.transform(match, config)

    def transform_explain(self, match: Match, config: Dict[str, Any]) -> str:
        return explain.transform(match, config)

    def match(
        self, content: str, config: Optional[Dict[str, Any]] = None
    ) -> List[RuleResult]:
        if config is None:
            config = {}
        current_mode = config.get("_mode", "refactor")
        matches = (
            self.detect_explain(content, config)
            if current_mode == "explain"
            else self.detect_refactor(content, config)
        )
        results = []
        for m in matches:
            if not self.should_transform(m.context, config, current_mode):
                continue
            new_code = (
                self.transform_explain(m, config)
                if current_mode == "explain"
                else self.transform_refactor(m, config)
            )
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
