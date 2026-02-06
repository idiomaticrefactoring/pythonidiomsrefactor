# -*- coding: utf-8 -*-
"""
Assign Multiple Targets - Detection logic (fully self-contained).

Core logic copied from RefactoringIdioms/extract_complicate_code/extract_assign_multiple.py
"""

import ast
import tokenize
import traceback
from io import BytesIO
from typing import List, Dict, Any

from ...base_rule import Match
from ...ast_helpers import FunAnalyzer, get_basic_count


# ==========================================
# 核心检测逻辑 (从 extract_assign_multiple.py 复制)
# ==========================================


def get_tokens(node):
    s = ast.unparse(node)
    g = tokenize.tokenize(BytesIO(s.encode("utf-8")).readline)
    tokens = set([])
    for toknum, child, _, _, _ in g:
        tokens.add(child)
    return tokens


class Visit_vars(ast.NodeVisitor):
    def __init__(self):
        self.vars = []

    def visit_Name(self, node):
        self.vars.append(node)

    def visit_Attribute(self, node):
        self.vars.append(node)

    def visit_Subscript(self, node):
        self.vars.append(node)


def visit_single_vars(target, list_vars):
    if isinstance(target, (ast.Name)):
        list_vars.append(ast.unparse(target))
    elif isinstance(target, ast.Subscript):
        list_vars.append(ast.unparse(target))
        if not isinstance(target.value, ast.Subscript):
            visit_single_vars(target.value, list_vars)
    elif isinstance(target, ast.Attribute):
        list_vars.append(ast.unparse(target))
        visit_single_vars(target.value, list_vars)
    else:
        for e in ast.iter_child_nodes(target):
            visit_single_vars(e, list_vars)


def is_occur_body(same_value_var, body_list):
    for body in body_list:
        for e in ast.walk(body):
            if ast.unparse(e) == same_value_var:
                return 1
    return 0


def is_not_intersect_value_also_in_left(all_target_list, value):
    for tar in all_target_list:
        if tar == value:
            return 0
    return 1


def once_again(ass):
    a = [ass]
    target = ass.targets[0]
    value = ass.value
    write_vars = []
    visit_single_vars(target, write_vars)
    all_write_vars = [write_vars]
    all_target_list = [ast.unparse(target)]
    all_value_list = [ast.unparse(value)]
    return a, all_write_vars, all_target_list, all_value_list


def split_assignments_overlap_read_write(all_assign_list, all_body_list):
    def is_depend(pre_tar, next_tar):
        pre_tar_str = ast.unparse(pre_tar)
        for node in ast.walk(next_tar):
            if pre_tar_str == ast.unparse(node):
                return 1
        return 0

    all_assign_left_no_overlap_list = []
    for ind_ass, assign_list in enumerate(all_assign_list):
        body_list = all_body_list[ind_ass]
        a = [assign_list[0]]
        for ind_e, ass in enumerate(assign_list[1:]):
            next_tar = ass.targets[0]
            for reverse_ind_e2, pre_ass in enumerate(a[::-1]):
                ind_e2 = len(a) - reverse_ind_e2 - 1
                pre_tar = pre_ass.targets[0]

                if is_depend(pre_tar, next_tar):
                    if len(a[: ind_e2 + 1]) > 1:
                        all_assign_left_no_overlap_list.append(
                            [a[: ind_e2 + 1], body_list]
                        )
                    a = a[ind_e2 + 1 :]
                    a.append(ass)
                    break
            else:
                a.append(ass)
        if len(a) > 1:
            all_assign_left_no_overlap_list.append([a, body_list])

    real_assign_list = []
    for ind_ass, (assign_list, body_list) in enumerate(all_assign_left_no_overlap_list):
        a = [assign_list[0]]
        overlap_flag = 0
        for ind_e, ass in enumerate(assign_list[1:]):
            next_value = ass.value
            for reverse_ind_e2, pre_ass in enumerate(a[::-1]):
                ind_e2 = len(a) - reverse_ind_e2 - 1
                pre_tar = pre_ass.targets[0]
                pre_value = pre_ass.value

                def intersect_var(pre_tar, next_value):
                    for node in ast.walk(next_value):
                        if ast.unparse(pre_tar) == ast.unparse(node):
                            return 1
                    for node in ast.walk(pre_tar):
                        if ast.unparse(node) == ast.unparse(next_value):
                            return 1
                    return 0

                def value_is_in_target_list(pre_value, ass_list):
                    for ass in ass_list:
                        tar = ass.targets[0]
                        if ast.unparse(pre_value) == ast.unparse(tar):
                            return 1
                    return 0

                if intersect_var(pre_tar, next_value):
                    if (
                        not is_depend(pre_tar, next_value)
                        or is_occur_body(ast.unparse(pre_tar), body_list)
                        or not value_is_in_target_list(pre_value, a[ind_e2 + 1 :])
                    ):
                        if len(a[: ind_e2 + 1]) > 1 and overlap_flag:
                            real_assign_list.append(a)
                        a = a[ind_e2 + 1 :]
                        a.append(ass)
                        if ind_e != len(assign_list[1:]) - 1:
                            overlap_flag = 0
                        break
                    else:
                        overlap_flag = 1
            else:
                a.append(ass)

        if len(a) > 1 and overlap_flag:
            real_assign_list.append(a)

    return real_assign_list


