# -*- coding: utf-8 -*-
"""
Assign Multiple Targets - Explain transformation (fully self-contained).

Core logic copied from DeIdiom/transform_s_c/transform_multi_assign_s_c.py
"""

import ast
import copy
import traceback
from typing import Dict, Any

from ...base_rule import Match


# ==========================================
# 核心转换逻辑 (从 transform_multi_assign_s_c.py 复制)
# ==========================================


def whether_repeat_var(target_list, value_list):
    tmp_ass_list = []
    new_value_list = value_list

    count = 0

    for ind_tar, tar in enumerate(target_list[:-1]):
        for ind, value in enumerate(value_list[ind_tar + 1 :]):
            for node in ast.walk(ast.parse(value)):
                if ast.unparse(node) == tar:
                    tmp_str = f"tmp{count}"
                    tmp_ass_list.append("".join([tmp_str, " = ", value]))
                    new_value_list[ind + ind_tar + 1] = tmp_str
                    count += 1
                    break
            else:
                for node in ast.walk(ast.parse(tar)):
                    if ast.unparse(node) == value:
                        tmp_str = f"tmp{count}"
                        tmp_ass_list.append("".join([tmp_str, " = ", value]))
                        new_value_list[ind + ind_tar + 1] = tmp_str
                        count += 1
                        break
                else:
                    continue
                break
            break
    return tmp_ass_list, new_value_list, count


# count represent the number of temporary values
def whether_add_tmp_var(target_list, value_list):
    tmp_ass_list, new_value_list, count = whether_repeat_var(target_list, value_list)
    new_ass_list = []
    new_ass_list.extend(tmp_ass_list)
    for ind, tar in enumerate(target_list):
        new_ass_list.append("".join([target_list[ind], " = ", new_value_list[ind]]))
    return "\n".join(new_ass_list), count


def get_basic_object_value_star(e, tar, var_list=[], value_list=[]):
    if isinstance(e, (ast.Tuple, ast.List)):
        try:
            tar_elts = tar.elts
            bias = 0
            for ind, cur in enumerate(e.elts):
                if isinstance(cur, ast.Starred):
                    star_len = len(tar_elts) - len(e.elts)
                    new_tar_list = [i for i in tar_elts[ind : ind + star_len + 1]]
                    bias += star_len
                    get_basic_object_value_star(cur, new_tar_list, var_list, value_list)
                else:
                    get_basic_object_value_star(
                        cur, tar_elts[ind + bias], var_list, value_list
                    )

        except:
            var_list.append("SYNTAXERROR")
            value_list.append("SYNTAXERROR")
    elif isinstance(e, ast.Starred):
        value = ast.unparse(e.value)
        value_list.extend([value + f"[{i}]" for i, v in enumerate(tar)])
        var_list.extend([ast.unparse(v) for i, v in enumerate(tar)])
    else:
        var_list.append(ast.unparse(tar))
        value_list.append(ast.unparse(e))


