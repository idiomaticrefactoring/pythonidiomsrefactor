# -*- coding: utf-8 -*-
"""
Star in Function Call - Detection logic (fully self-contained).

Core logic copied from RefactoringIdioms/extract_complicate_code/extract_star_call.py

NOTE: This module uses sympy for symbolic math. Ensure sympy is installed.
"""

import ast
import copy
import traceback
from typing import List, Dict, Any

from ...base_rule import Match
from ...ast_helpers import FunAnalyzer

# 尝试导入 sympy，如果不可用则提供备用实现
from sympy import sympify


# ==========================================
# 核心检测逻辑 (从 extract_star_call.py 复制)
# ==========================================


def whether_add_end(slice_list, each_seq, arg_seq, step, new_arg_same_list, beg, end):
    if end == len(slice_list[1:]) and end > beg:
        # arg_list, ind_list, call node, step
        new_arg_same_list.append(
            [each_seq[beg : end + 1], arg_seq[1][beg : end + 1], arg_seq[2], step]
        )


def whether_add(each_seq, arg_seq, step, new_arg_same_list, beg, end):
    if end > beg:
        new_arg_same_list.append(
            [each_seq[beg : end + 1], arg_seq[1][beg : end + 1], arg_seq[2], step]
        )


def get_func_call_by_args(tree):
    arg_same_list = []
    new_arg_same_list = []

    # 1. 第一次遍历：寻找连续的 Subscript 参数 (如 a[0], a[1])
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            args_list = node.args
            var_set = []
            ind_list = []
            arg_one_list = []

            for ind_elts, e in enumerate(args_list):
                if isinstance(e, ast.Subscript):
                    if isinstance(e.slice, ast.Slice):
                        if len(var_set) > 1:
                            arg_same_list.append([arg_one_list, ind_list, node])
                        var_set = []
                        ind_list = []
                        arg_one_list = []
                        continue

                    e_value = e.value
                    value_str = ast.unparse(e_value)

                    if not var_set:
                        var_set.append(e_value)
                        ind_list.append(ind_elts)
                        arg_one_list.append(e)
                    else:
                        if value_str == ast.unparse(var_set[-1]):
                            var_set.append(e_value)
                            ind_list.append(ind_elts)
                            arg_one_list.append(e)
                            if ind_elts == len(args_list) - 1:
                                arg_same_list.append([arg_one_list, ind_list, node])
                        else:
                            if len(var_set) > 1:
                                arg_same_list.append([arg_one_list, ind_list, node])
                            var_set = [e_value]
                            ind_list = [ind_elts]
                            arg_one_list = [e]
                else:
                    if len(var_set) > 1:
                        arg_same_list.append([arg_one_list, ind_list, node])
                    var_set = []
                    ind_list = []
                    arg_one_list = []

    # 2. 第二次遍历：验证下标是否构成等差数列 (使用 sympy)
    for arg_seq in arg_same_list:
        each_seq = arg_seq[0]
        slice_list = []

        # 检查是否为字典定义 (排除字典下标)
        is_dict_access = False
        for e_child in ast.walk(tree):
            if (
                hasattr(e_child, "lineno")
                and e_child.lineno < each_seq[0].lineno
                and isinstance(e_child, (ast.Assign, ast.AnnAssign))
            ):
                targets = (
                    e_child.targets
                    if isinstance(e_child, ast.Assign)
                    else [e_child.target]
                )
                for tar in targets:
                    try:
                        if (
                            ast.unparse(tar) == ast.unparse(each_seq[0].value)
                            and hasattr(e_child, "value")
                            and (
                                ast.unparse(e_child.value).startswith("dict(")
                                or ast.unparse(e_child.value).startswith("{")
                            )
                        ):
                            is_dict_access = True
                            break
                    except:
                        continue
                if is_dict_access:
                    break

        if is_dict_access:
            continue

        # 提取切片
        for arg in each_seq:
            slice_list.append(arg.slice)

        # 计算步长 (Step)
        step = None
        beg = 0
        end = 0

        for ind, e_node in enumerate(slice_list[1:]):
            pre_var_str = ast.unparse(slice_list[ind])
            e_str = ast.unparse(e_node)

            if not step:
                try:
                    step_val = str(sympify(f"{e_str}-({pre_var_str})"))
                except:
                    step_val = "None"

                if not step_val.isdigit() or (
                    step_val.isdigit() and int(step_val) == 0
                ):
                    whether_add(each_seq, arg_seq, step, new_arg_same_list, beg, end)
                    step = None
                    end += 1
                    beg = end
                else:
                    step = int(step_val)
                    end += 1
                    whether_add_end(
                        slice_list, each_seq, arg_seq, step, new_arg_same_list, beg, end
                    )
            else:
                try:
                    new_step = str(sympify(f"{e_str}-({pre_var_str})"))
                except:
                    new_step = "None"

                if new_step.isdigit() and int(new_step) == step:
                    end += 1
                    whether_add_end(
                        slice_list, each_seq, arg_seq, step, new_arg_same_list, beg, end
                    )
                else:
                    whether_add(each_seq, arg_seq, step, new_arg_same_list, beg, end)
                    step = None
                    end += 1
                    beg = end

    return new_arg_same_list


