# -*- coding: utf-8 -*-
"""
For Multiple Targets - Explain transformation (fully self-contained).

Core logic copied from DeIdiom/transform_s_c/transform_for_target_multi_s_c.py
"""

import ast
import copy
from typing import Dict, Any

from ...base_rule import Match


# ==========================================
# 核心转换逻辑 (从 transform_for_target_multi_s_c.py 复制)
# ==========================================


def get_Subscript_node(code_str):
    """辅助函数：将字符串形式的下标访问转换为 AST 节点"""
    return ast.parse(code_str).body[0].value


def trasnform_target(elts, Map_var, pre_str):
    """
    递归解析解包结构，生成变量到索引的映射。
    Args:
        elts: 解包元素列表 (e.g. [a, b])
        Map_var: 结果字典 {变量名: 索引AST}
        pre_str: 当前层级的临时变量名 (e.g. "e_target")
    """
    count_sub = 0
    # 偏移量逻辑：用于处理带星号的情况

    for ind, e_elt in enumerate(elts):
        if isinstance(e_elt, ast.Starred):
            # 处理 *rest
            if ind == len(elts) - 1:
                # 如果是最后一个: e_target[i:]
                slice_str = f"{pre_str}[{count_sub}:]"
            else:
                # 如果在中间: e_target[i : i - len + 1] (即 e_target[i:-n])
                slice_str = f"{pre_str}[{count_sub}:{count_sub - len(elts) + 1}]"

            Map_var[ast.unparse(e_elt.value)] = get_Subscript_node(slice_str)

            # 星号之后，索引计数逻辑改变
            count_sub = ind - len(elts)  # 变为负数索引逻辑

        elif isinstance(e_elt, (ast.List, ast.Tuple)):
            # 递归处理嵌套解包
            trasnform_target(e_elt.elts, Map_var, f"{pre_str}[{count_sub}]")
            count_sub += 1

        else:
            # 普通变量
            slice_str = f"{pre_str}[{count_sub}]"
            Map_var[ast.unparse(e_elt)] = get_Subscript_node(slice_str)
            count_sub += 1


def transform_idiom_for_multi_tar(node):
    """
    将自动解包的 For 循环转换为手动解包。

    Returns:
        tuple: (success_flag, new_code_string)
    """
    try:
        # 1. 深拷贝节点，避免修改原树
        new_node = copy.deepcopy(node)
        target = new_node.target

        # 2. 确定不冲突的临时变量名
        all_names = {
            ast.unparse(n) for n in ast.walk(new_node) if isinstance(n, ast.Name)
        }
        replace_name = "e_target"
        while replace_name in all_names:
            replace_name = "e_" + replace_name

        # 3. 生成变量映射 Map_var {原变量: 临时变量下标}
        Map_var = dict()
        # 处理 target 是 Tuple/List 的情况
        if isinstance(target, (ast.List, ast.Tuple)):
            trasnform_target(target.elts, Map_var, replace_name)
        else:
            # 理论上这里的 target 必定是 List/Tuple，因为 Extractor 做了过滤
            return False, None

        # 4. 修改 AST
        # 4.1 将循环目标替换为临时变量: for (a,b) -> for e_target
        new_node.target = ast.Name(id=replace_name, ctx=ast.Store())

        # 4.2 在循环体头部插入解包赋值语句
        assign_stmts = []
        for k, v_node in Map_var.items():
            # 构造 k = e_target[i]
            assign_node = ast.Assign(
                targets=[ast.Name(id=k, ctx=ast.Store())],
                value=v_node,
                lineno=new_node.lineno,  # 尽量保留行号信息
            )
            assign_stmts.append(assign_node)

        # 将赋值语句插入 body 最前面
        new_node.body = assign_stmts + new_node.body

        return True, ast.unparse(new_node)

    except Exception:
        return False, None


# ==========================================
# 适配 ridiom_core 接口
# ==========================================


def transform(match: Match, config: Dict[str, Any]) -> str:
    """Transform tuple unpacking for to subscript access."""
    context = match.context
    for_node = context.get("for_node")

    if not for_node:
        return match.old_code

    success, new_code = transform_idiom_for_multi_tar(for_node)
    if success:
        return new_code
    else:
        return match.old_code
