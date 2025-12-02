import ast
import tokenize
import sys
import os
import traceback
from io import BytesIO

# ==========================================
# 路径修复
# ==========================================
current_file_path = os.path.abspath(__file__)
# extract_transform... -> RefactoringIdioms -> Root
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
if project_root not in sys.path:
    sys.path.append(project_root)

from RefactoringIdioms.extract_simp_cmpl_data import ast_util
from RefactoringIdioms.transform_c_s import transform_multiple_assign

'''
input: 代码片段 code1
'''
def get_tokens(node):
    s = ast.unparse(node)
    g = tokenize.tokenize(BytesIO(s.encode('utf-8')).readline)  # tokenize the string
    tokens=set([])
    for toknum, child, _, _, _ in g:
        tokens.add(child)
    return tokens

class Visit_vars(ast.NodeVisitor):
    def __init__(self):
        self.vars = []
    def visit_Name(self, node) :
        self.vars.append(node)
    def visit_Attribute(self, node):
        self.vars.append(node)
    def visit_Subscript(self, node):
        self.vars.append(node)

def visit_single_vars(target, list_vars):
    # print(">>>>>>>target: ",target.__dict__)
    if isinstance(target, (ast.Name)):
        list_vars.append(ast.unparse(target))
    elif  isinstance(target, ast.Subscript):
        list_vars.append(ast.unparse(target))
        if not isinstance(target.value,ast.Subscript):
            visit_single_vars(target.value, list_vars)
    elif isinstance(target,ast.Attribute):
        # print("attr: ",ast.unparse(target))
        list_vars.append(ast.unparse(target))
        visit_single_vars(target.value, list_vars)
    else:
        # print("visit_single_vars else node: ", ast.unparse(target))
        for e in ast.iter_child_nodes(target):
            # print("visit_single_vars e: ",e,ast.unparse(e))
            visit_single_vars(e, list_vars)

def is_occur_body(same_value_var,body_list):
    for body in body_list:
        for e in ast.walk(body):
            if ast.unparse(e)==same_value_var:
                return 1
    return 0

def is_not_intersect_value_also_in_left(all_target_list, value):
    for tar in all_target_list:
        if tar == value:
            return 0
    return 1

def once_again(ass):
    a=[ass]
    target = ass.targets[0]
    value=ass.value
    write_vars = []
    visit_single_vars(target, write_vars)
    all_write_vars = [write_vars]
    all_target_list = [ast.unparse(target)]
    all_value_list=[ast.unparse(value)]
    return a,all_write_vars, all_target_list,all_value_list

def split_assignments_overlap_read_write(all_assign_list, all_body_list):
    def is_depend(pre_tar, next_tar):
        pre_tar_str = ast.unparse(pre_tar)
        for node in ast.walk(next_tar):
            if pre_tar_str == ast.unparse(node):
                return 1
        return 0

    all_assign_left_no_overlap_list = []
    for ind_ass, assign_list in enumerate(all_assign_list):
        body_list = all_body_list[ind_ass]
        a = [assign_list[0]]
        for ind_e, ass in enumerate(assign_list[1:]):
            next_tar = ass.targets[0]
            for reverse_ind_e2, pre_ass in enumerate(a[::-1]):
                ind_e2=len(a)-reverse_ind_e2-1
                pre_tar = pre_ass.targets[0]

                if is_depend(pre_tar, next_tar):
                    if len(a[:ind_e2+1]) > 1:
                        all_assign_left_no_overlap_list.append([a[:ind_e2+1], body_list])
                    a = a[ind_e2+1:]
                    a.append(ass)
                    break
            else:
                a.append(ass)
        if len(a) > 1:
            all_assign_left_no_overlap_list.append([a, body_list])

    real_assign_list = []
    for ind_ass, (assign_list, body_list) in enumerate(all_assign_left_no_overlap_list):
        a = [assign_list[0]]
        overlap_flag=0
        for ind_e, ass in enumerate(assign_list[1:]):
            next_value = ass.value
            for reverse_ind_e2, pre_ass in enumerate(a[::-1]):
                ind_e2=len(a)-reverse_ind_e2-1
                pre_tar = pre_ass.targets[0]
                pre_value = pre_ass.value

                def intersect_var(pre_tar, next_value):
                    for node in ast.walk(next_value):
                        if ast.unparse(pre_tar)==ast.unparse(node):
                            return 1
                    for node in ast.walk(pre_tar):
                        if ast.unparse(node)==ast.unparse(next_value):
                            return 1
                    return 0

                def value_is_in_target_list(pre_value, ass_list):
                    for ass in ass_list:
                        tar = ass.targets[0]
                        if ast.unparse(pre_value) == ast.unparse(tar):
                            return 1
                    return 0

                if intersect_var(pre_tar, next_value):
                    if not is_depend(pre_tar, next_value) or is_occur_body(ast.unparse(pre_tar), body_list) or not value_is_in_target_list(pre_value, a[ind_e2 + 1:]):
                        if len(a[:ind_e2+1]) > 1 and overlap_flag:
                            real_assign_list.append(a)
                        a = a[ind_e2+1:]
                        a.append(ass)
                        if ind_e!=len(assign_list[1:])-1:
                                overlap_flag=0
                        break
                    else:
                        overlap_flag = 1
            else:
                a.append(ass)

        if len(a) > 1 and  overlap_flag:
            real_assign_list.append(a)

    return real_assign_list