def split_assignments(all_assign_list, all_body_list):
    def is_depend(pre_tar, next_tar):
        pre_tar_str = ast.unparse(pre_tar)
        for node in ast.walk(next_tar):
            if pre_tar_str == ast.unparse(node):
                return 1
        return 0

    def is_depend_str(pre_tar_str, next_tar):
        for node in ast.walk(next_tar):
            if pre_tar_str == ast.unparse(node):
                return 1
        return 0

    all_assign_left_no_overlap_list = []
    for ind_ass, assign_list in enumerate(all_assign_list):
        body_list = all_body_list[ind_ass]
        a = [assign_list[0]]
        for ind_e, ass in enumerate(assign_list[1:]):
            next_tar = ass.targets[0]
            for reverse_ind_e2, pre_ass in enumerate(a[::-1]):
                ind_e2 = len(a) - reverse_ind_e2 - 1
                pre_tar = pre_ass.targets[0]

                if is_depend(pre_tar, next_tar):
                    if len(a[: ind_e2 + 1]) > 1:
                        all_assign_left_no_overlap_list.append(
                            [a[: ind_e2 + 1], body_list]
                        )
                    a = a[ind_e2 + 1 :]
                    a.append(ass)
                    break
            else:
                a.append(ass)
        if len(a) > 1:
            all_assign_left_no_overlap_list.append([a, body_list])

    real_assign_list = []
    for ind_ass, (assign_list, body_list) in enumerate(all_assign_left_no_overlap_list):
        a = [assign_list[0]]
        for ind_e, ass in enumerate(assign_list[1:]):
            next_value = ass.value
            for reverse_ind_e2, pre_ass in enumerate(a[::-1]):
                ind_e2 = len(a) - reverse_ind_e2 - 1
                pre_tar = pre_ass.targets[0]
                pre_value = pre_ass.value

                def value_is_in_target_list(pre_value, ass_list):
                    for ass in ass_list:
                        tar = ass.targets[0]
                        if ast.unparse(pre_value) == ast.unparse(tar):
                            return 1
                    return 0

                def intersect_var(pre_tar, next_value):
                    pre_var_list = []
                    for node in ast.walk(pre_tar):
                        pre_var_list.append(ast.unparse(node))

                    def visit_vars(target, list_vars, pre_var_list, pre_tar):
                        if isinstance(target, (ast.Name)):
                            list_vars.append(ast.unparse(target))
                        elif isinstance(target, ast.Subscript):
                            list_vars.append(ast.unparse(target))
                            if not (
                                isinstance(target, type(pre_tar))
                                and ast.unparse(target.value) in pre_var_list
                            ):
                                visit_vars(
                                    target.value, list_vars, pre_var_list, pre_tar
                                )
                            visit_vars(target.slice, list_vars, pre_var_list, pre_tar)
                        elif isinstance(target, ast.Attribute):
                            list_vars.append(ast.unparse(target))
                            if not (
                                isinstance(target, type(pre_tar))
                                and ast.unparse(target.value) in pre_var_list
                            ):
                                visit_vars(
                                    target.value, list_vars, pre_var_list, pre_tar
                                )
                        elif isinstance(target, list):
                            for e in target:
                                visit_vars(e, list_vars, pre_var_list, pre_tar)
                        else:
                            for e in ast.iter_child_nodes(target):
                                visit_vars(e, list_vars, pre_var_list, pre_tar)
                        pass

                    list_vars = []
                    visit_vars(next_value, list_vars, pre_var_list, pre_tar)
                    if set(list_vars) & set(pre_var_list):
                        return 1
                    return 0

                if intersect_var(pre_tar, next_value) or intersect_var(
                    next_value, pre_tar
                ):
                    if not (
                        is_depend(pre_tar, next_value)
                        and not is_occur_body(ast.unparse(pre_tar), body_list)
                        and value_is_in_target_list(pre_value, a[ind_e2 + 1 :])
                    ):
                        if len(a[: ind_e2 + 1]) > 1:
                            real_assign_list.append(a[: ind_e2 + 1])
                        a = a[ind_e2 + 1 :]
                        a.append(ass)
                        break
            else:
                a.append(ass)

        if len(a) > 1:
            real_assign_list.append(a)
    return real_assign_list


