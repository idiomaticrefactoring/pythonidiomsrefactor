# -*- coding: utf-8 -*-
"""
Truth Value Test - Detection logic (fully self-contained).

Detects redundant boolean comparisons like:
  - if x == True  → if x
  - if x != []    → if x
  - if x == 0     → if not x

Core logic copied from RefactoringIdioms/extract_complicate_code/extract_truth_value.py
"""

import ast
from typing import List, Dict, Any, Tuple

from ...base_rule import Match
from ...ast_helpers import FunAnalyzer


# Empty/False values that indicate redundant comparisons
EMPTY_SET = [
    "None",
    "True",
    "False",
    "0",
    "0.0",
    "0j",
    "Decimal(0)",
    "Fraction(0, 1)",
    "''",
    '""',
    "()",
    "[]",
    "{}",
    "dict()",
    "set()",
    "range(0)",
]


def _decide_compare_complicate_truth_value(test: ast.Compare) -> bool:
    """Check if comparison is a redundant truth value test."""
    if not test.comparators:
        return False

    ops = test.ops
    left_str = ast.unparse(test.left)
    comp_str = ast.unparse(test.comparators[0])

    # Only Eq (==) and NotEq (!=) are considered redundant
    if len(ops) == 1 and isinstance(ops[0], (ast.Eq, ast.NotEq)):
        if left_str in EMPTY_SET or comp_str in EMPTY_SET:
            return True

    return False


def _get_truth_value_tests(tree: ast.AST) -> List[Tuple[ast.Compare, ast.AST]]:
    """Find all redundant truth value tests in the AST."""
    code_list = []

    for node in ast.walk(tree):
        # Check control flow statements
        if isinstance(node, (ast.If, ast.While, ast.Assert)):
            test = node.test
            if isinstance(test, ast.Compare):
                if _decide_compare_complicate_truth_value(test):
                    code_list.append(test)

        # Check values in BoolOp (and/or)
        elif isinstance(node, ast.BoolOp):
            for value in node.values:
                if isinstance(value, ast.Compare):
                    if _decide_compare_complicate_truth_value(value):
                        code_list.append(value)

    return code_list


def detect_refactor(content: str, config: Dict[str, Any]) -> List[Match]:
    """Detect redundant truth value tests (non-idiomatic)."""
    matches = []

    try:
        file_tree = ast.parse(content)
        analyzer = FunAnalyzer()
        analyzer.visit(file_tree)

        search_targets = (
            analyzer.func_def_list
            if analyzer.func_def_list
            else [(file_tree, "Module")]
        )

        for tree, class_name in search_targets:
            method_name = getattr(tree, "name", "")
            if isinstance(tree, ast.Module):
                method_name = "Global"

            test_nodes = _get_truth_value_tests(tree)

            for old_node in test_nodes:
                context = {
                    "class_name": class_name if class_name != "Module" else "NULL",
                    "method_name": method_name,
                    "compare_node": old_node,
                }

                lineno = (
                    [[old_node.lineno, old_node.end_lineno]]
                    if hasattr(old_node, "lineno")
                    else []
                )

                matches.append(
                    Match(
                        node=old_node,
                        context=context,
                        old_code=ast.unparse(old_node),
                        lineno=lineno,
                    )
                )

        return matches

    except Exception:
        import traceback

        traceback.print_exc()
        return []


def detect_explain(content: str, config: Dict[str, Any]) -> List[Match]:
    """Detect idiomatic truth value tests (simplified boolean conditions)."""
    # For explain mode, we'd look for direct boolean tests
    # This is more complex and less commonly needed
    return []
