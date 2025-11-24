import ast, os, copy
import sys
abs_path=os.path.abspath(os.path.dirname(__file__))

# abs_path=os.getcwd()
# print("abs_path: ",abs_path)
pack_path="/".join(abs_path.split("/")[:-1])
# print(pack_path)
sys.path.append(pack_path)

# import time
# from code1 import util
# from extract_simp_cmpl_data import ast_util
# from extract_simp_cmpl_data.extract_compli_truth_value_test_code import decide_compare_complicate_truth_value
# from code1.transform_c_s.transform_truth_value_test_compli_to_simple import transform_c_s_truth_value_test
import time
import util
from RefactoringIdioms.extract_simp_cmpl_data import  ast_util
from RefactoringIdioms.extract_simp_cmpl_data.extract_compli_truth_value_test_code import decide_compare_complicate_truth_value
from RefactoringIdioms.transform_c_s.transform_truth_value_test_compli_to_simple import transform_c_s_truth_value_test
from pathos.multiprocessing import ProcessingPool as newPool
import traceback
# from code1.extract_simp_cmpl_data import ast_util
# from code1.extract_simp_cmpl_data.extract_compli_truth_value_test_code import decide_compare_complicate_truth_value
# from pathos.multiprocessing import ProcessingPool as newPool
# from code1.transform_c_s.transform_truth_value_test_compli_to_simple import transform_c_s_truth_value_test

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


# def traverse_for_else_comp(node,dict_source_code,file_path=None):
#     if
#     if isinstance(node, ast.For):
#
#     pass
class Analyzer(ast.NodeVisitor):
    def __init__(self,class_name="NULL"):
        self.func_def_list = []
        self.class_name = class_name
    def visit_FunctionDef(self, node):
        self.func_def_list.append([node, self.class_name])

        # print("fun name: ", node.name)

    def visit_ClassDef(self, node):

        class_ana=Analyzer(node.name)
        for stmt in node.body:
            class_ana.visit(stmt)
        self.func_def_list.extend(class_ana.func_def_list)
        # print("class name: ",class_ana.class_name)
    #
    def visit_If(self, node: ast.If):
        if ast.unparse(node.test) == "__name__ == '__main__'":
            self.func_def_list.append([node,"NULL"])


def get_intersect_vars(assign_list_in_for, vars_if_after_for):
    intersect_flag = 0
    intersect_infor = []

    for ind, node in enumerate(assign_list_in_for):
        if isinstance(node, (ast.Assign,ast.AnnAssign)):
            # print("come assign node: ",node.targets[0].__dict__)
            vars_assign_one = []
            intersect_vars = set([])
            targets=node.targets if isinstance(node,ast.Assign) else [node.target]
            for target in targets:
                vars_assign_one.append(ast.unparse(target))
                # visit_vars(target, vars_assign_one)
            intersect_vars |= set(vars_assign_one) & set(vars_if_after_for)
            if intersect_vars:
                intersect_flag = 1
                intersect_infor.append([node.lineno, node, intersect_vars])

    return intersect_flag, intersect_infor


def whether_is_break(node, if_vars_list):
    # print("the node is: ", node,node.__dict__)
    break_flag = 0
    # if isinstance(node, list):
    #     print("come here")
    #     for e in node:
    #         break_flag=break_flag or whether_is_break(e)
    # else:
    if isinstance(node, (ast.For, ast.While)):
        return 0
    elif isinstance(node, ast.Break):
        return 1
    elif isinstance(node, ast.Assign):
        pass
    elif isinstance(node.ast.If):
        pass
    else:
        for e in ast.iter_child_nodes(node):
            break_flag = break_flag or whether_is_break(e)
    return break_flag


def whether_contain_break_and_const_assign(node, assign_list_in_for, if_list_in_for,break_list_in_for):
    # assign_list_in_for=[]
    # if_list_in_for=[]
    break_flag = 0
    assign_list = []
    if hasattr(node, "body"):
        # print(">>>>>>the node: ",ast.unparse(node))
        for ind, e in enumerate(node.body):

            if isinstance(e, ast.Break):
                    break_list_in_for.append(e)
                    break_flag=1

                    # if 1:#isinstance(node, ast.If):
                    if_list_in_for.append(node)
                    assign_list_in_for.append(assign_list)

                # break
            elif isinstance(e, (ast.Assign,ast.AnnAssign,ast.AugAssign)):
                assign_list.append(e)
            elif isinstance(e, (ast.For, ast.While,ast.AsyncFor)):
                continue
            else:
                # print(">>>>>>the ele: ", ast.unparse(e))
                break_flag = whether_contain_break_and_const_assign(e, assign_list_in_for, if_list_in_for,break_list_in_for) or break_flag

    return break_flag


