# -*- coding: utf-8 -*-
"""
Set Comprehension - Refactor transformation (fully self-contained).

Transforms non-idiomatic for-loop + add patterns into set comprehensions.
Core logic copied from RefactoringIdioms/transform_c_s/transform_set_comp.py
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


def _for_transform(node: ast.AST, setcompre: ast.SetComp) -> None:
    """Recursively transform for/if structure into set comprehension."""
    if isinstance(node, ast.For):
        body = node.body[0]
        setcompre.generators.append(_copy_compre(node))
        _for_transform(body, setcompre)

    elif isinstance(node, ast.If):
        body = node.body[0]
        if not node.orelse:
            setcompre.generators[-1].ifs.append(node.test)
            _for_transform(body, setcompre)
        else:

            def if_else_transform(n):
                if isinstance(n, ast.If):
                    ifexpr = ast.IfExp()
                    ifexpr.test = n.test
                    ifexpr.body = n.body[0].value.args[0]
                    ifexpr.orelse = if_else_transform(n.orelse[0])
                    return ifexpr
                else:
                    return n.value.args[0]

            setcompre.elt = if_else_transform(node)
    else:
        # ast.Expr with s.add(x)
        setcompre.elt = node.value.args[0]


def transform(match: Match, config: Dict[str, Any]) -> str:
    """Transform non-idiomatic for-loop to set comprehension."""
    context = match.context
    for_node = context["for_node"]
    assign_node = context["assign_node"]
    remove_ass_flag = context["remove_ass_flag"]

    new_code = copy.deepcopy(assign_node)

    setcompre = ast.SetComp()
    setcompre.generators = []
    setcompre.elt = None
    _for_transform(for_node, setcompre)
    new_code.value = setcompre

    if remove_ass_flag:
        return ast.unparse(new_code)
    else:
        return ast.unparse(assign_node) + "\n" + ast.unparse(new_code)