'''
左边不存在数据依赖，(a1,a2) a1没有出现在a2中
'''
def split_assignments(all_assign_list,all_body_list):
    def is_depend(pre_tar, next_tar):
        pre_tar_str = ast.unparse(pre_tar)
        for node in ast.walk(next_tar):
            if pre_tar_str == ast.unparse(node):
                return 1
        return 0
    
    def is_depend_str(pre_tar_str, next_tar):
        for node in ast.walk(next_tar):
            if pre_tar_str == ast.unparse(node):
                return 1
        return 0

    all_assign_left_no_overlap_list = []
    for ind_ass, assign_list in enumerate(all_assign_list):
        body_list = all_body_list[ind_ass]
        a = [assign_list[0]]
        for ind_e, ass in enumerate(assign_list[1:]):
            next_tar = ass.targets[0]
            for reverse_ind_e2, pre_ass in enumerate(a[::-1]):
                ind_e2=len(a)-reverse_ind_e2-1
                pre_tar = pre_ass.targets[0]

                if is_depend(pre_tar, next_tar):
                    if len(a[:ind_e2+1]) > 1:
                        all_assign_left_no_overlap_list.append([a[:ind_e2+1], body_list])
                    a = a[ind_e2+1:]
                    a.append(ass)
                    break
            else:
                a.append(ass)
        if len(a) > 1:
            all_assign_left_no_overlap_list.append([a, body_list])

    real_assign_list = []
    for ind_ass, (assign_list, body_list) in enumerate(all_assign_left_no_overlap_list):
        a = [assign_list[0]]
        for ind_e, ass in enumerate(assign_list[1:]):
            next_value = ass.value
            for reverse_ind_e2, pre_ass in enumerate(a[::-1]):
                ind_e2=len(a)-reverse_ind_e2-1
                pre_tar = pre_ass.targets[0]
                pre_value = pre_ass.value

                def value_is_in_target_list(pre_value, ass_list):
                    for ass in ass_list:
                        tar = ass.targets[0]
                        if ast.unparse(pre_value) == ast.unparse(tar):
                            return 1
                    return 0
                
                def intersect_var(pre_tar, next_value):
                    pre_var_list=[]
                    for node in ast.walk(pre_tar):
                        pre_var_list.append(ast.unparse(node))
                    
                    def visit_vars(target, list_vars, pre_var_list, pre_tar):
                        if isinstance(target, (ast.Name)):
                            list_vars.append(ast.unparse(target))
                        elif isinstance(target, ast.Subscript):
                            list_vars.append(ast.unparse(target))
                            if not(isinstance(target,type(pre_tar)) and ast.unparse(target.value) in pre_var_list):
                                visit_vars(target.value, list_vars, pre_var_list, pre_tar)
                            visit_vars(target.slice, list_vars, pre_var_list, pre_tar)
                        elif isinstance(target, ast.Attribute):
                            list_vars.append(ast.unparse(target))
                            if not(isinstance(target, type(pre_tar)) and ast.unparse(target.value) in pre_var_list):
                                visit_vars(target.value, list_vars, pre_var_list, pre_tar)
                        elif isinstance(target, list):
                            for e in target:
                                visit_vars(e, list_vars, pre_var_list, pre_tar)
                        else:
                            for e in ast.iter_child_nodes(target):
                                visit_vars(e, list_vars, pre_var_list, pre_tar)
                        pass
                    
                    list_vars=[]
                    visit_vars(next_value, list_vars, pre_var_list, pre_tar)
                    if set(list_vars)&set(pre_var_list):
                        return 1
                    return 0

                if intersect_var(pre_tar, next_value) or intersect_var( next_value,pre_tar) :
                        if not (is_depend(pre_tar, next_value) and not is_occur_body(ast.unparse(pre_tar), body_list) and value_is_in_target_list(pre_value, a[ind_e2 + 1:])):
                            if len(a[:ind_e2+1]) > 1:
                                real_assign_list.append(a[:ind_e2+1])
                            a = a[ind_e2+1:]
                            a.append(ass)
                            break
            else:
                a.append(ass)

        if len(a) > 1:
            real_assign_list.append(a)
    return real_assign_list

