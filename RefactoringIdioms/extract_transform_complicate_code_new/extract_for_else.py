import sys
import ast
import os
import copy
import traceback

# ==========================================
# 路径修复
# ==========================================
current_file_path = os.path.abspath(__file__)
# extract_transform... -> RefactoringIdioms -> Root
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
if project_root not in sys.path:
    sys.path.append(project_root)

from RefactoringIdioms.extract_simp_cmpl_data import ast_util
from RefactoringIdioms.extract_simp_cmpl_data.extract_compli_truth_value_test_code import decide_compare_complicate_truth_value
from RefactoringIdioms.transform_c_s.transform_truth_value_test_compli_to_simple import transform_c_s_truth_value_test

'''
这里在遍历的时候需要记录下 变量T的读写
广度优先遍历
input: 代码片段
对于当前层
if 是赋值语句 (记录 左边的write写的变量T)
    if 后面节点是 for节点
        if for节点的下一个节点是if 语句，其中test中存在T变量
            获得for节点的body
            if exist 涉及T变量的赋值语句
               后面节点是否存在 break节点
    else:
       判断是否T有读操作()
'''

class Analyzer(ast.NodeVisitor):
    def __init__(self,class_name="NULL"):
        self.func_def_list = []
        self.class_name = class_name
    def visit_FunctionDef(self, node):
        self.func_def_list.append([node, self.class_name])

    def visit_ClassDef(self, node):
        class_ana=Analyzer(node.name)
        for stmt in node.body:
            class_ana.visit(stmt)
        self.func_def_list.extend(class_ana.func_def_list)
    
    def visit_If(self, node: ast.If):
        if ast.unparse(node.test) == "__name__ == '__main__'":
            self.func_def_list.append([node,"NULL"])


def get_intersect_vars(assign_list_in_for, vars_if_after_for):
    intersect_flag = 0
    intersect_infor = []

    for ind, node in enumerate(assign_list_in_for):
        if isinstance(node, (ast.Assign,ast.AnnAssign)):
            vars_assign_one = []
            intersect_vars = set([])
            targets=node.targets if isinstance(node,ast.Assign) else [node.target]
            for target in targets:
                vars_assign_one.append(ast.unparse(target))
            intersect_vars |= set(vars_assign_one) & set(vars_if_after_for)
            if intersect_vars:
                intersect_flag = 1
                intersect_infor.append([node.lineno, node, intersect_vars])

    return intersect_flag, intersect_infor


def whether_is_break(node, if_vars_list):
    break_flag = 0
    if isinstance(node, (ast.For, ast.While)):
        return 0
    elif isinstance(node, ast.Break):
        return 1
    elif isinstance(node, ast.Assign):
        pass
    elif isinstance(node, ast.If):
        pass
    else:
        for e in ast.iter_child_nodes(node):
            break_flag = break_flag or whether_is_break(e, if_vars_list)
    return break_flag


def whether_contain_break_and_const_assign(node, assign_list_in_for, if_list_in_for,break_list_in_for):
    break_flag = 0
    assign_list = []
    if hasattr(node, "body"):
        for ind, e in enumerate(node.body):
            if isinstance(e, ast.Break):
                    break_list_in_for.append(e)
                    break_flag=1
                    if_list_in_for.append(node)
                    assign_list_in_for.append(assign_list)
            elif isinstance(e, (ast.Assign,ast.AnnAssign,ast.AugAssign)):
                assign_list.append(e)
            elif isinstance(e, (ast.For, ast.While,ast.AsyncFor)):
                continue
            else:
                break_flag = whether_contain_break_and_const_assign(e, assign_list_in_for, if_list_in_for,break_list_in_for) or break_flag
    if hasattr(node,"orelse"):
        for e in node.orelse:
            if isinstance(e, ast.Break):
                    break_list_in_for.append(e)
                    break_flag=1
                    if_list_in_for.append(node)
                    assign_list_in_for.append(assign_list)
            elif isinstance(e, (ast.Assign,ast.AnnAssign,ast.AugAssign)):
                assign_list.append(e)
            elif isinstance(e, (ast.For, ast.While,ast.AsyncFor)):
                continue
            else:
                break_flag = whether_contain_break_and_const_assign(e, assign_list_in_for, if_list_in_for,break_list_in_for) or break_flag

    return break_flag


def visit_vars(target, list_vars):
    if isinstance(target, (ast.Name, ast.Subscript, ast.Attribute)):
        list_vars.append(ast.unparse(target))
    else:
        for e in ast.iter_child_nodes(target):
            visit_vars(e, list_vars)


def whether_if_and_contain_var(node):
    flag_if_var = 0
    if_vars_list = None
    if isinstance(node, ast.If):
        flag_if_var = 1
        if_vars_list = node
        return flag_if_var, if_vars_list
    else:
        return flag_if_var, if_vars_list


