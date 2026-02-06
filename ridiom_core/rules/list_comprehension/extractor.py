# -*- coding: utf-8 -*-
"""
List Comprehension - Detection logic (fully self-contained).

Detects:
- detect_refactor: for-loop + append patterns that can become list comprehensions
- detect_explain: existing list comprehensions for explanation
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
    """Safely unparse AST node, compatible with Python < 3.9."""
    if hasattr(ast, "unparse"):
        try:
            return ast.unparse(node)
        except Exception:
            return ""
    else:
        try:
            if isinstance(node, ast.Name):
                return node.id
            elif isinstance(node, ast.Attribute):
                val = _safe_unparse(node.value)
                return f"{val}.{node.attr}" if val else ""
            elif isinstance(node, ast.Constant):
                return str(node.value)
            elif isinstance(node, ast.Subscript):
                val = _safe_unparse(node.value)
                # In Python < 3.9, slice might be an Index wrapper or direct or Slice
                # For simplicity in this fallback, we recurse on slice
                sl = _safe_unparse(node.slice)
                return f"{val}[{sl}]" if val else ""
            return ""
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

    return count


def _check_call_usage_in_tree(
    tree: ast.AST, fun_name: str, time_var_list: List[str]
) -> bool:
    """Check if variable is used in a specific function (closure check)."""
    try:
        analyzer = FunAnalyzer()
        analyzer.visit(tree)
        for tree_fun, _ in analyzer.func_def_list:
            if hasattr(tree_fun, "name") and tree_fun.name == fun_name:
                for child in ast.walk(tree_fun):
                    if _safe_unparse(child) in time_var_list:
                        return True
    except Exception:
        pass
    return False


def _is_use_var(next_child: ast.AST, vars_set: Set[str]) -> int:
    """Check if a node uses the target variable."""
    s = _safe_unparse(next_child)
    if not s:
        return 0
    target_var = list(vars_set)[0]
    if s != target_var:
        try:
            tokens = _tokenize_content(s)
            for tok in tokens:
                if len(tok) >= 2 and tok[1].strip() == target_var:
                    return 1
        except Exception:
            pass
    return 0


def _get_func_name(one_body: ast.AST) -> Tuple[Optional[str], Optional[str]]:
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
    return pre_name, call_name


def _whether_fun_is_append(
    one_body: ast.AST, assign_block_list: List, const_func_name: str = "append"
) -> bool:
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
    elif isinstance(one_body, ast.Expr):
        return _whether_fun_is_append(one_body, assign_block_list, const_func_name)
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
    if_body_flag = _whether_fun_is_append(
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
    return _whether_fun_is_append(else_body_one, assign_block_list, const_func_name)


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
        # 1. Check append/add calls
        if isinstance(child, ast.Call):
            a = []
            if _whether_fun_is_append(child, a, const_func_name):
                append_time += 1

            try:
                fun_name = ""
                if hasattr(child.func, "attr"):
                    fun_name = child.func.attr
                elif hasattr(child.func, "id"):
                    fun_name = child.func.id
                else:
                    parts = _safe_unparse(child.func).split(".")
                    fun_name = parts[-1] if parts else ""

                # Check direct arguments for variable usage
                for arg in child.args:
                    if _safe_unparse(arg) in time_var_list:
                        flag = 1
                        return flag, assign_stmt_lineno, assign_stmt, remove_ass_flag

                # Check closure/global usage
                if _check_call_usage_in_tree(tree, fun_name, time_var_list):
                    flag = 1
                    return flag, assign_stmt_lineno, assign_stmt, remove_ass_flag
            except Exception:
                pass

        # 2. Check dict assignment (d[k] = v)
        elif isinstance(child, ast.Assign) and const_func_name == "__setitem__":
            a = []
            if _whether_fun_is_append(child, a, const_func_name):
                append_time += 1

    if time - append_time > 0:
        return 1, assign_stmt_lineno, assign_stmt, remove_ass_flag

    # Search for the empty list assignment before the for loop
    for_node_block_record = None
    found = False
    for node in ast.walk(tree):
        if found:
            break
        # Calculate end_lineno roughly if not present for the block check
        # But usually nodes in tree should have lineno
        if hasattr(node, "lineno") and node.lineno == for_node.lineno:
            break

        if hasattr(node, "body") and isinstance(node.body, list):
            # Check if this block contains our for_node
            has_for = False
            if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                if node.lineno < for_node.lineno <= node.end_lineno:
                    has_for = True
            elif node.body:
                # Fallback: check body range
                first = node.body[0]
                last = node.body[-1]
                if (
                    hasattr(first, "lineno")
                    and hasattr(last, "end_lineno")
                    and first.lineno < for_node.lineno < last.end_lineno
                ):
                    has_for = True

            if not has_for:
                continue

            for child in node.body:
                if isinstance(child, ast.Assign):
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
                            # Don't break here, we need the latest assignment before loop?
                            # Legacy code assigns and continues but legacy logic seems to rely on finding THE assignment.
                            # We will assume unique assignment for simplicity or last one win.
                            assign_stmt = child
                            assign_stmt_lineno = child.lineno
                            for_node_block_record = node
                            flag = 2
                    except Exception:
                        pass

    if for_node_block_record:
        # Check if for_node is a direct child of the block to set remove flag
        for child in ast.iter_child_nodes(for_node_block_record):
            if child == for_node:
                remove_ass_flag = 1

        # Check for intermediate usage between assignment and for loop
        for node in ast.walk(for_node_block_record):
            if hasattr(node, "end_lineno") and hasattr(node, "lineno"):
                if (
                    node != assign_stmt
                    and node.end_lineno < for_node.lineno
                    and node.lineno > assign_stmt_lineno
                ):
                    # Check if this node uses the variable
                    if _is_use_var(node, vars_set):
                        flag = 1
                        return flag, assign_stmt_lineno, assign_stmt, remove_ass_flag

            # Check for nested loop overlap (legacy logic)
            if (
                isinstance(node, (ast.For, ast.While, ast.AsyncFor))
                and hasattr(node, "lineno")
                and hasattr(node, "end_lineno")
            ):
                if (
                    for_node.lineno > node.lineno > assign_stmt_lineno
                    and node.end_lineno >= for_node.end_lineno
                ):
                    # This implies for_node is inside another loop that is after assignment
                    return 1, assign_stmt_lineno, assign_stmt, remove_ass_flag

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
    """Detect non-idiomatic for-loop patterns that can become list comprehensions."""
    matches = []

    try:
        file_tree = ast.parse(content)
        analyzer = FunAnalyzer()
        analyzer.visit(file_tree)

        for tree, class_name in analyzer.func_def_list:
            method_name = getattr(tree, "name", "")

            code_list = _get_complicated_for_comprehen_code_list(
                tree, const_empty_list=["[]", "list()"], const_func_name="append"
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
    """Detect idiomatic list comprehension patterns for explanation."""
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
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.ListComp):
            class_name, method_name = _get_context(node)
            has_if = any(gen.ifs for gen in node.value.generators)

            context = {
                "class_name": class_name,
                "method_name": method_name,
                "has_if": has_if,
                "assign_node": node,
                "list_comp_node": node.value,
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
