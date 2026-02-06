# -*- coding: utf-8 -*-
"""
Truth Value Test - Refactor transformation (fully self-contained).

Transforms redundant truth comparisons into simpler forms.
Core logic copied from RefactoringIdioms/transform_c_s/transform_truth_value.py
"""

import ast
from typing import Dict, Any

from ...base_rule import Match


EMPTY_SET = [
    "None",
    "False",
    "0",
    "0.0",
    "0j",
    "Decimal(0)",
    "Fraction(0, 1)",
    "",
    "()",
    "[]",
    "{}",
    "dict()",
    "set()",
    "range(0)",
]
TRUE_SET = ["True"]


def _convert_func_var(node: ast.AST) -> ast.AST:
    """Unwrap bool() calls."""
    if isinstance(node, ast.Call):
        func_name = ast.unparse(node.func)
        if func_name == "bool" and node.args:
            return ast.Name(id=ast.unparse(node.args[0]), ctx=ast.Load())
    return node


def _transform_truth_value_test(node: ast.Compare) -> ast.AST:
    """Transform a redundant comparison into simpler form."""
    op = node.ops[0]
    left = node.left
    comparator = node.comparators[0]

    # Handle bool() wrapping
    if isinstance(left, ast.Call):
        left_node = _convert_func_var(left)
        comparator_node = comparator
    elif isinstance(comparator, ast.Call):
        left_node = left
        comparator_node = _convert_func_var(comparator)
    else:
        left_node = left
        comparator_node = comparator

    left_str = ast.unparse(left_node)
    comparator_str = ast.unparse(comparator_node)

    comp_code_node = None

    if left_str in EMPTY_SET:
        if isinstance(op, (ast.Eq, ast.Is)):
            # x == [] → not x
            comp_code_node = ast.UnaryOp(op=ast.Not(), operand=comparator_node)
        else:
            # x != [] → x
            comp_code_node = comparator_node
    elif comparator_str in EMPTY_SET:
        if isinstance(op, (ast.Eq, ast.Is)):
            # x == [] → not x
            comp_code_node = ast.UnaryOp(op=ast.Not(), operand=left_node)
        else:
            # x != [] → x
            comp_code_node = left_node
    elif left_str in TRUE_SET:
        if isinstance(op, (ast.Eq, ast.Is)):
            # True == x → x
            comp_code_node = comparator_node
        else:
            # True != x → not x
            comp_code_node = ast.UnaryOp(op=ast.Not(), operand=comparator_node)
    elif comparator_str in TRUE_SET:
        if isinstance(op, (ast.Eq, ast.Is)):
            # x == True → x
            comp_code_node = left_node
        else:
            # x != True → not x
            comp_code_node = ast.UnaryOp(op=ast.Not(), operand=left_node)

    return comp_code_node or node


def transform(match: Match, config: Dict[str, Any]) -> str:
    """Transform redundant truth value test to simpler form."""
    compare_node = match.context["compare_node"]
    new_node = _transform_truth_value_test(compare_node)
    return ast.unparse(new_node)
