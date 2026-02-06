# -*- coding: utf-8 -*-
"""
For Multiple Targets - Detection logic (fully self-contained).

Core logic copied from RefactoringIdioms/extract_complicate_code/extract_for_multiple_target.py
"""

import ast
import copy
import traceback
from typing import List, Dict, Any, Set

from ...base_rule import Match
from ...ast_helpers import FunAnalyzer, get_basic_count


# ==========================================
# 核心检测逻辑 (从 extract_for_multiple_target.py 复制)
# ==========================================


def whether_slice_is_constant(slice, var):
    """判断切片是否为常量"""
    if isinstance(slice, ast.Constant):
        slice_value = slice.value
        if isinstance(slice_value, int):
            return True
        else:
            return False
    elif isinstance(slice, ast.Slice):
        if slice.lower:
            if not isinstance(slice.lower, ast.Constant):
                return False
        if slice.upper:
            if not isinstance(slice.upper, ast.Constant):
                return False
        if slice.step:
            if isinstance(slice.step, ast.Constant):
                if not (isinstance(slice.step.value, int) and slice.step.value == 1):
                    return False
            else:
                return False
    return False


def is_var_subscript(node, var):
    if isinstance(node, ast.Subscript):
        value = node.value
        if ast.unparse(value) == var:
            slice = node.slice
            return whether_slice_is_constant(slice, var)
        elif isinstance(value, ast.Subscript):
            return is_var_subscript(value, var)
    return False


def is_var(node, var_ast):
    if isinstance(node, type(var_ast)) and ast.unparse(node) == ast.unparse(var_ast):
        return True
    return False


def whether_var_subscript(node, target, var_list):
    var = ast.unparse(target)
    if is_var_subscript(node, var):
        var_list.add(node)
        return True
    elif is_var(node, target):
        return False
    else:
        for e in ast.iter_child_nodes(node):
            if not whether_var_subscript(e, target, var_list):
                return False
        return True


def get_for_target(tree):
    """
    获取可重构的 For 循环目标
    :param max_unpack: 最大允许解包的元素数量限制
    """
    code_list = []

    for node in ast.walk(tree):
        if isinstance(node, ast.For):
            var_list = set([])
            target = node.target
            var = ast.unparse(target)

            count_obj = get_basic_count(target)
            if count_obj == 1:
                # 1. 检查循环体中是否有对 target 的写操作 (如果有则不能重构)
                has_write = False
                for e_body in ast.walk(node):
                    if isinstance(e_body, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                        targets = (
                            e_body.targets
                            if hasattr(e_body, "targets")
                            else [e_body.target]
                        )
                        for left_e in targets:
                            if ast.unparse(left_e) == var:
                                has_write = True
                                break
                            # 深度遍历左值
                            for ass_e in ast.walk(left_e):
                                if ast.unparse(ass_e) == var:
                                    has_write = True
                                    break
                            if has_write:
                                break
                        if has_write:
                            break
                if has_write:
                    continue

                # 2. 检查循环体中是否有对 target 的使用
                has_use = False
                for stmt in node.body:
                    for e in ast.walk(stmt):
                        if is_var(e, target):
                            has_use = True
                            break
                    if has_use:
                        break

                if has_use:
                    # 3. 检查所有使用是否都是下标访问 (var[0])
                    all_subscript = True
                    for stmt in node.body:
                        if not whether_var_subscript(stmt, target, var_list):
                            all_subscript = False
                            break

                    if all_subscript:
                        var_list_real = list(var_list)

                        # 去重逻辑: ['val[1]', 'val[1][0]'] -> 保留最外层
                        for i, var1 in enumerate(var_list):
                            for j, var2 in enumerate(var_list):
                                if ast.unparse(var1) in ast.unparse(
                                    var2
                                ) and ast.unparse(var1) != ast.unparse(var2):
                                    if var2 in var_list_real:
                                        var_list_real.remove(var2)

                        code_list.append([node, var_list_real])
    return code_list


# ==========================================
# 适配 ridiom_core 接口
# ==========================================


def detect_refactor(content: str, config: Dict[str, Any]) -> List[Match]:
    """Detect for loops that can unpack their targets."""
    matches = []

    try:
        file_tree = ast.parse(content)
        ana_py = FunAnalyzer()
        ana_py.visit(file_tree)

        search_targets = (
            ana_py.func_def_list if ana_py.func_def_list else [(file_tree, "Module")]
        )

        for tree, class_name in search_targets:
            try:
                me_name = getattr(tree, "name", "")
            except:
                me_name = ""

            new_code_list = get_for_target(tree)

            for e in new_code_list:
                if len(e) < 2:
                    continue

                old_node = e[0]
                var_list = e[1]

                context = {
                    "class_name": class_name if class_name != "Module" else "NULL",
                    "method_name": me_name or "Global",
                    "for_node": old_node,
                    "var_list": var_list,
                }

                line_list = [[old_node.lineno, old_node.end_lineno]]

                matches.append(
                    Match(
                        node=old_node,
                        context=context,
                        old_code=ast.unparse(old_node),
                        lineno=line_list,
                    )
                )

        return matches

    except Exception:
        traceback.print_exc()
        return []


def detect_explain(content: str, config: Dict[str, Any]) -> List[Match]:
    """Detect idiomatic tuple unpacking in for loops."""
    matches = []

    try:
        tree = ast.parse(content)
    except:
        return []

    for node in ast.walk(tree):
        if isinstance(node, ast.For) and isinstance(node.target, ast.Tuple):
            matches.append(
                Match(
                    node=node,
                    context={
                        "for_node": node,
                        "class_name": "NULL",
                        "method_name": "Global",
                    },
                    old_code=ast.unparse(node),
                    lineno=[[node.lineno, node.end_lineno]],
                )
            )

    return matches