def transform_truth_value_test(test):
    if isinstance(test, ast.Compare):
        if decide_compare_complicate_truth_value(test):
            return transform_c_s_truth_value_test(test)
    return test


def is_same_two_if_test(test_1, test_2):
    def is_same_ops(op1, op2):
        if isinstance(op1, (ast.Eq, ast.Is)) and isinstance(op2, (ast.Eq, ast.Is)):
            return 1
        elif isinstance(op2, (ast.NotEq, ast.IsNot)) and isinstance(op1, (ast.NotEq, ast.IsNot)):
            return 1
        elif isinstance(op1, (ast.Lt)) and isinstance(op2, (ast.Lt)):
            return 1
        elif isinstance(op1, (ast.LtE)) and isinstance(op2, (ast.LtE)):
            return 1
        elif isinstance(op1, (ast.Gt)) and isinstance(op2, (ast.Gt)):
            return 1
        elif isinstance(op1, (ast.GtE)) and isinstance(op2, (ast.GtE)):
            return 1
        return 0

    test_1 = transform_truth_value_test(test_1)
    test_2 = transform_truth_value_test(test_2)
    if isinstance(test_1, ast.Compare) and isinstance(test_2, ast.Compare):
        op1 = test_1.ops[0]
        operators_1 = set([ast.unparse(test_1.left), ast.unparse(test_1.comparators[0])])
        op2 = test_2.ops[0]
        operators_2 = set([ast.unparse(test_2.left), ast.unparse(test_2.comparators[0])])
        if is_same_ops(op1, op2) and operators_1 == operators_2:
            return 1
        pass
    else:
        test_1_str = ast.unparse(test_1)
        test_2_str = ast.unparse(test_2)
        if test_1_str == test_2_str:
            return 1
    return 0


def is_differ_two_if_test(test_1, test_2):
    def is_differ_ops(op1, op2):
        if isinstance(op1, (ast.Eq, ast.Is)) and isinstance(op2, (ast.NotEq, ast.IsNot)):
            return 1
        elif isinstance(op2, (ast.Eq, ast.Is)) and isinstance(op1, (ast.NotEq, ast.IsNot)):
            return 1
        elif isinstance(op1, (ast.Lt)) and isinstance(op2, (ast.GtE)):
            return 1
        elif isinstance(op1, (ast.LtE)) and isinstance(op2, (ast.Gt)):
            return 1
        elif isinstance(op1, (ast.Gt)) and isinstance(op2, (ast.LtE)):
            return 1
        elif isinstance(op1, (ast.GtE)) and isinstance(op2, (ast.Lt)):
            return 1
        return 0

    test_1 = transform_truth_value_test(test_1)
    test_2 = transform_truth_value_test(test_2)

    if isinstance(test_1, ast.Compare) and isinstance(test_2, ast.Compare):
        if len(test_1.ops) > 1 and len(test_2.ops) > 1:
            return 0
        op1 = test_1.ops[0]
        operators_1 = set([ast.unparse(test_1.left), ast.unparse(test_1.comparators[0])])
        op2 = test_2.ops[0]
        operators_2 = set([ast.unparse(test_2.left), ast.unparse(test_2.comparators[0])])
        if is_differ_ops(op1, op2) and operators_1 == operators_2:
            return 1
    else:
        test_1_str = ast.unparse(test_1)
        test_2_str = ast.unparse(test_2)
        if "not " + test_1_str == test_2_str or test_1_str == "not " + test_2_str:
            return 1

    return 0


def is_same_ass_init_if_test(assign, test):
    count = 0
    targets = assign.targets if isinstance(assign, ast.Assign) else [assign.target]
    value = assign.value
    for tar in targets:
        count += ast_util.get_basic_count(tar)
    if count > 1:
        return 0
    count = ast_util.get_basic_count(value)
    if count > 1:
        return 0
    tree = ast.parse(ast.unparse(targets[0]) + "==" + ast.unparse(value))
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            return is_same_two_if_test(node, test)
    return 0


def is_differ_ass_again_if_test(assign, test):
    count = 0
    targets = assign.targets if isinstance(assign, ast.Assign) else [assign.target]
    value = assign.value
    for tar in targets:
        count += ast_util.get_basic_count(tar)
    if count > 1:
        return 0
    count = ast_util.get_basic_count(value)
    if count > 1:
        return 0
    tree = ast.parse(ast.unparse(targets[0]) + "==" + ast.unparse(value))

    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            return is_differ_two_if_test(node, test)
    return 0

def modify_normalize(tree, child, if_varnode, if_list_in_for, orelse_node,stmts_insert_break):
    child.orelse = orelse_node
    len_body = len(if_list_in_for[0].body)
    for ind_e_if, e_if in enumerate(stmts_insert_break):
        if_list_in_for[0].body.insert(len_body - 1 + ind_e_if, e_if)
    tree.body.remove(if_varnode)

