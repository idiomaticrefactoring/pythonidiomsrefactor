# -*- coding: utf-8 -*-
"""
Truth Value Test - Explain transformation (fully self-contained).

Core logic copied from DeIdiom/transform_s_c/transform_truth_value_s_c.py
"""

import ast
import copy
from typing import Dict, Any

from ...base_rule import Match


# ==========================================
# 核心转换逻辑 (从 transform_truth_value_s_c.py 复制)
# ==========================================


def transform_idiom_truth_value(node):
    a = "def own_func_truth_test(var):\n\
    if var in [None, False, 0, 0.0, 0j, Decimal(0), Fraction(0, 1), '', (),[], {}, dict(), set(), range(0)]:\n\
        return False \n\
    elif hasattr(var,'__bool__'):\n\
        return bool(var)\n\
    elif hasattr(var, '__len__'):\n\
        return len(var)!=0\n\
    else:\n\
        return True"

    setup_code = "from decimal import Decimal\nfrom fractions import Fraction\n" + a

    new_code_str = ""

    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        # 处理 if not x:
        value = node.operand
        new_code_str = f"own_func_truth_test({ast.unparse(value)})==False"
    else:
        # 处理 if x:
        new_code_str = f"own_func_truth_test({ast.unparse(node)})==True"

    # 返回: (是否转换成功, 新代码字符串, 需要注入的头部代码)
    return True, new_code_str, setup_code


# ==========================================
# 适配 ridiom_core 接口
# ==========================================


def transform(match: Match, config: Dict[str, Any]) -> str:
    """Transform truth value test to explicit check."""
    context = match.context
    test_node = context.get("test_node")

    if not test_node:
        return match.old_code

    success, new_code, setup_code = transform_idiom_truth_value(test_node)
    if success:
        return new_code
    else:
        return match.old_code