def get_multiple_assign(tree):
    assign_list = []
    body_list = []
    for e_trr in ast.walk(tree):
        if hasattr(e_trr, "body") :
            body = e_trr.body
            if not isinstance(body,list):
                continue
            a = []
            for ind_node, node in enumerate(body):
                if isinstance(node, ast.Assign):
                    targets = node.targets
                    count = 0
                    for e in targets:
                        count += ast_util.get_basic_count(e)
                    if count > 1:
                        if len(a) > 1:
                            assign_list.append(a)
                            if ind_node + 1 <= len(body) - 1:
                                body_list.append(body[ind_node+1:])
                            else:
                                body_list.append([])
                        a = []
                        continue
                    else:
                        a.append(node)
                        if ind_node == len(body) - 1 and len(a) > 1:
                            assign_list.append(a)
                            body_list.append([])
                else:
                    if len(a) > 1:
                        assign_list.append(a)
                        if ind_node<=len(body) - 1:
                            body_list.append(body[ind_node:])
                        else:
                            body_list.append([])
                    a=[]
        if hasattr(e_trr, "orelse") :
            body = e_trr.orelse
            if not isinstance(body, list):
                continue
            a = []
            for ind_node, node in enumerate(body):
                if isinstance(node, ast.Assign):
                    targets = node.targets
                    count = 0
                    for e in targets:
                        count += ast_util.get_basic_count(e)
                    if count > 1:
                        if len(a) > 1:
                            assign_list.append(a)
                            if ind_node + 1 <= len(body) - 1:
                                body_list.append(body[ind_node + 1:])
                            else:
                                body_list.append([])
                        a = []
                        continue
                    else:
                        a.append(node)
                        if ind_node == len(body) - 1 and len(a) > 1:
                            assign_list.append(a)
                            body_list.append([])
                else:
                    if len(a) > 1:
                        assign_list.append(a)
                        if ind_node <= len(body) - 1:
                            body_list.append(body[ind_node:])
                        else:
                            body_list.append([])
                    a = []

    return assign_list,body_list

def transform_multiple_assign_code(content, config=None):
    if config is None:
        config = {}
    
    # 获取配置中的限制
    # 如果 max_assignments 为 False (默认), 则不限制; 为数字则限制最大数量
    max_assignments = config.get("max-assignments-to-refactor", False)

    code_pair_list = []
    try:
        file_tree = ast.parse(content)
        ana_py = ast_util.Fun_Analyzer()
        ana_py.visit(file_tree)

        for tree, class_name in ana_py.func_def_list:
            try:
                me_name=tree.name
            except:
                me_name=""
            all_assign_list, all_body_list = get_multiple_assign(tree)
            assign_list = split_assignments(all_assign_list, all_body_list)

            for ind_ass, each_assign_list in enumerate(assign_list):
                # 检查配置限制
                if isinstance(max_assignments, int) and max_assignments > 0:
                    if len(each_assign_list) > max_assignments:
                        continue

                each_assign_list_str = "\n".join([ast.unparse(e_ass) for e_ass in each_assign_list])
                line_list =[[e_ass.lineno, e_ass.end_lineno] for e_ass in each_assign_list]
                new_code = transform_multiple_assign.transform(each_assign_list)

                code_pair_list.append([class_name,me_name,each_assign_list_str, new_code,line_list])

        return code_pair_list

    except:
        # traceback.print_exc()
        return code_pair_list

if __name__ == '__main__':
    code = """
def main():
    a = 1
    b = 2
    c = 3
"""
    print(transform_multiple_assign_code(code))