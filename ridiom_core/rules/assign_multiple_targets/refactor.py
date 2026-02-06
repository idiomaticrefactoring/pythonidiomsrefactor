# -*- coding: utf-8 -*-
"""
Assign Multiple Targets - Refactor transformation (fully self-contained).

Core logic copied from RefactoringIdioms/transform_c_s/transform_multiple_assign.py
"""

import ast
import copy
from typing import Dict, Any

from ...base_rule import Match


# ==========================================
# 核心转换逻辑 (从 transform_multiple_assign.py 复制)
# ==========================================


class RewriteName(ast.NodeTransformer):
    def __init__(self, Map_var):
        super(RewriteName, self).__init__()
        self.Map_var = Map_var

    def visit_Name(self, node):
        if ast.unparse(node) in self.Map_var:
            return self.Map_var[ast.unparse(node)]
        else:
            return node

    def visit_Attribute(self, node):
        if ast.unparse(node) in self.Map_var:
            return self.Map_var[ast.unparse(node)]
        else:
            if isinstance(
                node.value, (ast.Attribute, ast.Name, ast.Subscript, ast.Slice)
            ):
                node.value = self.visit(node.value)
            return node

    def visit_Subscript(self, node):
        if ast.unparse(node) in self.Map_var:
            return self.Map_var[ast.unparse(node)]
        else:
            if isinstance(
                node.value, (ast.Attribute, ast.Name, ast.Subscript, ast.Slice)
            ):
                node.value = self.visit(node.value)
            if isinstance(
                node.slice, (ast.Attribute, ast.Name, ast.Subscript, ast.Slice)
            ):
                node.slice = self.visit(node.slice)
            return node

    def visit_Slice(self, node):
        if ast.unparse(node) in self.Map_var:
            return self.Map_var[ast.unparse(node)]
        else:
            if isinstance(
                node.lower, (ast.Attribute, ast.Name, ast.Subscript, ast.Slice)
            ):
                node.lower = self.visit(node.lower)
            if isinstance(
                node.upper, (ast.Attribute, ast.Name, ast.Subscript, ast.Slice)
            ):
                node.upper = self.visit(node.upper)
            if isinstance(
                node.step, (ast.Attribute, ast.Name, ast.Subscript, ast.Slice)
            ):
                node.step = self.visit(node.step)
            return node


def is_depend(pre_tar, next_tar):
    pre_tar_str = ast.unparse(pre_tar)
    for node in ast.walk(next_tar):
        if pre_tar_str == ast.unparse(node):
            return 1
    return 0


def _transform_multiple_assign(old_ass_list):
    """Transform consecutive assignments to tuple unpacking."""
    ass_list = copy.deepcopy(old_ass_list)
    remove_ind_list = set([])
    Map_var = dict()

    for ind, pre_ass in enumerate(ass_list[:-1]):
        for ind_e, next_ass in enumerate(ass_list[ind + 1 :]):
            pre_tar = pre_ass.targets[0]
            next_value = next_ass.value
            if is_depend(pre_tar, next_value):
                remove_ind_list.add(ind)
                pre_value = pre_ass.value
                Map_var = {**Map_var, ast.unparse(pre_tar): pre_value}

    left = []
    right = []
    for ind, assign in enumerate(ass_list):
        if ind in remove_ind_list:
            continue
        assign.value = RewriteName(Map_var).visit(assign.value)
        assign_str = ast.unparse(assign)
        vars = ast.unparse(assign).split("=")
        left.append(vars[0])
        right.append(ast.unparse(assign.value))

    return ", ".join(left) + " = " + ", ".join(right)


def transform(match: Match, config: Dict[str, Any]) -> str:
    """Transform consecutive assignments to tuple unpacking."""
    assigns = match.context["assigns"]
    return _transform_multiple_assign(assigns)
