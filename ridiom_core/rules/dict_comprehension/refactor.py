# -*- coding: utf-8 -*-
"""
Dict Comprehension - Refactor transformation (fully self-contained).

Transforms non-idiomatic for-loop + d[k]=v patterns into dict comprehensions.
Core logic copied from RefactoringIdioms/transform_c_s/transform_dict_comp.py
"""

import ast
import copy
from typing import Dict, Any

from ...base_rule import Match


def _copy_compre(node: ast.For) -> ast.comprehension:
    """Create a comprehension from a For node."""
    compr = ast.comprehension()
    compr.target = node.target
    compr.iter = node.iter
    compr.ifs = []
    compr.is_async = getattr(node, "is_async", 0)
    return compr


def _for_transform(node: ast.AST, dictcompre: ast.DictComp) -> None:
    """Recursively transform for/if structure into dict comprehension."""
    if isinstance(node, ast.For):
        body = node.body[0]
        dictcompre.generators.append(_copy_compre(node))
        _for_transform(body, dictcompre)

    elif isinstance(node, ast.If):
        body = node.body[0]
        if not node.orelse:
            dictcompre.generators[-1].ifs.append(node.test)
            _for_transform(body, dictcompre)
        else:

            def if_else_transform(n, dc):
                if isinstance(n, ast.If):
                    ifexpr = ast.IfExp()
                    ifexpr.test = n.test
                    ifexpr.body = n.body[0].value
                    dc.key = n.body[0].targets[0].slice
                    ifexpr.orelse = if_else_transform(n.orelse[0], dc)
                    return ifexpr
                else:
                    return n.value

            dictcompre.value = if_else_transform(node, dictcompre)
    else:
        # ast.Assign with d[k] = v
        dictcompre.key = node.targets[0].slice
        dictcompre.value = node.value


def transform(match: Match, config: Dict[str, Any]) -> str:
    """Transform non-idiomatic for-loop to dict comprehension."""
    context = match.context
    for_node = context["for_node"]
    assign_node = context["assign_node"]
    remove_ass_flag = context["remove_ass_flag"]

    new_code = copy.deepcopy(assign_node)

    dictcompre = ast.DictComp()
    dictcompre.generators = []
    dictcompre.key = None
    dictcompre.value = None
    _for_transform(for_node, dictcompre)
    new_code.value = dictcompre

    if remove_ass_flag:
        return ast.unparse(new_code)
    else:
        return ast.unparse(assign_node) + "\n" + ast.unparse(new_code)
