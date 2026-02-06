# -*- coding: utf-8 -*-
"""
For Multiple Targets - Refactor transformation (fully self-contained).

Core logic copied from RefactoringIdioms/transform_c_s/transform_for_multiple_target.py
"""

import ast
import copy
import traceback
from typing import Dict, Any

from ...base_rule import Match


# ==========================================
# 核心转换逻辑 (从 transform_for_multiple_target.py 复制)
# ==========================================


def create_list(num):
    a = []
    for i in range(num - 1):
        if a:
            a[-1].append([])
        else:
            a.append([])
    return a


def get_subscript_num(node):
    if isinstance(node.value, ast.Subscript):
        return 1 + get_subscript_num(node.value)
    else:
        return 1


def get_subscript_index_not_last(node):
    if isinstance(node.value, ast.Subscript):
        a = [ast.unparse(node.slice)]
        a.extend(get_subscript_index_not_last(node.value))
        return a
    else:
        return [ast.unparse(node.slice)]


def build_node_list(node_list):
    pre_index = []
    new_node_list = []
    for ind, node in enumerate(node_list):
        cur_num = get_subscript_num(node)
        cur_index_list = get_subscript_index_not_last(node)[1:][::-1]
        last_ele = new_node_list
        list_num = cur_num - 1
        for ind, cur_ind in enumerate(cur_index_list):
            if len(pre_index) > ind:
                if cur_ind != pre_index[ind]:
                    break
                else:
                    list_num -= 1
                    last_ele = last_ele[-1]
        for i in range(list_num):
            last_ele.append([])
            last_ele = last_ele[-1]

        last_ele.append(node)
        pre_index = cur_index_list
    return new_node_list


def sort_node_list(node_list):
    map_dict = dict()
    node_str_list = []
    for node in node_list:
        node_str = ast.unparse(node)
        node_str_list.append(node_str)
        map_dict[node_str] = node
    map_dict = sorted(map_dict.items(), key=lambda kv: (len(kv[0]), kv[0]))
    new_node_list = []
    for e1, e2 in map_dict:
        new_node_list.append(e2)

    return build_node_list(new_node_list)


def build_pre_var_name(node):
    value = node.value
    var_name = ""
    if isinstance(value, ast.Subscript):
        var_name += build_pre_var_name(value)
    else:
        var_name = ast.unparse(value)
    return var_name


def get_beg(slice):
    if isinstance(slice, ast.Constant):
        return int(ast.unparse(slice)), int(ast.unparse(slice))
    elif isinstance(slice, ast.Slice):
        upper = int(ast.unparse(slice.upper)) if slice.upper else "len"
        lower = int(ast.unparse(slice.lower)) if slice.lower else 0
        beg = lower
        return beg, upper


def add_node_before_beg(node, beg):
    pre_node = None
    cur_beg, cur_end = get_beg(node.slice)
    if beg < cur_beg:
        pre_node_var_name = build_var(node).split("_")
        pre_node_var_name[-1] = str(cur_beg - 1)

        if cur_beg - beg > 1:
            pre_node = ast.Starred()
            pre_node.value = ast.Name("_".join(pre_node_var_name))
        else:
            pre_node = ast.Name("_".join(pre_node_var_name))
    if cur_end == "len":
        beg = cur_end
    else:
        beg = cur_end + 1
    return beg, cur_beg, pre_node


def get_slice(slice):
    if isinstance(slice, ast.Constant):
        return "_" + ast.unparse(slice)
    elif isinstance(slice, ast.Slice):
        upper = ast.unparse(slice.upper) if slice.upper else "len"
        lower = ast.unparse(slice.lower) if slice.lower else "0"
        step = ast.unparse(slice.step) if slice.step else "1"
        return "_".join(["", lower, step, upper])
    else:
        return ""


def build_var(node):
    slice = node.slice
    value = node.value
    var_name = ""
    if isinstance(value, ast.Subscript):
        var_name += build_var(value)
        var_name += get_slice(slice)
    else:
        var_name = ast.unparse(value) + get_slice(slice)
    return var_name


