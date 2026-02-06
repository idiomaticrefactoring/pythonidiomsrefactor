# -*- coding: utf-8 -*-
"""
Dict Comprehension - Detection logic (fully self-contained).

Detects:
- detect_refactor: for-loop + d[k]=v patterns that can become dict comprehensions
- detect_explain: existing dict comprehensions for explanation
"""

import ast
from typing import List, Dict, Any, Set, Tuple, Optional
from io import BytesIO
import tokenize as tokenize_module

from ...base_rule import Match
from ...ast_helpers import FunAnalyzer


# ============================================================
# Helper functions (inlined from comprehension_utils)
# ============================================================


def _safe_unparse(node: ast.AST) -> str:
    try:
        return ast.unparse(node)
    except Exception:
        return ""


def _tokenize_content(content: str) -> List[Tuple]:
    try:
        g = tokenize_module.tokenize(BytesIO(content.encode("utf-8")).readline)
        return list(g)
    except Exception:
        return []


def _visit_single_vars(target: ast.AST, var_list: List[str]) -> None:
    if isinstance(target, ast.Name):
        var_list.append(_safe_unparse(target))
    elif isinstance(target, ast.Subscript):
        var_list.append(_safe_unparse(target))
        _visit_single_vars(target.value, var_list)
    elif isinstance(target, ast.Attribute):
        var_list.append(_safe_unparse(target))
        _visit_single_vars(target.value, var_list)


def _get_time_var(vars_set: Set[str]) -> List[str]:
    all_var_list = []
    try:
        var_name = list(vars_set)[0]
        for e_var in ast.walk(ast.parse(var_name)):
            if _safe_unparse(e_var) == var_name and isinstance(
                e_var, (ast.Subscript, ast.Attribute, ast.Name)
            ):
                _visit_single_vars(e_var, all_var_list)
                break
    except Exception:
        pass
    if not all_var_list and vars_set:
        all_var_list.append(list(vars_set)[0])
    return all_var_list


def _whether_contain_var(
    node: ast.AST, vars_set: Set[str], time_var_list: List[str]
) -> int:
    count = 0
    s = _safe_unparse(node)
    if not s or s == list(vars_set)[0]:
        return 0
    for tok in _tokenize_content(s):
        if len(tok) >= 2 and tok[1] in time_var_list:
            count += 1
    return count


def _get_func_name(one_body: ast.AST) -> Tuple[Optional[str], Optional[str]]:
    """Get function/operator name and target variable for dict operations."""
    pre_name, call_name = None, None
    if isinstance(one_body, ast.Expr) and isinstance(one_body.value, ast.Call):
        call_front = one_body.value.func
        if isinstance(call_front, ast.Name):
            call_name = _safe_unparse(call_front)
        elif isinstance(call_front, ast.Attribute):
            call_name = call_front.attr
            pre_name = _safe_unparse(call_front.value)
        else:
            call_name = _safe_unparse(call_front)
    # Handle d[k] = v pattern (__setitem__)
    elif isinstance(one_body, ast.Assign):
        if len(one_body.targets) == 1 and isinstance(
            one_body.targets[0], ast.Subscript
        ):
            pre_name = _safe_unparse(one_body.targets[0].value)
            call_name = "__setitem__"
    return pre_name, call_name


def _whether_fun_is_setitem(
    one_body: ast.AST, assign_block_list: List, const_func_name: str = "__setitem__"
) -> bool:
    """Check if the body is a dict setitem operation (d[k] = v)."""
    # Handle d[k] = v pattern
    if const_func_name == "__setitem__":
        if isinstance(one_body, ast.Assign):
            if len(one_body.targets) == 1 and isinstance(
                one_body.targets[0], ast.Subscript
            ):
                assign_block_list.append([one_body])
                return True
    # Handle method call pattern (fallback)
    call_node = None
    if isinstance(one_body, ast.Expr) and isinstance(one_body.value, ast.Call):
        call_node = one_body.value
    elif isinstance(one_body, ast.Call):
        call_node = one_body
    if call_node:
        call_front = call_node.func
        call_name = (
            call_front.attr
            if isinstance(call_front, ast.Attribute)
            else _safe_unparse(call_front)
        )
        if call_name == const_func_name:
            assign_block_list.append([one_body])
            return True
    return False


