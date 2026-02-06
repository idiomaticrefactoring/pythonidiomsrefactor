# -*- coding: utf-8 -*-
"""
Chain Comparison - Refactor transformation (fully self-contained).

Core logic copied from RefactoringIdioms/transform_c_s/transform_chained_cs.py
"""

import ast
import copy
from typing import Dict, Any

from ...base_rule import Match


# ==========================================
# 核心转换逻辑 (从 transform_chained_cs.py 复制)
# ==========================================


def get_pos(ele, one_var):
    """判断公共变量在比较式中的位置（左还是右）"""
    if one_var[0] == ele:
        return "l"
    else:
        return "r"


def merge(node1, node2):
    """合并两个比较节点：node1.ops + node2.ops"""
    ops = node2.ops
    comparator = node2.comparators
    for op, e in zip(ops, comparator):
        node1.ops.append(op)
        node1.comparators.append(e)
    return ast.unparse(node1)


def change_compare_node(node1):
    """翻转比较节点：a > b  -->  b < a"""
    new_node = copy.deepcopy(node1)
    # 交换左右
    new_node.left = node1.comparators[-1]
    new_node.comparators = node1.comparators[::-1][1:]
    new_node.comparators.append(node1.left)

    # 反转操作符
    for ind, op in enumerate(node1.ops[::-1]):
        if isinstance(op, ast.Gt):
            new_node.ops[ind] = ast.Lt()
        elif isinstance(op, ast.Lt):
            new_node.ops[ind] = ast.Gt()
        elif isinstance(op, ast.GtE):
            new_node.ops[ind] = ast.LtE()
        elif isinstance(op, ast.LtE):
            new_node.ops[ind] = ast.GtE()
        else:
            continue
    return new_node


def transform_left_right(pos1, pos2, node1, node2):
    """根据公共变量位置决定合并策略"""
    code = ""
    node1_still_flag = 0

    # 特殊处理：如果包含 None 检查 (is/is not)，通常不能随意交换位置
    if isinstance(node1.ops[0], (ast.Is, ast.IsNot, ast.Eq, ast.NotEq)):
        if pos1 == "l" and ast.unparse(node1.comparators[0]) == "None":
            node1.left, node1.comparators[0] = node1.comparators[0], node1.left
            pos1 = "r"
            node1_still_flag = 1

    elif isinstance(node2.ops[0], (ast.Is, ast.IsNot, ast.Eq, ast.NotEq)):
        if pos2 == "l" and ast.unparse(node2.comparators[0]) == "None":
            node2.left, node2.comparators[0] = node2.comparators[0], node2.left
            node1, node2 = node2, node1
            pos1, pos2 = "r", pos1
            node1_still_flag = 1

    # 策略表
    if pos1 == "r" and pos2 == "l":  # ... a < b AND b < c ...
        code = merge(node1, node2)

    elif pos1 == "l" and pos2 == "r":  # ... b > a AND b < c ...
        if node1_still_flag:
            return ""
        code = merge(node2, node1)  # 尝试交换顺序合并

    elif pos1 == "l" and pos2 == "l":  # ... b > a AND c > b ...
        if isinstance(node1.ops[-1], (ast.NotIn, ast.In)) and isinstance(
            node2.ops[-1], (ast.NotIn, ast.In)
        ):
            return ""
        elif isinstance(node1.ops[-1], (ast.NotIn, ast.In)):
            if node1_still_flag:
                return ""
            new_node = change_compare_node(node2)
            code = merge(new_node, node1)
        else:
            new_node = change_compare_node(node1)
            code = merge(new_node, node2)

    else:  # 右右: ... a < b AND c < b ...
        if isinstance(node1.ops[-1], (ast.NotIn, ast.In)) and isinstance(
            node2.ops[-1], (ast.NotIn, ast.In)
        ):
            return ""
        elif isinstance(node2.ops[-1], (ast.NotIn, ast.In)):
            if node1_still_flag:
                return ""
            new_node = change_compare_node(node1)
            code = merge(node2, new_node)
        else:
            new_node = change_compare_node(node2)
            code = merge(node1, new_node)

    return code


def transform_remain_code(remain_vars_list, ignore_ind_list):
    """重新组装剩余未合并的代码"""
    code = []
    flag = 0  # 0表示放在后面
    for ind, e in enumerate(remain_vars_list):
        if ind in ignore_ind_list:
            continue
        if ind == 0:
            flag = 1
        code.append(ast.unparse(e[1]))
    return " and ".join(code), flag


def transform_chained_comparison(node):
    """尝试对 BoolOp(And) 进行一次合并"""
    if not (isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And)):
        return 0, node

    vars_list = []
    values = node.values
    other_code = []

    for value in values:
        if isinstance(value, ast.Compare):
            left = value.left
            comparator = value.comparators[-1]
            vars = [[ast.unparse(left), ast.unparse(comparator)], value]
            vars_list.append(vars)

        else:
            other_code.append(ast.unparse(value))

    other_code_str = " and ".join(other_code) if other_code else ""
    remain_vars_list = copy.deepcopy(vars_list)

    # 两两比较寻找合并机会
    for ind, one_var in enumerate(vars_list):
        for ind_next in range(ind + 1, len(vars_list)):
            another_var = vars_list[ind_next]

            # 检查是否有公共变量
            common = set(one_var[0]) & set(another_var[0])
            if common:
                ele = list(common)[0]
                one_pos = get_pos(ele, one_var[0])
                another_pos = get_pos(ele, another_var[0])

                transform_code = transform_left_right(
                    one_pos, another_pos, one_var[1], another_var[1]
                )

                if not transform_code:
                    continue  # 无法合并，尝试下一对

                # 组装新代码
                remain_code, pos_flag = transform_remain_code(
                    remain_vars_list, [ind, ind_next]
                )

                if remain_code:
                    if pos_flag:
                        remain_code = remain_code + " and " + transform_code
                    else:
                        remain_code = transform_code + " and " + remain_code
                else:
                    remain_code = transform_code

                if other_code_str:
                    final_code_str = remain_code + " and " + other_code_str
                else:
                    final_code_str = remain_code

                for node in ast.walk(ast.parse(final_code_str)):
                    if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And):
                        return 1, node
                    elif isinstance(node, ast.Compare):
                        return 1, node

    return 0, node


# ==========================================
# 适配 ridiom_core 接口
# ==========================================


def transform(match: Match, config: Dict[str, Any]) -> str:
    """Transform chained comparison using inlined logic."""
    # 优先使用 detect 计算的结果
    if match.context.get("new_code"):
        return match.context["new_code"]

    node = match.node
    if not node:
        # 尝试从 old_code 解析
        try:
            node = ast.parse(match.old_code).body[0]
            if isinstance(node, ast.Expr):
                node = node.value
        except:
            return match.old_code

    max_operands = config.get("max-operands-to-refactor", False)

    # 迭代转换
    curr_node = copy.deepcopy(node)
    has_change = False

    while True:
        flag, new_node = transform_chained_comparison(curr_node)
        if not flag:
            break
        curr_node = new_node
        has_change = True

    if has_change:
        if max_operands and isinstance(max_operands, int):
            if isinstance(curr_node, ast.Compare):
                operand_count = len(curr_node.ops) + 1
                if operand_count > max_operands:
                    return match.old_code
        return ast.unparse(curr_node)

    return match.old_code