def modify(tree, child, if_varnode, if_list_in_for, flag=0):
    if flag == 0:
        child.orelse = if_varnode.orelse
        len_body = len(if_list_in_for.body)

        for ind_e_if, e_if in enumerate(if_varnode.body):
            if isinstance(e_if, ast.Break):
                return 1
            if_list_in_for.body.insert(len_body - 1 + ind_e_if, e_if)
        if if_varnode in tree.body:
            tree.body.remove(if_varnode)

    elif flag == 1:
        child.orelse = if_varnode.body
        len_body = len(if_list_in_for.body)
        
        if if_varnode.orelse:
            for ind_e_if, e_if in enumerate(if_varnode.orelse):
                if isinstance(e_if, ast.Continue):
                    return 1
                if isinstance(e_if,ast.Break):
                    return 1
                if_list_in_for.body.insert(len_body - 1 + ind_e_if, e_if)
        if if_varnode in tree.body:
            tree.body.remove(if_varnode)


def remove_assign(tree_copy, child_copy, tree, child, if_vars_list, intersect_infor_ass_list_in_for,
                      intersect_infor_ass_init,ind):
    init_ass_remove=0
    if 1:
        count = 0
        for node in ast.walk(child):
            if ast.unparse(node) == if_vars_list[0]:
                count += 1
                if count > len(intersect_infor_ass_list_in_for):
                    break
        else:
            # print("come remove_assign: code1 behind should not occur var")
            count = 0
            for body in tree.body[ind + 1:]:
                for node in ast.walk(body):
                    if ast.unparse(node) == if_vars_list[0]:
                        count += 1
                        if count > 1:
                            break
                if count > 1:
                    break
            else:
                for e in ast.walk(child_copy):
                    if hasattr(e, "body") and isinstance(e.body,list):
                        for e_each in e.body:
                            for ass_each_list in intersect_infor_ass_list_in_for:
                                if e_each == ass_each_list[0][1]:
                                    e.body.remove(e_each)
                    if hasattr(e,"orelse"):
                        for e_e in e.orelse:
                            if e_e == ass_each_list[0][1]:
                                e.orelse.remove(e_e)
                                break

                for e in ast.walk(tree_copy):
                    if hasattr(e, "body")  and isinstance(e.body,list):
                        for node in e.body:
                            if ast.unparse(intersect_infor_ass_init[0][1]) == ast.unparse(node):
                                e.body.remove(node)
                                init_ass_remove=1
                                break
                        else:
                            continue
                        break
                    if hasattr(e, "orelse"):
                            for e_e in e.orelse:
                                if e_e == ass_each_list[0][1]:
                                    e.orelse.remove(e_e)
                                    break
    return init_ass_remove