def _for_traverse(node: ast.AST, assign_block_list: List, const_func_name: str) -> bool:
    if isinstance(node, ast.For) and node.orelse:
        return False
    for_body_list = node.body if hasattr(node, "body") else []
    if len(for_body_list) != 1:
        return False

    one_body = for_body_list[0]
    if isinstance(one_body, ast.For):
        return _for_traverse(one_body, assign_block_list, const_func_name)
    elif isinstance(one_body, ast.If):
        return _if_traverse(one_body, assign_block_list, const_func_name)
    elif isinstance(one_body, (ast.Expr, ast.Assign)):
        return _whether_fun_is_setitem(one_body, assign_block_list, const_func_name)
    return False


def _if_traverse(
    one_body: ast.If, assign_block_list: List, const_func_name: str
) -> bool:
    if not one_body.orelse:
        return _for_traverse(one_body, assign_block_list, const_func_name)
    return _if_else_traverse(one_body, assign_block_list, const_func_name)


def _if_else_traverse(
    if_body: ast.If, assign_block_list: List, const_func_name: str
) -> bool:
    if_body_list = if_body.body
    if len(if_body_list) != 1:
        return False
    if_body_flag = _whether_fun_is_setitem(
        if_body_list[0], assign_block_list, const_func_name
    )
    return if_body_flag and _else_traverse(if_body, assign_block_list, const_func_name)


def _else_traverse(
    if_body: ast.If, assign_block_list: List, const_func_name: str
) -> bool:
    else_body_list = if_body.orelse
    if len(else_body_list) != 1:
        return False
    else_body_one = else_body_list[0]
    if isinstance(else_body_one, ast.If):
        return _if_else_traverse(else_body_one, assign_block_list, const_func_name)
    return _whether_fun_is_setitem(else_body_one, assign_block_list, const_func_name)


def _filter_overlap(code_list: List) -> List:
    if len(code_list) <= 1:
        return code_list
    no_overlap = []
    for i, code in enumerate(code_list):
        beg, end = code[0].lineno, code[0].end_lineno
        is_overlapped = any(
            i != j
            and beg >= code_list[j][0].lineno
            and end <= code_list[j][0].end_lineno
            for j in range(len(code_list))
        )
        if not is_overlapped:
            no_overlap.append(code)
    return no_overlap


def _whether_first_var_is_empty_assign(
    tree, for_node, vars_set, const_func_name, const_empty_list
):
    assign_stmt = None
    assign_stmt_lineno = None
    flag = 0
    remove_ass_flag = 0

    time_var_list = _get_time_var(vars_set)
    time = _whether_contain_var(for_node, vars_set, time_var_list)
    append_time = 0

    for child in ast.walk(for_node):
        if isinstance(child, ast.Call):
            a = []
            if _whether_fun_is_setitem(child, a, const_func_name):
                append_time += 1
        elif isinstance(child, ast.Assign) and const_func_name == "__setitem__":
            a = []
            if _whether_fun_is_setitem(child, a, const_func_name):
                append_time += 1

    if time - append_time > 0:
        return 1, assign_stmt_lineno, assign_stmt, remove_ass_flag

    # Search for the empty list assignment before the for loop
    for_node_block_record = None
    found = False
    for node in ast.walk(tree):
        if found:
            break
        if hasattr(node, "body") and isinstance(node.body, list):
            for_in_body = any(
                hasattr(c, "lineno") and c.lineno == for_node.lineno for c in node.body
            )
            if not for_in_body:
                continue
            for child in node.body:
                if isinstance(child, ast.Assign) and child.lineno < for_node.lineno:
                    try:
                        target_name = _safe_unparse(child).strip().split("=")[0].strip()
                        value_str = _safe_unparse(child.value).replace(" ", "")
                        clean_consts = [x.replace(" ", "") for x in const_empty_list]
                        if (
                            target_name == list(vars_set)[0]
                            and value_str in clean_consts
                        ):
                            assign_stmt = child
                            assign_stmt_lineno = child.lineno
                            for_node_block_record = node
                            flag = 2
                            found = True
                            break
                    except Exception:
                        pass

    if for_node_block_record:
        # Check if for_node is a direct child of the block
        for child in for_node_block_record.body:
            if hasattr(child, "lineno") and child.lineno == for_node.lineno:
                remove_ass_flag = 1
                break
    else:
        return 1, assign_stmt_lineno, assign_stmt, remove_ass_flag

    return flag, assign_stmt_lineno, assign_stmt, remove_ass_flag