def get_basic_object(e, value, var_list=[], value_list=[], tmp_ass_list=[]):
    if isinstance(e, (ast.Tuple, ast.List)):
        try:
            if hasattr(value, "elts"):
                value_elts = value.elts
                bias = 0

                for ind, cur in enumerate(e.elts):
                    if isinstance(cur, ast.Starred):
                        star_len = len(value_elts) - len(e.elts)
                        new_value_list = [
                            i for i in value_elts[ind : ind + star_len + 1]
                        ]
                        bias += star_len
                        get_basic_object(
                            cur, new_value_list, var_list, value_list, tmp_ass_list
                        )
                    else:
                        get_basic_object(
                            cur,
                            value_elts[ind + bias],
                            var_list,
                            value_list,
                            tmp_ass_list,
                        )
            else:
                value_str_e = ast.unparse(value)
                for e_val in ast.walk(value):
                    if isinstance(e_val, ast.Call):
                        value_str_e = "tmp_fun_" + str(len(tmp_ass_list))
                        tmp_ass_list.append(
                            "".join([value_str_e, " = ", ast.unparse(value), "\n"])
                        )
                        break

                for ind, cur in enumerate(e.elts):
                    if isinstance(cur, ast.Starred):
                        star_len = len(e.elts) - ind
                        if star_len == 1:
                            value_str = value_str_e + f"[{ind}:]"
                        else:
                            value_str = value_str_e + f"[{ind}:-{star_len - 1}]"
                    else:
                        value_str = value_str_e + f"[{ind}]"
                    for w in ast.walk(ast.parse(value_str)):
                        if isinstance(w, ast.Subscript):
                            get_basic_object(cur, w, var_list, value_list, tmp_ass_list)
                            break
        except:
            var_list.append("SYNTAXERROR")
            value_list.append("SYNTAXERROR")

    elif isinstance(e, ast.Starred):
        var_list.append(ast.unparse(e.value))
        if isinstance(value, list):
            a = f"[{','.join([ast.unparse(v) for v in value])}]"
        else:
            a = ast.unparse(value)
        value_list.append(a)
    else:
        var_list.append(ast.unparse(e))
        value_list.append(ast.unparse(value))


def transform_assign_multi(node):
    """
    将多重赋值/解包赋值转换为基础赋值序列。

    Returns:
        tuple: (success_flag, new_code_string)
    """
    new_ass_str_list = []
    ass_trans_list = []

    # 1. 处理链式赋值 a = b = c = 1
    if len(node.targets) > 1:
        tmp_value = "tmp_value"
        new_ass_str_list = [f"{tmp_value} = {ast.unparse(node.value)}\n"]
        for tar in node.targets:
            # 构造虚拟的单一赋值 a = tmp_value
            virtual_assign = ast.Assign(
                targets=[tar], value=ast.Name(id=tmp_value, ctx=ast.Load())
            )
            ass_trans_list.append(virtual_assign)
    else:
        ass_trans_list.append(node)

    # 2. 处理每个单一赋值 (包含解包逻辑)
    for sub_node in ass_trans_list:
        # 由于上面已经拆解了链式赋值，这里 targets 长度必定为 1
        tar = sub_node.targets[0]

        tmp_ass_list = []
        var_list = []
        value_list = []

        # 统计星号
        count_star_tar = sum(1 for e in ast.walk(tar) if isinstance(e, ast.Starred))
        count_star_val = sum(
            1 for e in ast.walk(sub_node.value) if isinstance(e, ast.Starred)
        )

        # 复杂情况直接放弃 (如两边都有星号)
        if (
            count_star_val > 1
            or count_star_tar > 1
            or (count_star_val >= 1 and count_star_tar >= 1)
        ):
            return False, None

        # 核心解包逻辑
        if count_star_val:
            get_basic_object_value_star(
                copy.deepcopy(sub_node.value), tar, var_list, value_list
            )
        else:
            get_basic_object(
                tar, copy.deepcopy(sub_node.value), var_list, value_list, tmp_ass_list
            )

        if "SYNTAXERROR" in var_list:
            return False, None

        # 生成新代码 (处理变量交换等冲突)
        new_str, _ = whether_add_tmp_var(var_list, value_list)

        # 拼接临时函数变量声明 (如果有)
        full_block = "".join(tmp_ass_list) + new_str
        new_ass_str_list.append(full_block + "\n")

    compli_ass_stmt = "".join(new_ass_str_list).strip()
    return True, compli_ass_stmt


# ==========================================
# 适配 ridiom_core 接口
# ==========================================


def transform(match: Match, config: Dict[str, Any]) -> str:
    """Transform tuple unpacking to separate assignments."""
    context = match.context
    node = context.get("assign_node") or match.node

    if not node or not isinstance(node, ast.Assign):
        # 如果 context 没有 assign_node，尝试解析 old_code
        try:
            node = ast.parse(match.old_code).body[0]
        except:
            return match.old_code

    success, new_code = transform_assign_multi(node)

    if success:
        return new_code
    else:
        return match.old_code