def visit_vars(target, list_vars):
    # print(">>>>>>>target: ",target.__dict__)
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
        # visit_vars(node.test, if_vars_list)
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
    # print("is_same_two_if_test: ",ast.unparse(test_2),ast.unparse(test_1))
    if isinstance(test_1, ast.Compare) and isinstance(test_2, ast.Compare):
        op1 = test_1.ops[0]
        operators_1 = set([ast.unparse(test_1.left), ast.unparse(test_1.comparators[0])])
        op2 = test_2.ops[0]
        operators_2 = set([ast.unparse(test_2.left), ast.unparse(test_2.comparators[0])])
        # print("compare two ops: ",is_differ_ops(op1, op2))
        if is_same_ops(op1, op2) and operators_1 == operators_2:
            return 1
        pass
    else:
        test_1_str = ast.unparse(test_1)
        test_2_str = ast.unparse(test_2)
        if test_1_str == test_2_str or test_1_str == test_2_str:
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
        # print("compare: ",ast.unparse(test_1),ast.unparse(test_2))
        if len(test_1.ops) > 1 and len(test_2.ops) > 1:
            return 0
        op1 = test_1.ops[0]
        operators_1 = set([ast.unparse(test_1.left), ast.unparse(test_1.comparators[0])])
        op2 = test_2.ops[0]
        operators_2 = set([ast.unparse(test_2.left), ast.unparse(test_2.comparators[0])])
        # print("compare two ops: ",is_differ_ops(op1, op2))
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
    # targets = assign.targets
    value = assign.value
    for tar in targets:
        count += ast_util.get_basic_count(tar)
    if count > 1:
        return 0
    count = ast_util.get_basic_count(value)
    if count > 1:
        return 0
    tree = ast.parse(ast.unparse(targets[0]) + "==" + ast.unparse(value))
    new_test_ass = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            return is_same_two_if_test(node, test)

    return 0
    pass


def is_differ_ass_again_if_test(assign, test):
    count = 0
    targets = assign.targets if isinstance(assign, ast.Assign) else [assign.target]
    # targets = assign.targets
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
            # print("is_differ_ass_again_if_test: ",ast.unparse(node),ast.unparse(test))
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
            if_list_in_for.body.insert(len_body - 1 + ind_e_if, e_if)
        if if_varnode in tree.body:
            tree.body.remove(if_varnode)
    elif flag == 1:
        child.orelse = if_varnode.body
        len_body = len(if_list_in_for.body)

        if if_varnode.orelse:
            for ind_e_if, e_if in enumerate(if_varnode.orelse):
                if_list_in_for.body.insert(len_body - 1 + ind_e_if, e_if)
        if if_varnode in tree.body:
            tree.body.remove(if_varnode)

def remove_assign(tree_copy, child_copy, tree, child, if_vars_list, intersect_infor_ass_list_in_for,
                      intersect_infor_ass_init,ind):
    # print("come remove_assign: ",len(intersect_infor_ass_init))
    if 1:
        # print("len intersect_infor_ass_list_in_for: ",len(intersect_infor_ass_list_in_for))
        count = 0
        for node in ast.walk(child):
            if ast.unparse(node) == if_vars_list[0]:
                count += 1
                if count > len(intersect_infor_ass_list_in_for):
                    break
        else:
            # print("come remove_assign")
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
                        # print("body: ",e,ast.unparse(e))
                        for e_each in e.body:
                            for ass_each_list in intersect_infor_ass_list_in_for:
                                if e_each == ass_each_list[0][1]:
                                    e.body.remove(e_each)
                for e in ast.walk(tree_copy):
                    if hasattr(e, "body")  and isinstance(e.body,list):
                        # print("body: ",e,ast.unparse(e))
                        for node in e.body:
                            if ast.unparse(intersect_infor_ass_init[0][1]) == ast.unparse(node):
                                e.body.remove(node)
                                break
                        else:
                            continue
                        break
    # print("new_tree: ", ast.unparse(tree))