def _get_complicated_for_comprehen_code_list(tree, const_empty_list, const_func_name):
    code_list = []
    if not hasattr(tree, "body"):
        return []

    for node in ast.walk(tree):
        if isinstance(node, ast.For):
            assign_block_list = []
            if _for_traverse(node, assign_block_list, const_func_name):
                vars_set = set()
                for each_block in assign_block_list:
                    pre_name, _ = _get_func_name(each_block[0])
                    if pre_name:
                        vars_set.add(pre_name)

                if len(vars_set) != 1:
                    continue

                flag, _, assign_stmt, remove_ass_flag = (
                    _whether_first_var_is_empty_assign(
                        tree, node, vars_set, const_func_name, const_empty_list
                    )
                )

                if flag == 2:
                    code_list.append([node, assign_stmt, remove_ass_flag])

    return _filter_overlap(code_list)


# ============================================================
# Public detection functions
# ============================================================


def detect_refactor(content: str, config: Dict[str, Any]) -> List[Match]:
    """Detect non-idiomatic for-loop patterns that can become dict comprehensions."""
    matches = []

    try:
        file_tree = ast.parse(content)
        analyzer = FunAnalyzer()
        analyzer.visit(file_tree)

        for tree, class_name in analyzer.func_def_list:
            method_name = getattr(tree, "name", "")

            code_list = _get_complicated_for_comprehen_code_list(
                tree, const_empty_list=["dict()", "{}"], const_func_name="__setitem__"
            )

            for for_node, assign_node, remove_ass_flag in code_list:
                context = {
                    "class_name": class_name or "NULL",
                    "method_name": method_name or "Global",
                    "for_node": for_node,
                    "assign_node": assign_node,
                    "remove_ass_flag": remove_ass_flag,
                }

                old_code = ast.unparse(assign_node) + "\n" + ast.unparse(for_node)
                lineno = [
                    [assign_node.lineno, assign_node.end_lineno],
                    [for_node.lineno, for_node.end_lineno],
                ]

                matches.append(
                    Match(
                        node=(for_node, assign_node),
                        context=context,
                        old_code=old_code,
                        lineno=lineno,
                    )
                )

        return matches

    except Exception:
        import traceback

        traceback.print_exc()
        return []


def detect_explain(content: str, config: Dict[str, Any]) -> List[Match]:
    """Detect idiomatic dict comprehension patterns for explanation."""
    matches = []

    try:
        tree = ast.parse(content)
    except Exception:
        return []

    # Add parent references
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.DictComp):
            class_name, method_name = _get_context(node)
            has_if = any(gen.ifs for gen in node.value.generators)

            context = {
                "class_name": class_name,
                "method_name": method_name,
                "has_if": has_if,
                "assign_node": node,
                "dict_comp_node": node.value,
            }

            old_code = ast.unparse(node)
            lineno = [[node.lineno, node.end_lineno]]

            matches.append(
                Match(node=node, context=context, old_code=old_code, lineno=lineno)
            )

    return matches


def _get_context(node: ast.AST) -> Tuple[str, str]:
    class_name = "NULL"
    method_name = "Global"
    curr = node
    while hasattr(curr, "parent"):
        curr = curr.parent
        if isinstance(curr, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if method_name == "Global":
                method_name = curr.name
        elif isinstance(curr, ast.ClassDef):
            if class_name == "NULL":
                class_name = curr.name
                break
    return class_name, method_name
