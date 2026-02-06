# -*- coding: utf-8 -*-
"""
Star in Function Call - Explain transformation (fully self-contained).

Core logic copied from DeIdiom/transform_s_c/transform_call_star_s_c.py
"""

import ast
import copy
import math
import traceback
from typing import Dict, Any

from ...base_rule import Match

import sympy


# ==========================================
# 核心转换逻辑 (从 transform_call_star_s_c.py 复制)
# ==========================================


def determine_refactor(star_node):
    """
    核心逻辑：计算 *args 的展开形式。
    返回: (success_flag, expanded_args_str, additional_assign_list)
    """
    additional_ass = []
    value = star_node.value

    # 1. 处理字面量 (List, Tuple, Set)
    if isinstance(value, (ast.List, ast.Tuple, ast.Set)):
        e_list = [ast.unparse(e) for e in value.elts]
        return True, ", ".join(e_list), additional_ass

    # 2. 处理常量 (Constant)
    elif isinstance(value, ast.Constant):
        try:
            # e.g. *[1, 2, 3]
            e_list = [str(e) for e in value.value]
            return True, ", ".join(e_list), additional_ass
        except:
            return False, "", additional_ass

    # 3. 处理切片 (Subscript with Slice) -> 最复杂的部分
    else:
        number_ele = None

        # 必须是切片形式: a[i:j:k]
        if isinstance(value, ast.Subscript) and isinstance(value.slice, ast.Slice):
            slice_node = value.slice
            star_var = value.value  # 切片的主体

            # 解析 step
            step = "1" if not slice_node.step else ast.unparse(slice_node.step)
            try:
                step_int = int(step)
            except:
                step_int = None

            if step_int:
                # 解析 upper / lower
                upper = (
                    f"len({ast.unparse(star_var)})"
                    if not slice_node.upper
                    else ast.unparse(slice_node.upper)
                )
                lower = "0" if not slice_node.lower else ast.unparse(slice_node.lower)

                # 尝试将上下界转为整数
                try:
                    upper_int = int(upper)
                except:
                    upper_int = None
                try:
                    lower_int = int(lower)
                except:
                    lower_int = None

                # 计算元素数量 logic
                if lower_int is not None and upper_int is not None:
                    # 简单情况：纯数字
                    if (lower_int >= 0 and upper_int >= 0) or (
                        lower_int <= 0 and upper_int <= 0
                    ):
                        if (step_int > 0 and upper_int - lower_int <= 0) or (
                            step_int < 0 and lower_int - upper_int <= 0
                        ):
                            number_ele = 0
                        else:
                            number_ele = math.ceil(
                                abs(upper_int - lower_int) / abs(step_int)
                            )

                elif lower_int is None or upper_int is None:
                    try:
                        expr_str = f"{upper}-({lower})"
                        diff = int(sympy.sympify(expr_str))  # 尝试化简差值
                        number_ele = math.ceil(diff / abs(step_int))
                    except Exception:
                        number_ele = None

                # 特殊修正
                if not slice_node.lower and step_int < 0:
                    # e.g. a[::-1] -> start is -1 effectively
                    lower = "-1"

        # 生成展开代码
        star_var_str = ast.unparse(value)

        # 如果表达式复杂，引入临时变量: tmp = a[...]; func(tmp[0], tmp[1])
        if not isinstance(value, ast.Name):
            tmp_var_name = "tmp_arg"
            additional_ass.append(f"{tmp_var_name} = {star_var_str}")
            star_var_str = tmp_var_name

        if number_ele is not None and number_ele > 0:
            try:
                # 尝试构建 a[lower + step*i]
                base_var = value.value  # a in a[0:3]
                base_var_str = ast.unparse(base_var)

                # 构造索引列表
                args_list = []
                for i in range(number_ele):
                    # 计算偏移: lower + step * i
                    if isinstance(lower, str) and not lower.isdigit() and lower != "-1":
                        idx_str = (
                            f"{lower} + {step_int * i}" if step_int * i != 0 else lower
                        )
                    else:
                        try:
                            start_val = int(lower)
                            idx_str = str(start_val + step_int * i)
                        except:
                            idx_str = f"{lower} + {step_int * i}"

                    args_list.append(f"{base_var_str}[{idx_str}]")

                return (
                    True,
                    ", ".join(args_list),
                    [],
                )
            except:
                traceback.print_exc()
                return False, "", []
        else:
            return False, "", []


def transform_star_call(call_node, star_node):
    """
    将带星号参数的函数调用转换为显式参数列表。
    E.g. func(*a[:2]) -> func(a[0], a[1])

    Args:
        call_node: ast.Call 节点
        star_node: ast.Starred 节点 (必须是 call_node.args 中的一个)
    """
    try:
        # 1. 计算展开后的参数字符串
        flag, expanded_args_str, additional_ass = determine_refactor(star_node)

        if not flag:
            return False, None

        # 2. 构造新代码
        new_call_node = copy.deepcopy(call_node)

        # 找到对应的 Starred 节点并替换
        new_args = []
        replaced = False
        for arg in new_call_node.args:
            if isinstance(arg, ast.Starred) and ast.unparse(arg.value) == ast.unparse(
                star_node.value
            ):
                if not replaced:
                    # 解析生成的字符串为 AST 节点列表
                    temp_list_node = ast.parse(f"[{expanded_args_str}]").body[0].value
                    new_args.extend(temp_list_node.elts)
                    replaced = True
                    continue
            new_args.append(arg)

        new_call_node.args = new_args

        # 3. 生成最终代码字符串
        new_code_str = ast.unparse(new_call_node)

        # 如果有额外的临时变量赋值 (pre-statements)
        if additional_ass:
            ass_block = "\n".join(additional_ass)
            new_code_str = f"{ass_block}\n{new_code_str}"

        return True, new_code_str

    except Exception:
        return False, None


# ==========================================
# 适配 ridiom_core 接口
# ==========================================


def transform(match: Match, config: Dict[str, Any]) -> str:
    """Transform star unpacking to explicit arguments."""
    context = match.context
    starred_arg = context.get("starred_arg")

    if not starred_arg:
        return match.old_code

    # 我们需要完整的 Call 节点才能转换，但在 explain 模式下只有 starred_arg
    # 这里简单返回 starred_arg 的展开形式
    flag, expanded_str, additional_ass = determine_refactor(starred_arg)
    if flag:
        return expanded_str
    else:
        return match.old_code