def traverse_cur_layer(tree, code_list, ass_init_list):
    # print(">>>>>>>>>assign_list: ", ass_init_list)
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
                # print("tree_copy: ",tree_copy,tree.body,ast.unparse(child),child)
                next_child = tree_copy.body[ind + 1]

                flag_if_var, if_varnode = whether_if_and_contain_var(next_child)

                if not if_varnode:
                    traverse_cur_layer(child, code_list, ass_init_list)
                    continue
                # print("it is if node after for stmt: ", flag_if_var, ast.unparse(next_child), if_vars_list)
                all_assign_list_in_for = []
                if_list_in_for = []
                break_list_in_for=[]
                break_flag = whether_contain_break_and_const_assign(child_copy, all_assign_list_in_for, if_list_in_for,break_list_in_for)


                if break_flag:

                    flag_simplify = 0
                    if if_varnode.orelse:
                        for if_list_each in if_list_in_for:
                            if hasattr(if_list_each, "test") and if_list_each.test and is_same_two_if_test(
                                if_varnode.test, if_list_each.test):
                                # modify(tree_copy, child_copy, if_varnode, if_list_each, 0)
                                flag_simplify=1
                            else:
                                flag_simplify=0
                                break
                        else:
                            for if_list_each in if_list_in_for:
                                modify(tree_copy, child_copy, if_varnode, if_list_each, 0)


                    if not flag_simplify:
                        for if_list_each in if_list_in_for:
                            if not hasattr(if_list_each, "test") or (hasattr(if_list_each, "test") and if_list_each.test and not is_differ_two_if_test(
                                if_varnode.test, if_list_each.test)):
                                break
                        else:
                            for if_list_each in if_list_in_for:
                                modify(tree_copy, child_copy, if_varnode, if_list_each, 1)
                            flag_simplify=1


                    assign_flag=0

                    # print("ass_init_list: ",ass_init_list)
                    if not flag_simplify:
                            # if_test and assign_again
                            flag_simplify=1
                            for ind_ass,assign_list_in_for in enumerate(all_assign_list_in_for):
                                for ass in assign_list_in_for:
                                    try:
                                        if ass_init_list and ast.unparse(ass_init_list[-1].value) != ast.unparse(ass.value):
                                            if is_differ_ass_again_if_test(ass, if_varnode.test):
                                                break
                                            elif if_varnode.orelse and is_same_ass_init_if_test(ass, if_varnode.test):
                                                break
                                            else:
                                                continue
                                    except:
                                        traceback.print_exc()
                                        continue
                                else:
                                    flag_simplify = 0
                                    break
                            if flag_simplify:
                                for ind_ass, assign_list_in_for in enumerate(all_assign_list_in_for):
                                    for ass in assign_list_in_for:
                                        if ass_init_list and ast.unparse(ass_init_list[-1].value) != ast.unparse(ass.value):
                                            if is_differ_ass_again_if_test(ass, if_varnode.test):
                                                modify(tree_copy, child_copy, if_varnode, if_list_in_for[ind_ass], 1)
                                                break
                                            elif if_varnode.orelse and is_same_ass_init_if_test(ass, if_varnode.test):
                                                modify(tree_copy, child_copy, if_varnode, if_list_in_for[ind_ass], 0)
                                                break
                                assign_flag = 1
                                # print("new_tree: ",ast.unparse(tree_copy))

                            # for ind_ass,assign_list_in_for in enumerate(all_assign_list_in_for):
                            #     for ass in assign_list_in_for:
                            #         if ast.unparse(ass_init_list[-1].value)!=ast.unparse(ass.value):
                            #             if is_differ_ass_again_if_test(ass, if_varnode.test):
                            #                 flag_simplify = 1
                            #                 for if_list_each in if_list_in_for:
                            #                     modify(tree_copy, child_copy, if_varnode, if_list_each, 1)
                            #                 # print("assig list in for new_tree 1: ", ast.unparse(tree_copy))
                            #                 break
                            #             elif if_varnode.orelse and is_same_ass_init_if_test(ass, if_varnode.test):
                            #                 for if_list_each in if_list_in_for:
                            #                     modify(tree_copy, child_copy, if_varnode, if_list_each, 0)
                            #                 # print("assig list in for  new_tree 0: ", ast.unparse(tree_copy))
                            #                 flag_simplify = 1
                            #                 break
                            #             else:
                            #                 flag_simplify = 0
                            #                 break

                        # print("new tree: ",ast.unparse(tree_copy),if_list_in_for)
                    visit_vars(if_varnode.test, if_vars_list)
                    # for ass_ini in ass_init_list:
                    #     print("ass_ini: ",ast.unparse(ass_ini))
                    intersect_flag_ass_init, intersect_infor_ass_init = get_intersect_vars(ass_init_list,if_vars_list)
                    # for ass_ini in intersect_infor_ass_init:
                    #     print("ass_ini: ",ast.unparse(ass_ini[1]))
                    intersect_flag_ass_list_in_for, intersect_infor_ass_list_in_for =0,[]
                    for assign_list_in_for in all_assign_list_in_for:
                        flag_inn,info_inn=get_intersect_vars(assign_list_in_for, if_vars_list)

                        if not flag_inn:
                            break
                        intersect_infor_ass_list_in_for.append(info_inn)
                    else:
                        intersect_flag_ass_list_in_for=1

                    # print("if_vars_list: ",if_vars_list)
                    # for ass in ass_init_list:
                    #     print("ass: ",ast.unparse(ass))
                    # print("intersect_flag_ass_init: ",ass_init_list,intersect_flag_ass_init,intersect_infor_ass_init)
                    # if intersect_infor_ass_init and intersect_flag_ass_list_in_for:
                    #     assign_init = ast.unparse(intersect_infor_ass_init[-1][1])
                    #     print("intersect_flag_ass_init: ",intersect_infor_ass_init,assign_init)

                    if not flag_simplify and intersect_infor_ass_init and intersect_flag_ass_list_in_for:
                        if is_same_ass_init_if_test(intersect_infor_ass_init[-1][1], if_varnode.test):
                            # print("yes  if_test and assign init could be simplified to for else: ",ast.unparse(tree_copy))
                            # print("child copy: ",ast.unparse(child_copy),"-------\n",ast.unparse(if_varnode),if_list_in_for)
                            for if_list_each in if_list_in_for:
                                modify(tree_copy, child_copy, if_varnode, if_list_each, 1)
                            # print("assign init new_tree: ",ast.unparse(tree_copy))
                            flag_simplify = 1
                            assign_flag = 1
                        elif  if_varnode.orelse and  is_differ_ass_again_if_test(intersect_infor_ass_init[-1][1], if_varnode.test):
                            for if_list_each in if_list_in_for:
                                modify(tree_copy, child_copy, if_varnode, if_list_each, 0)
                            # print("assign init new_tree: ", ast.unparse(tree_copy))
                            flag_simplify = 1
                            assign_flag = 1
                    if flag_simplify and assign_flag:
                            remove_assign(tree_copy,child_copy,tree,child,if_vars_list,intersect_infor_ass_list_in_for,intersect_infor_ass_init,ind)



                    if flag_simplify:
                        # print(">>>>>>>>>>>>>old tree:\n",ast.unparse(tree))
                        # print(">>>>>>>>>>>>>new tree:\n", ast.unparse(tree_copy))
                        code_list.append([tree,tree_copy,break_list_in_for])
                        # code_list.append([ ast.unparse(tree),ast.unparse(tree_copy),break_list_in_for[0].lineno])
                        # code_list.append(
                        #     [assign_init + "\n" + ast.unparse(child) + "\n" + ast.unparse(next_child), child.lineno,
                        #      next_child.lineno])

                # if break_flag and intersect_flag_ass or intersect_flag_if and break_flag:
                #     code_list.append([intersect_infor_ass_init[-1],child,next_child,])
                #     code_list.append([ast.unparse(child) + "\n" + ast.unparse(next_child),child.lineno,next_child.lineno])
            else:
                for e_chi in ast.walk(child_copy):
                    if isinstance(e_chi, (ast.Assign,ast.AnnAssign)) and e_chi not in ass_init_list  :
                        # print("else: ",ast.unparse(e_chi))
                        ass_init_list.append(e_chi)
                # print("assign_list: ",ass_init_list)

            traverse_cur_layer(child, code_list, ass_init_list)


