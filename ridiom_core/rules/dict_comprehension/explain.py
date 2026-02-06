# -*- coding: utf-8 -*-
"""
Dict Comprehension - Explain transformation (fully self-contained).

Transforms idiomatic dict comprehensions back into for-loop + d[k]=v patterns.
Core logic copied from DeIdiom/transform_s_c/transform_dict_compre_s_c.py
"""

import ast
import copy
from typing import Dict, Any, List, Set

from ...base_rule import Match


def _get_for_str(tmp_var: str, node: ast.DictComp, space: str = "") -> str:
    """Generate for-loop string from dict comprehension."""
    code_str = ""
    generators = node.generators

    for gen in generators:
        for_str = f"{space}for {ast.unparse(gen.target)} in {ast.unparse(gen.iter)}:\n"
        code_str += for_str
        for if_node in gen.ifs:
            space += "    "
            code_str += f"{space}if {ast.unparse(if_node)}:\n"
        space += "    "

    key = ast.unparse(node.key)
    value = ast.unparse(node.value)
    code_str += f"{space}{tmp_var}[{key}] = {value}\n"
    return code_str


def _visit_large_vars(
    target: ast.AST, var_list: List[ast.AST], filter_str: str = ""
) -> None:
    if ast.unparse(target) != filter_str:
        if isinstance(target, (ast.Name, ast.arg)):
            var_list.append(target)
        else:
            for e in ast.iter_child_nodes(target):
                _visit_large_vars(e, var_list, filter_str)


def _visit_filter_vars(target: ast.AST, var_list: List[ast.AST]) -> None:
    for e in ast.walk(target):
        for attr_str in ["target", "targets"]:
            if hasattr(e, attr_str):
                for var in ast.walk(getattr(e, attr_str)):
                    if isinstance(var, (ast.Name, ast.arg)):
                        var_list.append(var)


def _is_use_var_in_P_child(P: ast.AST, child: ast.AST) -> Set[str]:
    child_tokens = []
    _visit_large_vars(child, child_tokens)
    child_tokens_set = {ast.unparse(e) for e in child_tokens}

    child_filter_vars = []
    _visit_filter_vars(child, child_filter_vars)
    child_filter_vars_set = {ast.unparse(e) for e in child_filter_vars}

    child_tokens_set = child_tokens_set - child_filter_vars_set

    if isinstance(P, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
        P = P.value

    other_tokens = []
    _visit_large_vars(P, other_tokens, filter_str=ast.unparse(child))
    other_tokens_set = {ast.unparse(e) for e in other_tokens}

    return other_tokens_set & child_tokens_set


def _is_intersect_var(targets: List[ast.AST], comprehension: ast.AST) -> Set[str]:
    tar_vars = {ast.unparse(e) for e in ast.walk(targets[0]) if isinstance(e, ast.Name)}
    comp_vars = {
        ast.unparse(e) for e in ast.walk(comprehension) if isinstance(e, ast.Name)
    }
    return tar_vars & comp_vars


def _has_many_value(targets: List[ast.AST]) -> bool:
    if len(targets) > 1:
        return True
    return any(isinstance(e, (ast.Tuple, ast.List)) for e in targets)


class _RewriteCompre(ast.NodeTransformer):
    """Replace dict comprehension with variable reference."""

    def __init__(self, old_node: ast.AST, new_node: ast.AST):
        self.old_node = old_node
        self.new_node = new_node

    def visit_DictComp(self, node: ast.DictComp) -> ast.AST:
        if ast.unparse(node) == ast.unparse(self.old_node):
            return self.new_node
        return self.generic_visit(node)


def transform(match: Match, config: Dict[str, Any]) -> str:
    """Transform dict comprehension to non-idiomatic for-loop."""
    context = match.context
    parent_node = context["assign_node"]
    node = context["dict_comp_node"]

    tmp_var = "tmp_DictComp0"
    replace_flag = False
    create_fun_flag = False

    intersect_vars = list(_is_use_var_in_P_child(parent_node, node))

    if intersect_vars:
        replace_flag = True
        create_fun_flag = True
    elif isinstance(parent_node, ast.Assign) and isinstance(
        parent_node.value, ast.DictComp
    ):
        targets = parent_node.targets
        if _has_many_value(targets) or _is_intersect_var(targets, node):
            replace_flag = True
        else:
            tmp_var = ast.unparse(targets[0])
    else:
        replace_flag = True

    ass_str = f"{tmp_var} = dict()\n"
    code_for = _get_for_str(tmp_var, node, space="")

    if create_fun_flag:
        args_str = ", ".join(intersect_vars)
        code_for_indent = "".join(
            ["    " + e + "\n" for e in code_for.split("\n") if e.strip()]
        )
        func_code = f"def my_comprehension_func({args_str}):\n    {ass_str}{code_for_indent}    return {tmp_var}\n"
        replace_code = f"my_comprehension_func({args_str})"

        new_parent = _RewriteCompre(node, ast.parse(replace_code).body[0].value).visit(
            copy.deepcopy(parent_node)
        )
        return func_code + ast.unparse(new_parent)

    elif replace_flag:
        replace_node = ast.parse(tmp_var).body[0].value
        new_parent = _RewriteCompre(node, replace_node).visit(
            copy.deepcopy(parent_node)
        )
        return ass_str + code_for + ast.unparse(new_parent)

    else:
        return ass_str + code_for
