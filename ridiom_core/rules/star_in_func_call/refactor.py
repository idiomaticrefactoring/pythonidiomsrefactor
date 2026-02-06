# -*- coding: utf-8 -*-
"""
Star in Function Call - Refactor transformation (fully self-contained).

Core logic copied from RefactoringIdioms/transform_c_s/transform_var_unpack_call.py
"""

import ast
import copy
from typing import Dict, Any

from ...base_rule import Match

from sympy import sympify

# ==========================================
# 核心转换逻辑 (从 transform_var_unpack_call.py 复制)
# ==========================================


def build_star_node(arg_value_list, step):
    """构建 Starred 节点 (*a[i:j:step])"""
    star_node = None
    # arg_value_list[-1] 是 AST 节点 (Subscript)
    end = ast.unparse(arg_value_list[-1].slice)
    end = str(sympify(end + "+" + str(step)))

    # 构造类似于 *a[start:end:step] 的字符串
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
    star_code = "".join(a)
    star_node = ast.parse(star_code).body[0]
    return star_node


def transform_var_unpack_call_each_args(arg_info_list):
    """转换单个参数组"""
    bia = 0
    step = arg_info_list[3]
    ind_list = arg_info_list[1]
    node = arg_info_list[2]  # Call node
    args = node.args

    beg = ind_list[0] + bia
    arg_value_list = []

    # 注意: 这里修改的是 node (Call node) 的 args 列表
    # 如果传入的是 deepcopy 的 arg_info_list，则修改的是副本
    for i in range(len(ind_list)):
        if beg < len(args):
            arg_value_list.append(args.pop(beg))

    if not arg_value_list:
        return None

    star_node = build_star_node(arg_value_list, step)
    return star_node


# ==========================================
# 适配 ridiom_core 接口
# ==========================================


def transform(match: Match, config: Dict[str, Any]) -> str:
    """Transform function call args to star unpacking."""
    if match.context.get("new_code"):
        return match.context["new_code"]

    arg_info_list = match.context.get("arg_info_list")
    if not arg_info_list:
        return match.old_code

    # 使用副本进行转换，避免副作用影响原始 AST
    copy_arg_info_list = copy.deepcopy(arg_info_list)
    star_node = transform_var_unpack_call_each_args(copy_arg_info_list)

    if star_node:
        # 这里返回的是替换后的代码片段 (Starred 节点)
        return ast.unparse(star_node)

    return match.old_code