def save_repo_for_else_complicated(repo_name):
    start=time.time()
    count_complicated_code = 0
    print("come the repo: ", repo_name)
    one_repo_for_else_code_list = []

    dict_file=dict()
    # if os.path.exists(save_complicated_code_dir + repo_name + ".json"):
    #     print("the repo has been saved before")
    #     return None

    for ind,file_info in enumerate(dict_repo_file_python[repo_name]):



        file_path = file_info["file_path"]
        # if file_path!="/mnt/zejun/smp/data/python_repo_1000/VideoPose3D//run.py":
        #     continue
        file_html = file_info["file_html"]


        try:
            content = util.load_file_path(file_path)
        except:
            print(f"{file_path} is not existed!")
            continue

        # print("content: ",content)
        try:
            file_tree = ast.parse(content)
            ana_py = ast_util.Fun_Analyzer()
            ana_py.visit(file_tree)

            # dict_file["repo_name"]=repo_name


            dict_class=dict()
            for tree, class_name in ana_py.func_def_list:

                # print("tree_ func_name",tree.__dict__)
                new_code_list = []
                ass_init_list = []
                traverse_cur_layer(tree, new_code_list, ass_init_list)
                ast_util.set_dict_class_code_list(tree, dict_class, class_name, new_code_list)


            dict_file[file_html]=dict_class

            # if code_list:
            #     one_repo_for_else_code_list.append([code_list, file_path, file_html])
                # if len(one_repo_for_else_code_list)>2:
                #     break

        except SyntaxError:
            print("the file has syntax error")
            continue
        except ValueError:
            traceback.print_exc()
            print("the file has value error: ", file_html)
            continue
        except:
            print("the file error: ", file_html)
            traceback.print_exc()
        # break
    end = time.time()
    #'''
    if dict_file:
        count_complicated_code = count_complicated_code + len(one_repo_for_else_code_list)
        # print("it exists for else complicated code1: ", len(one_repo_for_else_code_list))
        util.save_pkl(save_complicated_code_dir_pkl, repo_name, dict_file)
        # util.save_json(save_complicated_code_dir, repo_name, one_repo_for_else_code_list)
        print(end-start," save successfully! ", save_complicated_code_dir_pkl + repo_name)
    else:
        print(end-start," the repo has no for else")
        util.save_pkl(save_complicated_code_dir_pkl, repo_name, dict_file)
        # util.save_json(save_complicated_code_dir, repo_name, one_repo_for_else_code_list)
    #'''
    return count_complicated_code