def get_multiple_assign(tree):
    assign_list = []
    body_list = []
    for e_trr in ast.walk(tree):
        if hasattr(e_trr, "body"):
            body = e_trr.body
            if not isinstance(body, list):
                continue
            a = []
            for ind_node, node in enumerate(body):
                if isinstance(node, ast.Assign):
                    targets = node.targets
                    count = 0
                    for e in targets:
                        count += get_basic_count(e)
                    if count > 1:
                        if len(a) > 1:
                            assign_list.append(a)
                            if ind_node + 1 <= len(body) - 1:
                                body_list.append(body[ind_node + 1 :])
                            else:
                                body_list.append([])
                        a = []
                        continue
                    else:
                        a.append(node)
                        if ind_node == len(body) - 1 and len(a) > 1:
                            assign_list.append(a)
                            body_list.append([])
                else:
                    if len(a) > 1:
                        assign_list.append(a)
                        if ind_node <= len(body) - 1:
                            body_list.append(body[ind_node:])
                        else:
                            body_list.append([])
                    a = []
        if hasattr(e_trr, "orelse"):
            body = e_trr.orelse
            if not isinstance(body, list):
                continue
            a = []
            for ind_node, node in enumerate(body):
                if isinstance(node, ast.Assign):
                    targets = node.targets
                    count = 0
                    for e in targets:
                        count += get_basic_count(e)
                    if count > 1:
                        if len(a) > 1:
                            assign_list.append(a)
                            if ind_node + 1 <= len(body) - 1:
                                body_list.append(body[ind_node + 1 :])
                            else:
                                body_list.append([])
                        a = []
                        continue
                    else:
                        a.append(node)
                        if ind_node == len(body) - 1 and len(a) > 1:
                            assign_list.append(a)
                            body_list.append([])
                else:
                    if len(a) > 1:
                        assign_list.append(a)
                        if ind_node <= len(body) - 1:
                            body_list.append(body[ind_node:])
                        else:
                            body_list.append([])
                    a = []

    return assign_list, body_list


# ==========================================
# 适配 ridiom_core 接口
# ==========================================


def detect_refactor(content: str, config: Dict[str, Any]) -> List[Match]:
    """Detect consecutive assignments that can be combined."""
    matches = []

    try:
        file_tree = ast.parse(content)
        ana_py = FunAnalyzer()
        ana_py.visit(file_tree)

        for tree, class_name in ana_py.func_def_list:
            try:
                me_name = tree.name
            except:
                me_name = ""
            all_assign_list, all_body_list = get_multiple_assign(tree)
            assign_list = split_assignments(all_assign_list, all_body_list)

            for ind_ass, each_assign_list in enumerate(assign_list):
                context = {
                    "class_name": class_name or "NULL",
                    "method_name": me_name or "Global",
                    "assigns": each_assign_list,
                }

                each_assign_list_str = "\n".join(
                    [ast.unparse(e_ass) for e_ass in each_assign_list]
                )
                line_list = [
                    [e_ass.lineno, e_ass.end_lineno] for e_ass in each_assign_list
                ]

                matches.append(
                    Match(
                        node=each_assign_list,
                        context=context,
                        old_code=each_assign_list_str,
                        lineno=line_list,
                    )
                )

        return matches

    except:
        traceback.print_exc()
        return []


def detect_explain(content: str, config: Dict[str, Any]) -> List[Match]:
    """Detect idiomatic tuple unpacking assignments."""
    matches = []

    try:
        tree = ast.parse(content)
    except:
        return []

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            if len(node.targets) == 1 and isinstance(node.targets[0], ast.Tuple):
                if isinstance(node.value, ast.Tuple):
                    matches.append(
                        Match(
                            node=node,
                            context={
                                "assign_node": node,
                                "class_name": "NULL",
                                "method_name": "Global",
                            },
                            old_code=ast.unparse(node),
                            lineno=[[node.lineno, node.end_lineno]],
                        )
                    )

    return matches