def traverse_cur_layer(tree, code_list, ass_init_list):
    if hasattr(tree, "body"):
        for ind,child in enumerate(tree.body):
            tree_copy = copy.deepcopy(tree)
            child_copy = tree_copy.body[ind]
            if isinstance(child, (ast.For, ast.While)):
                if child.orelse:
                    traverse_cur_layer(child, code_list, ass_init_list)
                    continue
                if ind + 1 >= len(tree.body):
                    traverse_cur_layer(child, code_list, ass_init_list)
                    continue
                if_vars_list, intersect_infor, assign_list_in_for = [], [], []
                next_child = tree_copy.body[ind + 1]

                flag_if_var, if_varnode = whether_if_and_contain_var(next_child)

                if not if_varnode or (isinstance(if_varnode,ast.BoolOp) and isinstance(if_varnode.op,(ast.And,ast.Or))):
                    traverse_cur_layer(child, code_list, ass_init_list)
                    continue
                
                all_assign_list_in_for = []
                if_list_in_for = []
                break_list_in_for=[]
                break_flag = whether_contain_break_and_const_assign(child_copy, all_assign_list_in_for, if_list_in_for,break_list_in_for)
                flag_simplify=1
                assign_flag=1
                if break_flag:
                    intersect_infor_ass_list_in_for=[]
                    visit_vars(if_varnode.test, if_vars_list)
                    intersect_flag_ass_init, intersect_infor_ass_init = get_intersect_vars(ass_init_list, if_vars_list)
                    
                    if not intersect_flag_ass_init or len(intersect_infor_ass_init[-1][-1]) > 1:
                        flag_simplify = 0
                        break
                    else:
                        for ind_chi, ass_child in enumerate(tree.body[:ind]):
                            if isinstance(ass_child,(ast.Assign,ast.AnnAssign)):
                                continue
                            else:
                                for ass_child_child in ast.walk(ass_child):
                                    if isinstance(ass_child_child,(ast.Assign,ast.AnnAssign,ast.AugAssign)):
                                        for ass_init_node in intersect_infor_ass_init:
                                            if ass_child_child.lineno == ass_init_node[1].lineno:
                                                flag_simplify=0
                                                break
                                        else:
                                            continue
                                        flag_simplify = 0
                                        break
                                else:
                                    continue
                                flag_simplify = 0
                                break

                        if not flag_simplify:
                            traverse_cur_layer(child, code_list, ass_init_list)
                            # print("init ass is not valid")
                            continue

                        if is_same_ass_init_if_test(intersect_infor_ass_init[-1][1], if_varnode.test):
                            modify(tree_copy, child_copy, if_varnode, if_list_each, 1)
                            flag_simplify = 1
                            assign_flag = 1
                        elif if_varnode.orelse and is_differ_ass_again_if_test(intersect_infor_ass_init[-1][1],
                                                                               if_varnode.test):
                            for if_list_each in if_list_in_for:
                                modify(tree_copy, child_copy, if_varnode, if_list_each, 0)
                            flag_simplify = 1
                            assign_flag = 1
                        else:
                            flag_simplify = 0

                    if not flag_simplify:
                        traverse_cur_layer(child, code_list, ass_init_list)
                        continue
                    
                    for ind_test,assign_list_in_for in enumerate(all_assign_list_in_for):
                        if_list_each=if_list_in_for[ind_test]
                        flag_inn, info_inn = get_intersect_vars(assign_list_in_for, if_vars_list)

                        if flag_inn:
                            intersect_infor_ass_list_in_for.append(info_inn)
                            for line_no,ass,inter_var in info_inn:
                                if is_differ_ass_again_if_test(ass, if_varnode.test):
                                    body_break_flag=modify(tree_copy, child_copy, if_varnode, if_list_each, 1)
                                    if body_break_flag:
                                        flag_simplify = 0
                                    break
                                elif if_varnode.orelse and is_same_ass_init_if_test(ass, if_varnode.test):
                                    body_break_flag=modify(tree_copy, child_copy, if_varnode, if_list_each, 0)
                                    if body_break_flag:
                                        flag_simplify = 0
                                    break
                            else:
                                flag_simplify = 0
                                break
                        else:
                            if hasattr(if_list_each, "test"):
                                if is_differ_two_if_test(if_varnode.test, if_list_each.test):
                                    body_break_flag=modify(tree_copy, child_copy, if_varnode, if_list_each, 1)
                                    if body_break_flag:
                                        flag_simplify = 0
                                    assign_flag = 0
                                elif if_varnode.orelse:
                                    if if_list_each.test and is_same_two_if_test(
                                        if_varnode.test, if_list_each.test):
                                        body_break_flag=modify(tree_copy, child_copy, if_varnode, if_list_each, 0)
                                        if body_break_flag:
                                            flag_simplify = 0
                                        assign_flag=0
                                        pass
                                    else:
                                        flag_simplify = 0
                                        break
                                else:
                                    flag_simplify = 0
                                    break
                            else:
                                flag_simplify = 0
                                break

                    init_ass_remove_flag=0
                    if flag_simplify and assign_flag:
                            init_ass_remove_flag=remove_assign(tree_copy,child_copy,tree,child,if_vars_list,intersect_infor_ass_list_in_for,intersect_infor_ass_init,ind)

                    if flag_simplify:
                        code_list.append([tree,tree_copy,break_list_in_for,child,child_copy,intersect_infor_ass_init[0][1],if_varnode,init_ass_remove_flag])

            else:
                for e_chi in ast.walk(child_copy):
                    if isinstance(e_chi, (ast.Assign,ast.AnnAssign)) and child_copy not in ass_init_list  :
                        ass_init_list.append(child_copy)

            traverse_cur_layer(child, code_list, ass_init_list)

def transform_for_else_code(content, config=None):
    if config is None:
        config = {}
    
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
            new_code_list = []
            ass_init_list = []
            traverse_cur_layer(tree, new_code_list, ass_init_list)
            
            for code in new_code_list:
                line_list=[[code[5].lineno, code[5].end_lineno]]
                line_list.append([code[3].lineno, code[3].end_lineno])
                line_list.append([code[6].lineno, code[6].end_lineno])
                
                old_code = ast.unparse(code[5]) + "\n" + ast.unparse(code[3]) + "\n" + ast.unparse(code[6])
                
                simple_code = ast.unparse(code[4]) if code[7] else ast.unparse(code[5])+"\n"+ast.unparse(code[4])
                
                code_pair_list.append([class_name, me_name, old_code, simple_code, line_list])

        return code_pair_list

    except:
        # traceback.print_exc()
        return code_pair_list

if __name__ == '__main__':
    code = '''
def main():
    found = False
    for a in action_filter:
        if action.startswith(a):
            found = True
            break
    if not found:
        continue
'''
    print(transform_for_else_code(code))