def add_cur_node(node):
    slice = node.slice
    var_name = build_var(node)
    if isinstance(slice, ast.Slice):
        var = ast.Starred()
        var.value = ast.Name(var_name)
    else:
        var = ast.Name(var_name)
    return var


def connect_slice_name(node):
    if isinstance(node, ast.Subscript):
        return [node] + connect_slice_name(node.value)
    else:
        return []


def get_first_node(node):
    if isinstance(node, list):
        return get_first_node(node[0])
    else:
        return node


def do_transform(node_list, new_list, depth, Map_var=None):
    beg = 0
    last_node = None
    cannot_trans_list = []
    star_count = 0
    for node in node_list:
        if isinstance(node, list):
            first_node = get_first_node(node)

            cur_node = connect_slice_name(first_node)[::-1][depth - 1]
            beg, cur_beg, pre_node = add_node_before_beg(cur_node, beg)

            if pre_node:
                if isinstance(pre_node, ast.Starred):
                    star_count += 1
                new_list.append(pre_node)
            new_list_2 = []
            the_cur_star_count = do_transform(node, new_list_2, depth + 1, Map_var)
            if the_cur_star_count > 1:
                return the_cur_star_count
            new_list.append(new_list_2)
        else:
            beg, cur_beg, pre_node = add_node_before_beg(node, beg)
            if pre_node:
                if isinstance(pre_node, ast.Starred):
                    star_count += 1
                new_list.append(pre_node)
            cur_node = add_cur_node(node)
            Map_var[ast.unparse(node)] = cur_node

            new_list.append(cur_node)
    if beg != "len":
        fir_node = get_first_node(node_list[0])
        end_node = connect_slice_name(fir_node)[::-1][depth - 1]
        var_name = build_var(end_node).split("_")
        var_name[-1] = "len"
        last_node = ast.Starred()
        last_node.value = ast.Name("_".join(var_name))
        star_count += 1
        new_list.append(last_node)
    return star_count


def build_elts(new_node_list, tuple_list):
    for node in new_node_list:
        if isinstance(node, list):
            tuple = ast.Tuple()
            tuple.elts = []
            build_elts(node, tuple.elts)
            tuple_list.append(tuple)
        else:
            tuple_list.append(node)


class RewriteName(ast.NodeTransformer):
    def __init__(self, Map_var):
        self.Map_var = Map_var

    def generic_visit(self, node):
        if ast.unparse(node) in self.Map_var:
            return ast.Expr(self.Map_var[ast.unparse(node)])

        for ind_field, k in enumerate(node._fields):
            try:
                v = getattr(node, k)
                if isinstance(v, ast.AST):
                    if v._fields:
                        setattr(node, k, self.generic_visit(v))
                    pass
                elif isinstance(v, list):
                    for ind, e in enumerate(v):
                        if hasattr(e, "_fields"):
                            v[ind] = self.generic_visit(e)
                    setattr(node, k, v)
            except:
                continue
        return node


def transform_for_node_var_unpack(for_node, node_list, Map_var):
    try:
        node_list = sort_node_list(node_list)
        new_node_list = []

        star_count = do_transform(node_list, new_node_list, 1, Map_var)
        if star_count > 1:
            return None
        tuple = ast.Tuple()
        tuple.elts = []
        build_elts(new_node_list, tuple.elts)
        for_node.target = tuple
        new_tree = RewriteName(Map_var).visit(for_node)
        return new_tree
    except:
        traceback.print_exc()
        return None


# ==========================================
# 适配 ridiom_core 接口
# ==========================================


def transform(match: Match, config: Dict[str, Any]) -> str:
    """Transform for loop to use tuple unpacking."""
    context = match.context
    for_node = context["for_node"]
    var_list = context["var_list"]

    Map_var = dict()
    node_copy = copy.deepcopy(for_node)
    new_code = transform_for_node_var_unpack(node_copy, var_list, Map_var)

    if new_code:
        return ast.unparse(new_code)
    else:
        return match.old_code