if __name__ == '__main__':
    code = '''
# if match:
#     skip = True
#     for pat in self.patterns:
#         if not pat.exclusion:
#             continue
#         if pat.cleaned_pattern.startswith(normalize_slashes(fpath)):
#             skip = False
#             break
#     if skip:
#         continue
        
# for current_package in self._current_packages:
#     found = False
#     for (result_package, _) in self._result_packages:
#         if current_package.name == result_package.name:
#             found = True
#             break
#     if not found:
#         for installed_package in self._installed_packages:
#             if installed_package.name == current_package.name:
#                 operations.append(Uninstall(current_package))
# def __get_path_from_ref(self, ref):
#     refs = ref.split('/')
#     for (i, ref) in enumerate(refs):
#         if ref.endswith('.kp'):
#             break
#     if not ref.endswith('.kp'):
#         return None
#     return '/'.join(refs[:i + 1])
    
# crumb = None
# sess = requests.Session()
# for i in range(self.retries + 1):
#         resp = sess.get(url, **sesskwargs)
#         if resp.status_code != requests.codes.ok:
#             continue
#         txt = resp.text
#         i = txt.find('CrumbStore')
#         istart = txt.find('"', i + len('crumb') + 1)
#         if istart == -1:
#             continue
#         istart += 1
#         iend = txt.find('"', istart)
#         if iend == -1:
#             continue
#         crumb = txt[istart:iend]
#         crumb = crumb.encode('ascii').decode('unicode-escape')
#         break
# if crumb is None:
#         self.error = 'Crumb not found'
#         self.f = None
#         return
    
    
# is_choice = False
# if len(choice_list) == 0:
#     is_choice = True
# for ch in choice_list:
#     if ch in title:
#         is_choice = True
#         break
# if is_choice == False:
#     return False
# is_ban = False
# for ba in ban_list:
#     if ba in title:
#         is_ban = True
#         break
# if is_ban == True:
#     return False
# return True

# def trigger(self, char, *args, **kwargs):
#     if isinstance(char, six.string_types) and len(char) == 1:
#         char = ord(char)
#     func = None
#     for controller in self.parents:
#         func = controller.character_map.get((self.last_char, char))
#         if func:
#             break
#         func = controller.character_map.get(char)
#         if func:
#             break
#     if func:
#         self.last_char = None
#         return func(self.instance, *args, **kwargs)
#     else:
#         self.last_char = char
#         return None

# root_hierarchical_hash = None
# if hierarchical_hashes:
#     hierarchical_grouphashes = {h.hash: h for h in GroupHash.objects.filter(project=project, hash__in=hierarchical_hashes)}
#     for hash in reversed(hierarchical_hashes):
#         group_hash = hierarchical_grouphashes.get(hash)
#         if group_hash is not None and group_hash.state == GroupHash.State.SPLIT:
#             found_split = True
#             break
#         root_hierarchical_hash = hash
#         if group_hash is not None:
#             all_grouphashes.append(group_hash)
#     if root_hierarchical_hash is None:
#         root_hierarchical_hash = hierarchical_hashes[-1]
#         group_hash = hierarchical_grouphashes.get(root_hierarchical_hash)
#         if group_hash is not None:
#             all_grouphashes.append(group_hash)
# for i in range(2):
#     print(i)
#     break
# if a:
#     print("1")

# response = None
# callback, callback_args, callback_kwargs = self.resolve_request(request)
# 
# # Apply view middleware.
# for middleware_method in self._view_middleware:
#     response = await middleware_method(request, callback, callback_args, callback_kwargs)
#     if response:
#         break
# 
# if response is None:
#     # print("test_if")
#     wrapped_callback = self.make_view_atomic(callback)    
# else:
#     print("test")
#     print("test2")



# _checkpoint_callback = None
# require_checkpoint = False
# 
# with remote_store.get_local_output_dir() as run_output_dir:
#     logs_path = os.path.join(run_output_dir, remote_store.logs_subdir)
#     os.makedirs(logs_path, exist_ok=True)
#     print(f"Made directory {logs_path} for horovod rank {hvd.rank()}")
#     ckpt_dir = run_output_dir
#     ckpt_filename = remote_store.checkpoint_filename
# 
#     if logger is None:
#         # Use default logger if no logger is supplied
#         train_logger = TensorBoardLogger(logs_path)
#         print(f"Setup logger: Using TensorBoardLogger: {train_logger}")
# 
#     elif isinstance(logger, CometLogger) and logger._experiment_key is None:
#         # Resume logger experiment key if passed correctly from CPU.
#         train_logger = CometLogger(
#             save_dir=logs_path,
#             api_key=logger.api_key,
#             experiment_key=logger_experiment_key,
#         )
# 
#         print(f"Setup logger: Resume comet logger: {vars(train_logger)}")
#     else:
#         # use logger passed in.
#         train_logger = logger
#         train_logger.save_dir = logs_path
#         print(f"Setup logger: Using logger passed from estimator: {train_logger}")
# 
#     # Lightning requires to add checkpoint callbacks for all ranks.
#     # Otherwise we are seeing hanging in training.
#     for cb in callbacks:
#         if isinstance(cb, ModelCheckpoint):
#             cb.dirpath = ckpt_dir
#             cb.filename = ckpt_filename
#             _checkpoint_callback = cb
#             require_checkpoint = True
#             break
#     if not _checkpoint_callback:
#         # By default 'monitor'=None which saves a checkpoint only for the last epoch.
#         _checkpoint_callback = ModelCheckpoint(dirpath=ckpt_dir,
#                                                filename=ckpt_filename,
#                                                verbose=True) 
#     else:
#         print("the else 1")
#         print("the else 2")
       
# 
# for module_name in relevant_modules:
#     relevant_keys = set([key for key in state_dict.keys() if key.startswith(module_name + '.')])
#     if relevant_keys:
#         state_dict = {key.replace(module_name + '.', '', 1): value for (key, value) in state_dict.items() if key in relevant_keys}
#         found = True
#         break
# if not found:
#     warnings.warn(f'{relevant_modules} was not found at top level of state_dict!', UserWarning)
# else:
#     print("the else 1")
#     print("the else 2")
# for new_loc in new_locs:
#     new_loc_nes = [xx for xx in [(new_loc[0] + 1, new_loc[1]), (new_loc[0] - 1, new_loc[1]), (new_loc[0], new_loc[1] + 1), (new_loc[0], new_loc[1] - 1)] if xx[0] >= 0 and xx[0] < my_fpath_map.shape[0] and (xx[1] >= 0) and (xx[1] < my_fpath_map.shape[1])]
#     if fpath_map is not None and np.sum([fpath_map[nlne[0], nlne[1]] for nlne in new_loc_nes]) != 0:
#         break_flag = True
#         break
#     if my_npath_map[new_loc[0], new_loc[1]] != -1:
#         continue
#     if npath_map is not None and npath_map[new_loc[0], new_loc[1]] != edge_id:
#         break_flag = True
#         break
#     fpath.append(new_loc)
# if break_flag is True:
#     break    


# for controller in self.parents:
#     func = controller.character_map.get((self.last_char, char))
#     if func:
#         break
#     func = controller.character_map.get(char)
#     if func:
#         break
# if func:
#     self.last_char = None
#     return func(self.instance, *args, **kwargs)
# else:
#     self.last_char = char
#     return None
found = False
for a in action_filter:
    if action.startswith(a):
        found = True
        break
if not found:
    continue

# for (host, slots) in host_list:
#     slots = int(slots)
#     if slots > lsf.LSFUtils.get_num_gpus():
#         raise ValueError("Invalid host input, slot count for host '{host}:{slots}' is greater than number of GPUs per host '{gpus}'.".format(host=host, slots=slots, gpus=lsf.LSFUtils.get_num_gpus()))
#     needed_slots = min(slots, remaining_slots)
#     validated_list.append((host, needed_slots))
#     remaining_slots -= needed_slots
#     if remaining_slots == 1:
#         break
# if remaining_slots != 1:
#     raise ValueError('Not enough slots on the hosts to fulfill the {slots} requested.'.format(slots=settings.num_proc))

# for f in possible_font_names:
#     pdf_text_font = pdf_text_fonts.get(f, None)
#     if pdf_text_font is not None:
#         font_key = f
#         break
# if pdf_text_font:
#     font = self.pdf_base.copy_foreign(pdf_text_font)
# a=1
# b=2
# c,d=1,2
# for i in range(2):
#     a=1
#     if i>1:
#         if i>2:
#             a=3
#         a=2
#         break 
# if a==2:
#     print(1)
# print("1")   
# def a():
#     return 1
# a=2
# for i in range(5):
#     a=1
#     break
# if a:
#     print("test")
# for i in range(2):
#     if i>2:
#         a=1
#         for j in range(3):
#             if j>2:
#                 break
# if a:
#     print("it should not a 可简化的for else代码")
# if a>2:
#     for i in range(2):
#         break
# elif a>3:
#     print("test")
# def func2():
#     while start < len(chars):
#         end = len(chars)
#         cur_substr = None
#         while start < end:
#             substr = ''.join(chars[start:end])
#             if start == 0:
#                 substr = sentencepiece_prefix + substr
#             if start > 0:
#                 substr = prefix + substr
#             if substr in vocab:
#                 cur_substr = substr
#                 break
#             end -= 1
#         if cur_substr is None:
#             is_bad = True
#             break
#         sub_tokens.append(cur_substr)
#         sub_pos.append((start, end))
#         start = end
#     if is_bad:
#         return ([unk_token], [(0, len(chars))])
#     else:
#         return (sub_tokens, sub_pos)
# def func():
#     for nexttag in tag_iter:
#         tagname = nexttag.tag
#         attributes = nexttag.attributes
#         if tagname == 'a' and (nexttag.tag_type == CLOSE_TAG or (attributes.get('href') and (not attributes.get('href', '').startswith('#')))):
#             if astart:
#                 yield mklink(ahref, body[astart:nexttag.start], nofollow)
#                 astart = ahref = None
#                 nofollow = False
#             href = attributes.get('href')
#             if href:
#                 ahref = href
#                 astart = nexttag.end
#                 nofollow = attributes.get('rel') == u'nofollow'
#         elif tagname == 'head':
#             for nexttag in tag_iter:
#                 tagname = nexttag.tag
#                 if tagname == 'head' and nexttag.tag_type == HtmlTagType.CLOSE_TAG or tagname == 'body':
#                     break
#                 if tagname == 'base':
#                     href = nexttag.attributes.get('href')
#                     if href:
#                         joined_base = urljoin(htmlpage.url, href.strip().strip(), htmlpage.encoding)
#                         base_href = remove_entities(joined_base, encoding=htmlpage.encoding)
#                 elif tagname == 'meta':
#                     attrs = nexttag.attributes
#                     if attrs.get('http-equiv') == 'refresh':
#                         m = _META_REFRESH_CONTENT_RE.search(attrs.get('content') or '')
#                         if m:
#                             target = m.group('url')
#                             if target:
#                                 yield mklink(target)
#                 elif tagname == 'link':
#                     href = nexttag.attributes.get('href')
#                     if href:
#                         yield mklink(href)
#         elif tagname == 'area':
#             href = attributes.get('href')
#             if href:
#                 nofollow = attributes.get('rel') == 'nofollow'
#                 yield mklink(href, attributes.get('alt', ''), nofollow)
#         elif tagname in ('frame', 'iframe'):
#             target = attributes.get('src')
#             if target:
#                 yield mklink(target)
#         elif 'onclick' in attributes:
#             match = _ONCLICK_LINK_RE.search(attributes['onclick'] or '')
#             if not match:
#                 continue
#             target = match.group('url')
#             nofollow = attributes.get('rel') == u'nofollow'
#             yield mklink(target, nofollow=nofollow)
#     if astart:
#         yield mklink(ahref, htmlpage.body[astart:])
'''
    #     code1 = '''
    # for i in range(2):
    #     a=1
    #     b=2
    #     for j in range(3):
    #         w=8
    #         break
    #     if i>1 and j>3 and i!=0:
    #         if i>2 and call(1,t,*T):
    #             b=3
    #             break
    #     c=3
    #     '''

    # tree = ast.parse(code1)
    # for node in ast.walk(tree):
    #     if isinstance(node,(ast.For,ast.While)):
    #         print("-------------------------")
    #         assign_list_in_for,if_list_in_for=[],[]
    #         whether_contain_break_and_const_assign(node, assign_list_in_for, if_list_in_for)
    #         print(assign_list_in_for,if_list_in_for)
    #         # assign_list_in_for=[]
    #         # if_list_in_for=[]
    #         # break_flag=whether_contain_break_and_const_assign(node, assign_list_in_for,if_list_in_for)
    #         #
    #         # print(break_flag,assign_list_in_for,if_list_in_for)
    #     elif isinstance(node,ast.If):
    #         if_vars=[]
    #         visit_vars(node.test,if_vars)
    #         print("if vars: ",if_vars)
    # code_list = []
    # ass_init_list = []
    # traverse_cur_layer(tree, code_list, ass_init_list)
    # print("*****************: ", code_list)
    # code_list=[]
    # tree=ast.parse(code1)
    # traverse_cur_layer(tree,code_list)
    # print(code_list)

    # for_else_filter_redundant_code_list = get_for_else_complicate_code(file_tree)
    # print(for_else_filter_redundant_code_list)
    # for one_code in for_else_filter_redundant_code_list:
    #     print("-----------------------",one_code)
    #     print(one_code[0])

    # file_tree = ast.parse(code1)
    # ana_py = Analyzer()
    # ana_py.visit(file_tree)
    # print("fun number: ",len(ana_py.func_def_list))

    # save_complicated_code_dir= util.data_root + "complicated_code_dir_1000_star/for_else_assign_is_const_complicated/"
    # save_complicated_code_dir = util.data_root + "transform_complicate_to_simple/for_else_improve_5/"
    save_complicated_code_dir_pkl = util.data_root + "transform_complicate_to_simple_pkl/for_else/"

    dict_repo_file_python= util.load_json(util.data_root, "python3_1000repos_files_info")

    # dict_repo_file_python = util.load_json(util.data_root, "jupyter3_repos_files_info")

    repo_list = []
    count_file = 0
    for ind, repo_name in enumerate(dict_repo_file_python):
        if repo_name!="sympy":
            continue

        # if os.path.exists(save_complicated_code_dir_pkl + repo_name + ".pkl"):
        #     continue
        # if os.path.exists(save_complicated_code_dir + repo_name + ".json"):
        #     continuetransform_for_else_compli_to_simple_improve.py
        # if ind>30:
        #     break
        # print("repo_name: ", repo_name)
        repo_list.append(repo_name)
        # break
    print("len: ", len(repo_list))
    # save_repo_for_else_complicated(repo_list[0])
    # savetransform_c_s_repo_for_else_complicated(repo_list[0])
    '''
        for file_info in dict_repo_file_python[repo_name]:

            file_path = file_info["file_path"]
            # if file_path!="/mnt/zejun/smp/data/python_repo_1000/VideoPose3D//run.py":
            #     continue
            file_html = file_info["file_html"]
            #print("come this file: ", file_path)
            try:
                content = util.load_file(file_path)
            except:
                print(f"{file_path} is not existed!")
                continue

            #print("content: ",content)
            try:
                file_tree = ast.parse(content)
                count_file+=1
            except:
                continue
    print("number of repos: ", len(repo_list),count_file)
    '''
    '''
    count_complicated_code=0
    for ind,repo_name in enumerate(dict_repo_file_python):
        print("come repo: ",repo_name)
        count_complicated_code+=save_repo_for_else_complicated(repo_name)
        # break
    print("count_complicated_code: ",ind,count_complicated_code)
    '''
    # for repo in repo_list:
    #     # if repo!="django-extensions":#"keras-bert":#"sympy":#"Real-Time-Voice-Cloning":#"keras-bert":#"Legofy":
    #     #     continue
    #     save_repo_for_else_complicated(repo)

    # '''
    #7.8h +
    pool = newPool(nodes=30)
    pool.map(save_repo_for_else_complicated, repo_list)  # [:3]sample_repo_url ,token_num_list[:1]
    pool.close()
    pool.join()
    # print("len all_files: ", len(all_files))
    # '''


    # repo_files_info = util.load_json(util.data_root, "dict_1000_repo_files_info")
    # repo_star_info = util.load_json(util.data_root, "dict_1000_repo_star_info")
    # repo_contributor_info = util.load_json(util.data_root, "dict_1000_repo_contributor_info")


    def get_code_count(complicate_code):
        all_me_count=0
        all_file_count=len(list(complicate_code.keys()))
        code_count = 0
        me_count=0
        NULL_code_count=0
        file_count = 0
        cl_count=0
        for file_html in complicate_code:
            if complicate_code[file_html]:
                file_exist=0
                # cl_count +=len(list(complicate_code[file_html].keys()))
                for cl in complicate_code[file_html]:
                    if complicate_code[file_html][cl]:
                        all_me_count+=len(complicate_code[file_html][cl].keys())
                        for me in complicate_code[file_html][cl]:
                            if complicate_code[file_html][cl][me]:
                                me_count += 1
                                file_exist=1
                                code_count += len(complicate_code[file_html][cl][me])

                file_count += file_exist

        return file_count,me_count,code_count,all_file_count,all_me_count


    files_num_list = []
    star_num_list = []
    contributor_num_list = []
    count_repo, file_count, me_count, code_count = 0, 0, 0, 0
    file_list = set([])
    repo_code_num = dict()
    result_compli_for_else_list = []
    all_count_repo, all_file_count, all_me_count = 0, 0, 0
    for file_name in os.listdir(save_complicated_code_dir_pkl):
        all_count_repo+=1
        repo_name = file_name[:-4]
        # files_num_list.append(repo_files_info[repo_name])
        # star_num_list.append(repo_star_info[repo_name])
        # contributor_num_list.append(repo_contributor_info[repo_name])

        complicate_code = util.load_pkl(save_complicated_code_dir_pkl, repo_name)

        repo_file_count,repo_me_count,repo_code_count,repo_all_file_count,repo_all_me_count= get_code_count(complicate_code)
        # for code_list, file_path, file_html in complicate_code:
        code_count+=repo_code_count
        file_count+=repo_file_count
        me_count+=repo_me_count
        all_file_count+=repo_all_file_count
        all_me_count+=repo_all_me_count
        repo_exist=0
        for file_html in complicate_code:
             for cl in complicate_code[file_html]:
                for me in complicate_code[file_html][cl]:
                    if complicate_code[file_html][cl][me]:
                        repo_exist=1
                        for code in complicate_code[file_html][cl][me]:
                                # print("html: ",file_html,cl,me,ast.unparse(code1[0]))
                                result_compli_for_else_list.append(
                                [repo_name, cl,me,ast.unparse(code[0]), ast.unparse(code[1]), file_html])

            # print(f"{file_html} of {repo_name} has  {len(code_list)} code1 fragments")
        count_repo += repo_exist
            #     break
            # break
        # if complicate_code:
        #     repo_code_num[repo_name]=count_code_fra
        #     print(f"{repo_name} has  {count_code_fra} code1 fragments")
        # break
    # a=dict(sorted(repo_code_num.items(), key=lambda item: item[1], reverse=True))
    # print(a)
    # print(np.median(list(a.values())), np.max(list(a.values())), np.min(list(a.values())))
    # print(np.median(files_num_list), np.max(files_num_list), np.min(files_num_list))
    # print(np.median(star_num_list), np.max(star_num_list), np.min(star_num_list))
    # print(np.median(contributor_num_list), np.max(contributor_num_list), np.min(contributor_num_list))
    print("count: ", count_repo,code_count,file_count,me_count,all_count_repo,all_file_count,all_me_count)
    #1 156 2943 100 1 2990 40102 salt
    #791 2010 103165 1291 800 121348 1192868
    # util.save_csv(util.data_root + "complicated_code_dir_1000_star/for_else.csv", result_compli_for_else_list,
    #               ["repo_name","class_name","me_name", "old_code","new_code", "file_html", "file_path"])
    # # util.save_csv(util.data_root+"complicated_code_dir_1000_star/for_else_iftest_intersect_iftest_assign.csv",result_compli_for_else_list,["repo_name","code1","file_html","file_path"])

    # util.save_csv(util.data_root + "complicated_jupyter_code_dir/for_else.csv", result_compli_for_else_list,
    #               ["repo_name", "code1", "file_html", "file_path"])

    # print("----------------------------\n")
    # for code1 in for_else_filter_redundant_code_list:
    #     print("each code1: ", code1[0])
