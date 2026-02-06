# -*- coding: utf-8 -*-
"""
For-Else - Explain transformation (fully self-contained).

Core logic copied from DeIdiom/transform_s_c/transform_for_else_s_c.py
"""

import ast
import copy
from typing import Dict, Any

from ...base_rule import Match


# ==========================================
# 核心转换逻辑 (从 transform_for_else_s_c.py 复制)
# ==========================================


class For_Else_C_S:
    def __init__(self):
        self.code_node_change = "flag_else=0"
        code_node_change = "flag_else=0"
        for if_node in ast.walk(ast.parse(code_node_change)):
            if isinstance(if_node, ast.Assign):
                self.flag_node_change = if_node
                break
        self.has_break = 0

    def iter_ele(self, body):
        index_list = []
        copy_body = copy.deepcopy(body)
        bias = 0
        for ind, child in enumerate(copy_body):
            if isinstance(child, (ast.For, ast.While)):
                if child.orelse:
                    self.traverse_cur_layer_no_body(body[ind + bias])
                continue
            if isinstance(child, ast.Break):
                self.has_break += 1
                body.insert(ind + bias, copy.deepcopy(self.flag_node_change))
                bias += 1
                pass
            else:
                self.traverse_cur_layer(body[ind + bias])

    def traverse_cur_layer_no_body(self, tree):
        if hasattr(tree, "orelse"):
            self.iter_ele(tree.orelse)
        if hasattr(tree, "handlers"):
            for handle in tree.handlers:
                self.iter_ele(handle.body)
        if hasattr(tree, "finalbody"):
            self.iter_ele(tree.finalbody)

    def traverse_cur_layer(self, tree):
        if hasattr(tree, "body"):
            self.iter_ele(tree.body)
        if hasattr(tree, "orelse"):
            self.iter_ele(tree.orelse)
        if hasattr(tree, "handlers"):
            for handle in tree.handlers:
                self.iter_ele(handle.body)
        if hasattr(tree, "finalbody"):
            self.iter_ele(tree.finalbody)


def transform_idiom_for_else(node):
    if not hasattr(node, "orelse") or not node.orelse:
        return False, None

    # 1. 深拷贝节点，避免修改原树
    new_node = copy.deepcopy(node)

    # 2. 提取并清空 orelse
    original_orelse = new_node.orelse
    new_node.orelse = []

    # 3. 注入 flag 逻辑
    for_else_visitor = For_Else_C_S()
    for_else_visitor.traverse_cur_layer(new_node)
    has_break = for_else_visitor.has_break

    # 4. 生成新代码字符串
    # 情况 A: 循环体中有 break (需要 flag 机制)
    if has_break:
        # Step 4.1: 初始化语句
        init_code = "flag_else = 1"

        # Step 4.2: 构造 if flag_else: ...
        if_wrapper_code = "if flag_else:\n    pass"
        if_node = ast.parse(if_wrapper_code).body[0]
        if_node.body = original_orelse  # 将原 else 内容放入 if 块

        # Step 4.3: 拼接完整代码
        complete_code = f"{init_code}\n{ast.unparse(new_node)}\n{ast.unparse(if_node)}"
        return True, complete_code

    # 情况 B: 循环体中没有 break (else 块总是执行)
    else:
        # 直接把 else 块的内容拼接到循环后面
        else_block_str = "\n".join([ast.unparse(stmt) for stmt in original_orelse])
        complete_code = f"{ast.unparse(new_node)}\n{else_block_str}"
        return True, complete_code


# ==========================================
# 适配 ridiom_core 接口
# ==========================================


def transform(match: Match, config: Dict[str, Any]) -> str:
    """Transform for-else to flag+for+if pattern."""
    context = match.context
    for_node = context.get("for_node")

    if not for_node:
        return match.old_code

    success, new_code = transform_idiom_for_else(for_node)
    if success:
        return new_code
    else:
        return match.old_code
