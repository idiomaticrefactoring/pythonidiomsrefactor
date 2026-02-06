# -*- coding: utf-8 -*-
"""
Chain Comparison - Explain transformation (fully self-contained).

Core logic copied from DeIdiom/transform_s_c/transform_chain_compare_s_c.py
"""

import ast
import copy
from typing import Dict, Any

from ...base_rule import Match


# ==========================================
# 核心转换逻辑 (从 transform_chain_compare_s_c.py 复制)
# ==========================================


def get_op_str(node):
    if isinstance(node, (ast.Eq)):
        return "=="
    elif isinstance(node, (ast.NotEq)):
        return "!="
    elif isinstance(node, (ast.Lt)):
        return "<"
    elif isinstance(node, (ast.LtE)):
        return "<="
    elif isinstance(node, (ast.Gt)):
        return ">"
    elif isinstance(node, (ast.GtE)):
        return ">="
    elif isinstance(node, (ast.Is)):
        return "is"
    elif isinstance(node, (ast.IsNot)):
        return "is not"
    elif isinstance(node, (ast.In)):
        return "in"
    elif isinstance(node, (ast.NotIn)):
        return "not in"


def transform_idiom_chain_compare(node):
    """
    Transform chained comparison (e.g., a < b < c) into split comparisons (e.g., a < b and b < c).

    Args:
        node (ast.AST): The AST node to transform.

    Returns:
        tuple: (bool, ast.AST)
            - bool: True if transformed, False otherwise.
            - ast.AST: The transformed node (ast.BoolOp) or the original node.
    """
    if not isinstance(node, ast.Compare):
        return False, node

    ops = node.ops
    if len(ops) < 2:
        return False, node

    # Construct the split comparisons: a < b and b < c ...
    # Original: left, [op1, op2], [comp1, comp2]
    # Split: (left op1 comp1) AND (comp1 op2 comp2) ...

    comparators = [node.left] + node.comparators
    msg = []

    for i in range(len(ops)):
        left_val = comparators[i]
        right_val = comparators[i + 1]
        op = ops[i]

        new_compare = ast.Compare(
            left=copy.deepcopy(left_val),
            ops=[copy.deepcopy(op)],
            comparators=[copy.deepcopy(right_val)],
        )
        msg.append(new_compare)

    # Create And node
    new_bool_op = ast.BoolOp(op=ast.And(), values=msg)

    return True, new_bool_op


# ==========================================
# 适配 ridiom_core 接口
# ==========================================


def transform(match: Match, config: Dict[str, Any]) -> str:
    """Transform chained comparison to separate comparisons."""
    context = match.context
    compare_node = context.get("compare_node")

    if not compare_node:
        return match.old_code

    success, new_node = transform_idiom_chain_compare(compare_node)
    if success:
        return ast.unparse(new_node)
    else:
        return match.old_code
