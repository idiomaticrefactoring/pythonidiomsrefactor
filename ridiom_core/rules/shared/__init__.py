# -*- coding: utf-8 -*-
"""
Shared AST utilities for all rules.

This module consolidates common AST traversal and analysis functions
used across multiple rules, eliminating dependency on RefactoringIdioms/util.py.
"""

import ast
from typing import List, Set, Optional, Tuple, Any
from io import BytesIO
import tokenize as tokenize_module


def safe_unparse(node: ast.AST) -> str:
    """Safely unparse AST node to string."""
    try:
        return ast.unparse(node)
    except Exception:
        return ""


def visit_single_vars(target: ast.AST, var_list: List[str]) -> None:
    """Extract variable names from AST node."""
    if isinstance(target, ast.Name):
        var_list.append(safe_unparse(target))
    elif isinstance(target, ast.Subscript):
        var_list.append(safe_unparse(target))
        visit_single_vars(target.value, var_list)
    elif isinstance(target, ast.Attribute):
        var_list.append(safe_unparse(target))
        visit_single_vars(target.value, var_list)


def get_time_var(vars_set: Set[str]) -> List[str]:
    """Get variable and all its reference forms."""
    all_var_list = []
    try:
        var_name = list(vars_set)[0]
        for e_var in ast.walk(ast.parse(var_name)):
            if safe_unparse(e_var) == var_name and isinstance(
                e_var, (ast.Subscript, ast.Attribute, ast.Name)
            ):
                visit_single_vars(e_var, all_var_list)
                break
    except Exception:
        pass

    if not all_var_list and vars_set:
        all_var_list.append(list(vars_set)[0])
    return all_var_list


def tokenize_content(content: str) -> List[Tuple[int, str, Any, Any, Any]]:
    """Tokenize string content."""
    try:
        g = tokenize_module.tokenize(BytesIO(content.encode("utf-8")).readline)
        return list(g)
    except Exception:
        return []


def whether_contain_var(
    node: ast.AST, vars_set: Set[str], time_var_list: List[str]
) -> int:
    """Count occurrences of variables in node."""
    count = 0
    s = safe_unparse(node)
    if not s:
        return 0
    if s != list(vars_set)[0]:
        for tok in tokenize_content(s):
            if len(tok) >= 2 and tok[1] in time_var_list:
                count += 1
    return count


def is_use_var(node: ast.AST, vars_set: Set[str]) -> int:
    """Check if node uses variable from vars_set."""
    s = safe_unparse(node)
    if not s:
        return 0
    if s != list(vars_set)[0]:
        for tok in tokenize_content(s):
            if len(tok) >= 2 and tok[1].strip() == list(vars_set)[0]:
                return 1
    return 0


def visit_vars(target: ast.AST, var_list: List[ast.AST], filter_str: str = "") -> None:
    """Recursively extract variable nodes."""
    if safe_unparse(target) != filter_str:
        if isinstance(target, (ast.Name, ast.Subscript, ast.Attribute, ast.arg)):
            var_list.append(target)
            for e in ast.iter_child_nodes(target):
                visit_vars(e, var_list, filter_str)
        elif isinstance(target, ast.Call):
            if isinstance(target.func, ast.Attribute):
                visit_vars(target.func.value, var_list, filter_str)
                for e in target.args:
                    visit_vars(e, var_list, filter_str)
            else:
                for e in target.args:
                    visit_vars(e, var_list, filter_str)
        else:
            for e in ast.iter_child_nodes(target):
                visit_vars(e, var_list, filter_str)


def visit_large_vars(
    target: ast.AST, var_list: List[ast.AST], filter_str: str = ""
) -> None:
    """Extract Name/arg nodes recursively."""
    if safe_unparse(target) != filter_str:
        if isinstance(target, (ast.Name, ast.arg)):
            var_list.append(target)
        else:
            for e in ast.iter_child_nodes(target):
                visit_large_vars(e, var_list, filter_str)


def visit_filter_vars(
    target: ast.AST, var_list: List[ast.AST], filter_node_attr: str = "iter"
) -> None:
    """Extract variables filtering by attribute."""
    if isinstance(target, (ast.Name, ast.arg)):
        var_list.append(target)
    else:
        for e in ast.iter_child_nodes(target):
            if (
                hasattr(target, filter_node_attr)
                and hasattr(e, filter_node_attr)
                and e == getattr(target, filter_node_attr)
            ):
                visit_filter_vars(e, var_list, filter_node_attr)