# ==========================================
# 核心转换逻辑 (从 transform_var_unpack_call.py 复制)
# ==========================================


def build_star_node(arg_value_list, step):
    """构建 Starred 节点 (*a[i:j:step])"""
    star_node = None
    end = ast.unparse(arg_value_list[-1].slice)
    end = str(sympify(end + "+" + str(step)))
    a = [
        "*",
        ast.unparse(arg_value_list[0].value),
        "[",
        ast.unparse(arg_value_list[0].slice),
        ":",
        end,
        ":",
        str(step),
        "]",
    ]
    star_node = ast.parse("".join(a)).body[0]
    return star_node


def transform_var_unpack_call_each_args(arg_info_list):
    """转换单个参数组"""
    bia = 0
    step = arg_info_list[3]
    ind_list = arg_info_list[1]
    node = arg_info_list[2]
    args = node.args

    beg = ind_list[0] + bia
    arg_value_list = []
    for i in range(len(ind_list)):
        arg_value_list.append(args.pop(beg))

    star_node = build_star_node(arg_value_list, step)
    return star_node


# ==========================================
# 适配 ridiom_core 接口
# ==========================================


def detect_refactor(content: str, config: Dict[str, Any]) -> List[Match]:
    """Detect function call arguments that can use star unpacking."""
    matches = []

    try:
        file_tree = ast.parse(content)
        ana_py = FunAnalyzer()
        ana_py.visit(file_tree)

        # 兼容模块级代码
        search_targets = (
            ana_py.func_def_list if ana_py.func_def_list else [(file_tree, "Module")]
        )

        for tree, class_name in search_targets:
            try:
                me_name = getattr(tree, "name", "")
            except:
                me_name = ""

            # 获取候选列表
            new_arg_same_list = get_func_call_by_args(tree)

            for ind, arg_info_list in enumerate(new_arg_same_list):
                # arg_info_list 结构: [arg_nodes, ind_list, call_node, step]
                arg_nodes = arg_info_list[0]

                copy_arg_info_list = copy.deepcopy(arg_info_list)
                # 调用转换模块生成 Starred 节点 (如 *a[i:i+3])
                star_node = transform_var_unpack_call_each_args(copy_arg_info_list)

                arg_str_list = [ast.unparse(arg) for arg in arg_nodes]

                # 记录行号
                start_line = arg_nodes[0].lineno
                end_line = arg_nodes[-1].end_lineno
                line_list = [[start_line, end_line]]

                context = {
                    "class_name": class_name if class_name != "Module" else "NULL",
                    "method_name": me_name or "Global",
                    "arg_info_list": arg_info_list,
                    "star_node": star_node,
                    "new_code": ast.unparse(star_node),
                }

                matches.append(
                    Match(
                        node=arg_nodes,
                        context=context,
                        old_code=", ".join(arg_str_list),
                        lineno=line_list,
                    )
                )

        return matches

    except Exception:
        traceback.print_exc()
        return []


def detect_explain(content: str, config: Dict[str, Any]) -> List[Match]:
    """Detect idiomatic star unpacking in function calls."""
    matches = []

    try:
        tree = ast.parse(content)
    except:
        return []

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            for arg in node.args:
                if isinstance(arg, ast.Starred):
                    matches.append(
                        Match(
                            node=arg,
                            context={
                                "starred_arg": arg,
                                "class_name": "NULL",
                                "method_name": "Global",
                            },
                            old_code=ast.unparse(arg),
                            lineno=[[arg.lineno, arg.end_lineno]]
                            if hasattr(arg, "lineno")
                            else [],
                        )
                    )

    return matches
