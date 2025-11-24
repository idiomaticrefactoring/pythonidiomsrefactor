import ast
import tokenize
import sys
# sys.path.append("../../..")
# sys.path.append("../../../../")
# sys.path.append("/mnt/zejun/smp/code1/")
# sys.path.append("/mnt/zejun/smp/code1/transform_c_s")
from RefactoringIdioms.extract_simp_cmpl_data import ast_util
from RefactoringIdioms.transform_c_s.transform_assign_multi_compli_to_simple import transform_multiple_assign
from tokenize import tokenize
from io import BytesIO
# from pathos.multiprocessing import ProcessingPool as newPool
import traceback
'''
input: 代码片段 code1
'''
def get_tokens(node):
    s = ast.unparse(node)
    g = tokenize(BytesIO(s.encode('utf-8')).readline)  # tokenize the string
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


# def visit_vars(target, list_vars):
#     # print(">>>>>>>target: ",target.__dict__)
#     if isinstance(target, (ast.Name)):
#         list_vars.append(ast.unparse(target))
#     elif  isinstance(target, ast.Subscript):
#         list_vars.append(ast.unparse(target))
#         visit_vars(target.value, list_vars)
#         visit_vars(target.slice, list_vars)
#     elif isinstance(target,ast.Attribute):
#         # print("attr: ",ast.unparse(target))
#         list_vars.append(ast.unparse(target))
#         visit_vars(target.value, list_vars)
#     else:
#         print("visit_vars else node: ", ast.unparse(target))
#         for e in ast.iter_child_nodes(target):
#             visit_vars(e, list_vars)
def visit_single_vars(target, list_vars):
    # print(">>>>>>>target: ",target.__dict__)
    if isinstance(target, (ast.Name)):
        list_vars.append(ast.unparse(target))
    elif  isinstance(target, ast.Subscript):
        list_vars.append(ast.unparse(target))
        if not isinstance(target.value,ast.Subscript):
            visit_single_vars(target.value, list_vars)
    elif isinstance(target,ast.Attribute):
        print("attr: ",ast.unparse(target))
        list_vars.append(ast.unparse(target))
        visit_single_vars(target.value, list_vars)
    else:
        print("visit_single_vars else node: ", ast.unparse(target))
        for e in ast.iter_child_nodes(target):
            print("visit_single_vars e: ",e,ast.unparse(e))
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
        # print("assign_list: ",assign_list)
        body_list = all_body_list[ind_ass]
        a = [assign_list[0]]
        for ind_e, ass in enumerate(assign_list[1:]):
            next_tar = ass.targets[0]
            for reverse_ind_e2, pre_ass in enumerate(a[::-1]):#
                ind_e2=len(a)-reverse_ind_e2-1
                pre_tar = pre_ass.targets[0]

                if is_depend(pre_tar, next_tar):

                    if len(a[:ind_e2+1]) > 1:
                        all_assign_left_no_overlap_list.append([a[:ind_e2+1], body_list])
                    # print("is_depend: ",a,a[ind_e2+1:])
                    a = a[ind_e2+1:]
                    a.append(ass)#[]
                    break
            else:
                a.append(ass)
        if len(a) > 1:
            all_assign_left_no_overlap_list.append([a, body_list])
    # print(all_assign_left_no_overlap_list)
    real_assign_list = []
    for ind_ass, (assign_list, body_list) in enumerate(all_assign_left_no_overlap_list):

        a = [assign_list[0]]
        overlap_flag=0
        for ind_e, ass in enumerate(assign_list[1:]):
            # print("whether add the ass: ",ast.unparse(ass))
            next_value = ass.value
            for reverse_ind_e2, pre_ass in enumerate(a[::-1]):
                ind_e2=len(a)-reverse_ind_e2-1
                pre_tar = pre_ass.targets[0]
                pre_value = pre_ass.value

                def intersect_var(pre_tar, next_value):
                    # pre_var_list = []
                    for node in ast.walk(next_value):
                        if ast.unparse(pre_tar)==ast.unparse(node):
                            return 1
                    for node in ast.walk(pre_tar):
                        if ast.unparse(node)==ast.unparse(next_value):
                            return 1
                    return 0
                    # visit_vars(pre_tar, pre_var_list)
                    # next_var_list = []
                    # visit_vars(next_value, next_var_list)
                    # if set(pre_var_list) & set(next_var_list):
                    #     # print("intersect: ",pre_var_list,next_var_list,set(pre_var_list) & set(next_var_list))
                    #     return 1
                    # return 0

                def value_is_in_target_list(pre_value, ass_list):
                    for ass in ass_list:
                        tar = ass.targets[0]
                        if ast.unparse(pre_value) == ast.unparse(tar):
                            return 1
                    return 0

                if intersect_var(pre_tar, next_value):
                    # print("intersect assign: ",ast.unparse(ass),ast.unparse(pre_ass))
                    if not is_depend(pre_tar, next_value) or is_occur_body(ast.unparse(pre_tar), body_list) or not value_is_in_target_list(pre_value, a[ind_e2 + 1:]):
                        # print("intersect assign: ", ast.unparse(ass), ast.unparse(pre_ass),a)
                        # if len(a[:ind_e2+1]) > 1:
                        #     real_assign_list.append(a[:ind_e2+1])
                        if len(a[:ind_e2+1]) > 1 and overlap_flag:
                            real_assign_list.append(a)
                        a = a[ind_e2+1:]
                        a.append(ass)
                        if ind_e!=len(assign_list[1:])-1:
                                overlap_flag=0
                        # print("intersect assign: ",a)
                        # overlap_flag = 1
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

        # next_tar_str=ast.unparse(pre_tar)
        # for node in ast.walk(pre_tar):
        #     if next_tar_str == ast.unparse(node):
        #         return 1

        return 0
    def is_depend_str(pre_tar_str, next_tar):

        for node in ast.walk(next_tar):
            if pre_tar_str == ast.unparse(node):
                return 1
        return 0



    all_assign_left_no_overlap_list = []
    for ind_ass, assign_list in enumerate(all_assign_list):
        # print("assign_list: ",assign_list)
        body_list = all_body_list[ind_ass]
        a = [assign_list[0]]
        for ind_e, ass in enumerate(assign_list[1:]):
            next_tar = ass.targets[0]
            for reverse_ind_e2, pre_ass in enumerate(a[::-1]):#
                ind_e2=len(a)-reverse_ind_e2-1
                pre_tar = pre_ass.targets[0]

                if is_depend(pre_tar, next_tar):

                    if len(a[:ind_e2+1]) > 1:
                        all_assign_left_no_overlap_list.append([a[:ind_e2+1], body_list])
                    # print("is_depend: ",a,a[ind_e2+1:])
                    a = a[ind_e2+1:]
                    a.append(ass)#[]
                    break
            else:
                a.append(ass)
        if len(a) > 1:
            all_assign_left_no_overlap_list.append([a, body_list])
    # print(all_assign_left_no_overlap_list)
    # for ass,body_list in all_assign_left_no_overlap_list:
    #     print(">>>>>>>>>>>>>: ")
    #     for e_ass in ass:
    #         print("ass: ",ast.unparse(e_ass))

    real_assign_list = []
    for ind_ass, (assign_list, body_list) in enumerate(all_assign_left_no_overlap_list):

        a = [assign_list[0]]

        for ind_e, ass in enumerate(assign_list[1:]):
            # print("whether add the ass: ",ast.unparse(ass))
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
                    # pre_var_list = []
                    pre_var_list=[]
                    for node in ast.walk(pre_tar):
                        pre_var_list.append(ast.unparse(node))
                        # if ast.unparse(pre_tar)==ast.unparse(node):
                        #     return 1
                    def visit_vars(target, list_vars, pre_var_list, pre_tar):
                        if isinstance(target, (ast.Name)):
                            list_vars.append(ast.unparse(target))
                        elif isinstance(target, ast.Subscript):
                            list_vars.append(ast.unparse(target))
                            if not(isinstance(target,type(pre_tar)) and ast.unparse(target.value) in pre_var_list):
                            #     list_vars.append( ast.unparse(target.value))
                            # else:

                                visit_vars(target.value, list_vars, pre_var_list, pre_tar)
                            visit_vars(target.slice, list_vars, pre_var_list, pre_tar)
                        elif isinstance(target, ast.Attribute):
                            # print("attr: ",ast.unparse(target))
                            list_vars.append(ast.unparse(target))
                            if not(isinstance(target, type(pre_tar)) and ast.unparse(target.value) in pre_var_list):
                            #     list_vars.append( ast.unparse(target.value))
                            # else:
                            # if not (isinstance(target, type(pre_tar)) and (ast.unparse(target.value) not in pre_var_list)):
                                visit_vars(target.value, list_vars, pre_var_list, pre_tar)

                            # visit_vars(target.value, list_vars)
                        elif isinstance(target, list):
                            for e in target:
                                visit_vars(e, list_vars, pre_var_list, pre_tar)
                        else:
                            # print("visit_vars else node: ", ast.unparse(target),type(target))
                            for e in ast.iter_child_nodes(target):
                                visit_vars(e, list_vars, pre_var_list, pre_tar)

                        pass
                    # print("next_value,pre_tar: ",ast.unparse(next_value),ast.unparse(pre_tar))
                    list_vars=[]
                    visit_vars(next_value, list_vars, pre_var_list, pre_tar)
                    if set(list_vars)&set(pre_var_list):
                        return 1
                    return 0
                    # for node in ast.walk(pre_tar):
                    #     if ast.unparse(node)==ast.unparse(next_value):
                    #         return 1
                    # return 0
                # list_vars=[]
                # visit_vars(pre_tar, list_vars)
                # print("list_vars: ", ast.unparse(pre_tar),ast.unparse(pre_ass),list_vars)
                # next_value_var_list=[]
                # print(">>>>>>>come here",ast.unparse(next_value),ast.unparse(ass))
                # visit_single_vars(next_value,next_value_var_list)
                # print("next_value_var_list: ",ast.unparse(next_value),ast.unparse(ass),next_value_var_list)
                if intersect_var(pre_tar, next_value) or intersect_var( next_value,pre_tar) :#set(list_vars)&set(next_value_var_list):#intersect_var(pre_tar, next_value):
                        # print("next_value: ", ast.unparse(next_value))
                        # print("pre target tokens: ",get_tokens(pre_tar))
                    # print("next_value tokens: ", get_tokens(next_value))
                    # vars=get_tokens(next_value)
                    # # vis_vars=Visit_vars()
                    # # vis_vars.visit(next_value)
                    # nex_value_dep_pre_tar=0
                    # # for var in vis_vars.vars:
                    # for var in vars:
                    #     print("var: ",var)
                    #     if  is_depend_str(var, pre_tar):
                    #         nex_value_dep_pre_tar=1
                    #         break
                    # print("intersect assign: ",ast.unparse(ass),ast.unparse(pre_ass))
                    # if (is_depend(pre_tar, next_value) or nex_value_dep_pre_tar):
                    #     print("come here depend: ",)
                        if not (is_depend(pre_tar, next_value) and not is_occur_body(ast.unparse(pre_tar), body_list) and value_is_in_target_list(pre_value, a[ind_e2 + 1:])):
                        #     a.append(ass)
                        # else:
                        #     print("intersect assign: ", ast.unparse(ass), ast.unparse(pre_ass),a,ind_e2+1)
                            if len(a[:ind_e2+1]) > 1:
                                real_assign_list.append(a[:ind_e2+1])
                            a = a[ind_e2+1:]
                            a.append(ass)
                            # print("the real a : ",[ast.unparse(e) for e in a])

                            # overlap_flag = 1
                            break
            else:
                a.append(ass)

        if len(a) > 1:
            real_assign_list.append(a)
    return real_assign_list

# def split_assignments(all_assign_list,all_body_list):
#     real_assign_list=[]
#     for ind_ass,assign_list in enumerate(all_assign_list):
#         body_list=all_body_list[ind_ass]
#
#         node=assign_list[0]
#
#         all_write_vars=[]
#         write_vars=[]
#         visit_vars(node.targets[0], write_vars)
#
#         all_write_vars.append(write_vars)
#         same_value_var=ast.unparse(node.targets[0])
#         pre_same_values=[ast.unparse(node.targets[0])]
#         a=[assign_list[0]]
#         next_read_vars=[]
#
#         '''
#         s.p=a
#         b=s # this cannot be simplified
#         '''
#         flag=0# whether assignment list contain intersect vars for writing vars and reading vars
#         for ind,ass in enumerate(assign_list[1:]):
#             value=ass.value
#             read_vars = []
#             visit_right_vars(value, read_vars)
#             intersect=set([])
#             for write_vars in all_write_vars:
#                 intersect|=set(read_vars)&set(write_vars)
#
#
#             #
#             if intersect:
#                 print("intersect: ",intersect, ast.unparse(ass))
#                 ind_list = []
#                 for e in intersect:
#
#                     for ind_write,write_var in enumerate(all_write_vars):
#                         if e in write_var:
#                             ind_list.append(ind_write)
#                 # print("ind_list",ind_list,ast.unparse(ass),a)
#                 new_write_vars = []
#                 visit_vars(ass.targets[0], new_write_vars)
#                 all_write_vars.append(new_write_vars)
#
#                 if len(set(ind_list))>1:
#                     print("multiple targets overlap: ", ind_list, ast.unparse(ass))
#                     if len(a) > 1 and flag:
#                         real_assign_list.append(a)
#                         a=[ass]
#
#                         if ind!=len(assign_list[1:])-1:
#                             flag = 0
#                     continue
#
#                 if set(pre_same_values) & intersect:
#
#                     print("same_value_var: ",same_value_var, intersect,ast.unparse(ass))
#                     # is_occur=0
#                     for same_value_var in pre_same_values:
#                         if is_occur_body(same_value_var,body_list):
#
#
#                             if len(a)>1 and flag:
#                                 real_assign_list.append(a)
#                             a=[ass]
#                             if ind!=len(assign_list[1:])-1:
#                                 flag = 0
#                             is_occur=1
#                             break
#                     else:
#                         flag = 1
#                         a.append(ass)
#
#
#                 else:
#
#                     if len(a) > 1 and flag:
#                         real_assign_list.append(a)
#
#                     a = [ass]
#                     if ind != len(assign_list[1:]) - 1:
#                         flag = 0
#
#                     # continue
#                 pre_same_values.append(ast.unparse(ass.targets[0]))
#
#             else:
#                 print("it is not intersect")
#                 new_write_vars = []
#                 visit_vars(ass.targets[0], new_write_vars)
#                 all_write_vars.append(new_write_vars)
#                 pre_same_values.append(ast.unparse(ass.targets[0]))
#                 a.append(ass)
#         if len(a)>1 and flag:
#             real_assign_list.append(a)
#
#
#
#     return real_assign_list
#     pass
def transform_multiple_assign_code(content):
    code_pair_list = []
    # print(content)
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
            # assign_list = split_assignments_overlap_read_write(all_assign_list, all_body_list)
            assign_list = split_assignments(all_assign_list, all_body_list)
            # print(">>>>>>>>>>>>>>come here: ",assign_list)


            for ind_ass, each_assign_list in enumerate(assign_list):
                # print(">>>>>>ind_ass: ", ind_ass)
                each_assign_list_str = "\n".join([ast.unparse(e_ass) for e_ass in each_assign_list])
                line_list =[[e_ass.lineno, e_ass.end_lineno] for e_ass in each_assign_list]
                # line_list.append([[e_ass.lineno, e_ass.end_lineno] for e_ass in each_assign_list])
                new_code = transform_multiple_assign(each_assign_list)

                # new_file_content = replace_file_content_ass(content, each_assign_list, new_code)
                # assign_list[ind_ass].append(new_code)
                # complic_code_me_info_dir_pkl = util.data_root + "complic_code_me_info_dir_pkl/each_idiom_type_all_methods/multi_ass/"  # for_else
                # util.save_file(complic_code_me_info_dir_pkl, "test"+str(ind_ass), new_file_content, ".txt", "w")
                # util.save_file(complic_code_me_info_dir_pkl, "test_old"+str(ind_ass), content, ".txt", "w")

                code_pair_list.append([class_name,me_name,each_assign_list_str, new_code,line_list])

        return code_pair_list

    except:
        traceback.print_exc()
        return code_pair_list


def get_multiple_assign(tree):

    assign_list = []
    body_list = []
    for e_trr in ast.walk(tree):
        if hasattr(e_trr, "body") :
            body = e_trr.body
            if not isinstance(body,list):
                continue
            # print("body: ",ast.unparse(e_trr),ast.unparse(body))

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
            # print("body: ",ast.unparse(e_trr),ast.unparse(body))

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
# def save_repo_for_else_complicated(repo_name):
#     start=time.time()
#     count_complicated_code = 0
#     print("come the repo: ", repo_name)
#     dict_file=dict()
#
#
#     for ind,file_info in enumerate(dict_repo_file_python[repo_name]):
#         file_path = file_info["file_path"]
#         # if file_path!="/mnt/zejun/smp/data/python_repo_1000/VideoPose3D//run.py":
#         #     continue
#         file_html = file_info["file_html"]
#         # print(file_html)
#         if "bm_scimark.py" not in file_html:
#             continue
#         # if file_html!="https://github.com/devbisme/skidl/tree/master/skidl/netlist_to_skidl.py":#"https://github.com/akfamily/akshare/tree/master/akshare/cost/cost_living.py":##"https://github.com/mitmproxy/mitmproxy/tree/master/mitmproxy/net/http/url.py":#"https://github.com/localstack/localstack/tree/master/localstack/utils/aws/aws_responses.py":#"https://github.com/encode/django-rest-framework/tree/master/rest_framework/utils/urls.py":#"https://github.com/spulec/moto/tree/master/moto/utilities/docker_utilities.py":#"https://github.com/mitmproxy/mitmproxy/tree/master/mitmproxy/net/http/url.py":#"https://github.com/docker/docker-py/tree/master/docker/models/services.py":#"https://github.com/mitmproxy/mitmproxy/tree/master/mitmproxy/net/http/url.py":#"https://github.com/facebookresearch/Detectron/tree/master/detectron/modeling/detector.py":#"https://github.com/chainer/chainer/tree/master/chainer/functions/normalization/group_normalization.py":
#         #     continue
#         print(file_html)
#         try:
#             content = util.load_file_path(file_path)
#         except:
#             print(f"{file_path} is not existed!")
#             continue
#
#         # print("content: ",content)
#         try:
#             file_tree = ast.parse(content)
#             ana_py = ast_util.Fun_Analyzer()
#             ana_py.visit(file_tree)
#             dict_class=dict()
#             for tree, class_name in ana_py.func_def_list:
#
#                 all_assign_list, all_body_list = get_multiple_assign(tree)
#                 # assign_list = split_assignments_overlap_read_write(all_assign_list, all_body_list)
#                 assign_list = split_assignments(all_assign_list, all_body_list)
#                 # print(">>>>>>>>>>>>>>come here: ",assign_list)
#                 new_code_list = []
#                 for ind_ass, each_assign_list in enumerate(assign_list):
#                     # print(">>>>>>ind_ass: ", ind_ass)
#                     for e_ass in each_assign_list:
#                         print("e_ass: ",e_ass,ast.unparse(e_ass))
#                     new_code = transform_multiple_assign(each_assign_list)
#                     print("new_code: ",new_code)
#                     # new_file_content = replace_file_content_ass(content, each_assign_list, new_code)
#                     # assign_list[ind_ass].append(new_code)
#                     # complic_code_me_info_dir_pkl = util.data_root + "complic_code_me_info_dir_pkl/each_idiom_type_all_methods/multi_ass/"  # for_else
#                     # util.save_file(complic_code_me_info_dir_pkl, "test"+str(ind_ass), new_file_content, ".txt", "w")
#                     # util.save_file(complic_code_me_info_dir_pkl, "test_old"+str(ind_ass), content, ".txt", "w")
#
#                     new_code_list.append([each_assign_list, new_code])
#                 if new_code_list:
#                     ast_util.set_dict_class_code_list(tree, dict_class, class_name, new_code_list)
#
#
#
#             dict_file[file_html]=dict_class
#
#             # if code_list:
#             #     one_repo_for_else_code_list.append([code_list, file_path, file_html])
#                 # if len(one_repo_for_else_code_list)>2:
#                 #     break
#
#         except SyntaxError:
#             print("the file has syntax error")
#             continue
#         except ValueError:
#             traceback.print_exc()
#             print("the file has value error: ", file_html)  # content,
#             continue
#         except:
#             traceback.print_exc()
#         # break
#     end = time.time()
#     #'''
#     if dict_file:
#         # count_complicated_code = count_complicated_code + len(one_repo_for_else_code_list)
#         print("it exists for else complicated code1")
#         # util.save_pkl(save_complicated_code_dir_pkl, repo_name, dict_file)
#         # util.save_json(save_complicated_code_dir, repo_name, one_repo_for_else_code_list)
#         print(end-start," save successfully! ", save_complicated_code_dir_pkl + repo_name)
#     else:
#         print(end-start," the repo has no for else")
#         # util.save_pkl(save_complicated_code_dir_pkl, repo_name, dict_file)
#         # util.save_json(save_complicated_code_dir, repo_name, one_repo_for_else_code_list)
#     #'''
#     return count_complicated_code

if __name__ == '__main__':
    code='''
self.a=1
b=self.call(2)
url = urllib.parse.urlsplit(url)

url = list(url)

url[3] = urllib.parse.quote(url[3])

url = urllib.parse.urlunsplit(url)

response = BaseResponse()

response.querystring = qs_data

result = response._get_multi_param(top_level_attribute, skip_result_conversion=True)
(scheme, netloc, path, query, fragment) = parse.urlsplit(force_str(url))

query_dict = parse.parse_qs(query, keep_blank_values=True)

query_dict[force_str(key)] = [force_str(val)]

query = parse.urlencode(sorted(query_dict.items()), doseq=True)
a[0]=1
b=a[1]

# code_obj = BytesIO(blobdata)
# self._tar = tarfile.open(fileobj=code_obj, mode='r:gz')
# info_str = self._tar.extractfile('INFO').read().decode('utf-8')
# self._info = json.loads(info_str)

# serializer_class_store = self.serializer_class
# self.serializer_class = self.copy_return_serializer_class
# ret = self.get_serializer(*args, **kwargs)
# self.serializer_class = serializer_class_store

canvas = self.canvas
self.canvas = self.fbo
ret = super(FboFloatLayout, self).add_widget(*args, **kwargs)
self.canvas = canvas

# if_return_trans = module.return_transform
# if_return_label = module.return_label
# module.return_transform = False
# module.return_label = False
# out = module(*args, **kwargs)
# module.return_transform = if_return_trans
# module.return_label = if_return_label

self._load_model = self.model is not None
__model = self.model
self.model = None
path = super().save(path=path, verbose=verbose)
self.model = __model

e = throttling_mod_func(d, e)#https://github.com/pytube/pytube/blob/f06e0710dcf5089e582487fee94f7bb0afbf7ba9/pytube/cipher.py#L606-L611
f = d[0]
d[0] = d[e]
d[e] = f

container_spec = ContainerSpec(**container_spec_kwargs)

task_template_kwargs['container_spec'] = container_spec

create_kwargs['task_template'] = TaskTemplate(**task_template_kwargs)
#https://github.com/ansible/ansible/blob/a71ba817b0f7d75ff848000226ed5241c791f476/test/support/integration/plugins/module_utils/network/common/utils.py#L591-L594
# params = basic._ANSIBLE_ARGS
# basic._ANSIBLE_ARGS = to_bytes(json.dumps({'ANSIBLE_MODULE_ARGS': data}))
# validated_data = basic.AnsibleModule(spec).params
# basic._ANSIBLE_ARGS = params

# tmp_real = data[ii]
# tmp_imag = data[ii + 1]
# data[ii] = data[jj]
# data[ii + 1] = data[jj + 1]
# data[jj] = tmp_real
# data[jj + 1] = tmp_imag

# hidden_states = residual + hidden_states
# residual = hidden_states
# hidden_states = self.layer_norm2(hidden_states)
# integral_w = paddle.concat(result_w, axis=0)

# model_b = SimpleEmbedding(vocab_size, hidden_size, integral_w)
# 
# optimizer_a = paddle.optimizer.SGD(learning_rate=0.001,
#                                    parameters=model_a.parameters())
# 
# optimizer_b = paddle.optimizer.SGD(learning_rate=0.001,
#                                    parameters=model_b.parameters())
# for _ in range(5):
#             output_a = model_a(input_data)
#             func(a)
#             output_b = model_b(input_data)
           
# a=1
# b=1
# c=b
# src_polys = np.array(src_polys)
# src_polys[:, :, 0] = np.clip(src_polys[:, :, 0], 0, w)
# src_polys[:, :, 1] = np.clip(src_polys[:, :, 1], 0, h)
# data['image'] = src_img
# data['polys'] = src_polys
# data['ignore_tags'] = np.array(src_ignores)
# exc = vim.fault.NoPermission()
# exc.privilegeId = "Fake privilege"
# self.mock_prof_mgr.QueryProfile = MagicMock(side_effect=exc)
# with self.assertRaises(VMwareApiError) as excinfo:
#     salt.utils.pbm.get_storage_policies(self.mock_prof_mgr)
# b = np.arange(12).reshape((3, 4))
# a = da.from_array(c, 1)
# c=1
# _assert(a, b)
# _assert(a, b, 0)
# _assert(a, b, 1)
# _assert(a, b, -1)

# b = np.arange(8).reshape((2, 2, 2))
# a = da.from_array(b, 2)
# lambda x: list(x)[0]
# a=2
# if label_names:
#     # a=2
#     num_tensors_in_label = len(label_names)
# else:
#     num_tensors_in_label = int(has_labels)
# #a,b=1,2
# eeeeee,a=1,2
# b=c.b+1
# for i in range(1):
#         c=1
#         d=2
#         e=3
#         for i in range(2):
#             f=1
#             r=0
#             c=2
# if self . get_conf_value ( 'show' , header = header ) == [ ] :
#     pass
# elif stats_grab == { } :
#     pass
# assert policy . remember ( pretend . stub ( ) , pretend . stub ( ) ) == 0
# d=0
# a.b=func()
# 
# for backend in ["auto", "cv2", "skimage"]:
#     with self.subTest(backend=backend):
#         aug = iaa.Affine(rotate=45, fit_output=True,
#                          backend=backend)
#         _labels, nb_labels = skimage.morphology.label(
#             img_aug > 240, return_num=True, connectivity=2)
#         img = np.zeros((10, 10), dtype=np.uint8)
#         img[0:2, 0:2] = 255
#         img[-2:, 0:2] = 255
#         img[0:2, -2:] = 255
#         img[-2:, -2:] = 255
# 
#         img_aug = aug.augment_image(img)
# 
#         _labels, nb_labels = skimage.morphology.label(
#             img_aug > 240, return_num=True, connectivity=2)
#         assert nb_labels == 4
# while a!=[]:
#     w=1
#     d=w+1
#     for i in range(1):
#         c=1
#         d=2
#         e=3
#         for i in range(2):
#             f=1
#             r=0
#             c=2
#         a=1
#         b=func()
#         c=2
#     pass
# class TPUEstimatorSpec(model_fn_lib._TPUEstimatorSpec):
#     def __new__(cls,
#               mode,
#               predictions=None,
#               loss=None,
#               train_op=None,
#               eval_metrics=None,
#               export_outputs=None,
#               scaffold_fn=None,
#               host_call=None,
#               training_hooks=None,
#               evaluation_hooks=None,
#               prediction_hooks=None):
#         """Creates a validated `TPUEstimatorSpec` instance."""
#         host_calls = {}
#         if eval_metrics is not None:
#           host_calls['eval_metrics'] = eval_metrics
#         if host_call is not None:
#           host_calls['host_call'] = host_call
#         _OutfeedHostCall.validate(host_calls)
#     
#         training_hooks = list(training_hooks or [])
#         evaluation_hooks = list(evaluation_hooks or [])
#         prediction_hooks = list(prediction_hooks or [])
#     lambda x: list(x)[0]
#         for hook in training_hooks + evaluation_hooks + prediction_hooks:
#           if not isinstance(hook, session_run_hook.SessionRunHook):
#             raise TypeError(
#                 'All hooks must be SessionRunHook instances, given: {}'.format(
#                     hook))
#     
#         return super(TPUEstimatorSpec, cls).__new__(
#             cls,
#             mode=mode,
#             predictions=predictions,
#             loss=loss,
#             train_op=train_op,
#             eval_metrics=eval_metrics,
#             export_outputs=export_outputs,
#             scaffold_fn=scaffold_fn,
#             host_call=host_call,
#             training_hooks=training_hooks,
#             evaluation_hooks=evaluation_hooks,
#             prediction_hooks=prediction_hooks)
'''
    '''
    tree = ast.parse(code1)
    code_list=[]
    all_assign_list,all_body_list = get_multiple_assign(tree)
    print(all_assign_list,all_body_list)
    # real_ass_list=split_assignments_overlap_read_write(all_assign_list, all_body_list)
    real_ass_list=split_assignments(all_assign_list, all_body_list)
    for ind_ass, each_assign_list in enumerate(real_ass_list):
        a = []
        for node in each_assign_list:
            a.append(ast.unparse(node))
            # print("come here: ", a.append(ast.unparse(node)))
        if a:
            # print(a)
            code_list.append(a)
    for code1 in code_list:
        print("code1: ",code1)
    print(">>>>>end")
    '''

    '''
    save_complicated_code_dir = util.data_root + "complicated_code_dir/multip_assign_complicated_single_target/"
    
    dict_repo_file_python = util.load_json(util.data_root, "python3_repos_files_info")

    count_complicated_code = 0
    for ind, repo_name in enumerate(dict_repo_file_python):
        #print(ind)
        
        one_repo_mult_assign_code_list = []
        for file_info in dict_repo_file_python[repo_name]:
            file_path = file_info["file_path"]
            file_html = file_info["file_html"]
            content = util.load_file(file_path)
            try:
                # if 1:
                tree = ast.parse(content)
                layer_node_list = []
                ast_util.extract_ast_cur_layer_node(tree,layer_node_list)
                all_assign_list = get_multiple_assign(layer_node_list)
                all_assign_str_list =[]
                for assign_list in all_assign_list:
                    for ind_ass, each_assign_list in enumerate(assign_list):
                        a=[]
                        for node in each_assign_list:
                            a.append(ast.unparse(node))
                            # print("come here: ", a.append(ast.unparse(node)))
                        if a:
                            all_assign_str_list.append(a)
                
                count_complicated_code += len(all_assign_list)
                if all_assign_list:
                    one_repo_mult_assign_code_list.append(
                        [all_assign_str_list, file_path, file_html])
                    # print("one_file_truth_value_test_code_list: ",one_file_truth_value_test_code_list)
                    # break
            except SyntaxError:
                print("the file has syntax error")
                continue
        if one_repo_mult_assign_code_list:
            # print("it exists truth value test complicated code1: ", len(one_repo_for_else_code_list))
            util.save_json(save_complicated_code_dir, repo_name, one_repo_mult_assign_code_list)
        
    print("count_complicated_code: ", ind, count_complicated_code)
    '''
    '''
    tree=ast.parse(code1)
    all_assign_list, all_body_list = get_multiple_assign(tree)
    # print("all_assign_list: ",all_assign_list)
    # assign_list = split_assignments_overlap_read_write(all_assign_list, all_body_list)
    assign_list = split_assignments(all_assign_list, all_body_list)
    # print("come here")
    new_code_list = []
    for ind_ass, each_assign_list in enumerate(assign_list):
        print(">>>>>>ind_ass: ", ind_ass)
        for e_ass in each_assign_list:
            print("e_ass: ", e_ass, ast.unparse(e_ass))
        new_code = transform_multiple_assign(each_assign_list)
        print("new_code: ", new_code)
    '''

    # ana_py = Analyzer()
    # ana_py.visit(file_tree)
    # print("fun number: ",len(ana_py.func_def_list))
    # beg_time=time.time()
    # save_complicated_code_dir= util.data_root + "complicated_code_dir/multip_assign_complicated_json/"
    # save_complicated_code_dir_pkl= util.data_root + "transform_complicate_to_simple_pkl/multip_assign_complicated/"
    # # save_complicated_code_dir_pkl=util.data_root +"transform_complicate_to_simple_pkl/var_unpack_for_target_complicated/"
    #
    # # dict_repo_file_python=util.load_json(util.data_root, "python3_repos_files_info" )
    # dict_repo_file_python= util.load_json(util.data_root, "python3_1000repos_files_info")
    #
    # repo_name_list=[]
    # for repo_name in dict_repo_file_python:
    #
    #     # if os.path.exists(save_complicated_code_dir_pkl + repo_name + ".pkl"):
    #     #     continue
    #     if repo_name!="pyperformance":#"pytube":#"skidl":#"akshare":#"mitmproxy":#"localstack":#"django-rest-framework":#"moto":#"docker-py":#"cloud-custodian":#"mitmproxy":#"mitmproxy":
    #         continue
    #
    #     repo_name_list.append(repo_name)
    # print("repo_name_list:",repo_name_list)
    # save_repo_for_else_complicated(repo_name_list[0])
    '''
    count_complicated_code=0
    for ind,repo_name in enumerate(dict_repo_file_python):
        one_repo_truth_value_test_code_list = []
        for file_info in dict_repo_file_python[repo_name]:
            file_path = file_info["file_path"]
            file_html = file_info["file_html"]
            content = util.load_file(file_path)
            try:
            #if 1:
                one_file_truth_value_test_code_list=get_truth_value_test(content)
                count_complicated_code+=len(one_file_truth_value_test_code_list)
                if one_file_truth_value_test_code_list:
                    one_repo_truth_value_test_code_list.append([one_file_truth_value_test_code_list, file_path, file_html])
                    # print("one_file_truth_value_test_code_list: ",one_file_truth_value_test_code_list)
                    # break
            except SyntaxError:
                print("the file has syntax error")
                continue
            # break
        if one_repo_truth_value_test_code_list:
            # print("it exists truth value test complicated code1: ", len(one_repo_for_else_code_list))
            util.save_json(save_complicated_code_dir, repo_name, one_repo_truth_value_test_code_list)

        # break
    # print()


        # break
    print("count_complicated_code: ",ind,count_complicated_code)
    
    '''
    '''
    pool = newPool(nodes=30)
    pool.map(save_repo_for_else_complicated, repo_name_list)  # [:3]sample_repo_url ,token_num_list[:1]
    pool.close()
    pool.join()
    end_time = time.time()
    print("time of extracting all complicated code1: ", end_time-beg_time,len(repo_name_list))
    '''
    #'''

    # files_num_list = []
    # star_num_list = []
    # contributor_num_list = []
    # count_repo, file_count, me_count, code_count = 0, 0, 0, 0
    # file_list = set([])
    # repo_code_num = dict()
    # result_compli_for_else_list = []
    # all_count_repo, all_file_count, all_me_count = 0, 0, 0
    # for file_name in os.listdir(save_complicated_code_dir_pkl):
    #     all_count_repo += 1
    #     repo_name = file_name[:-4]
    #     # files_num_list.append(repo_files_info[repo_name])
    #     # star_num_list.append(repo_star_info[repo_name])
    #     # contributor_num_list.append(repo_contributor_info[repo_name])
    #
    #     complicate_code = util.load_pkl(save_complicated_code_dir_pkl, repo_name)
    #
    #     repo_file_count, repo_me_count, repo_code_count, repo_all_file_count, repo_all_me_count = complicated_code_util.get_code_count(
    #         complicate_code)
    #     # for code_list, file_path, file_html in complicate_code:
    #     code_count += repo_code_count
    #     file_count += repo_file_count
    #     me_count += repo_me_count
    #     all_file_count += repo_all_file_count
    #     all_me_count += repo_all_me_count
    #     repo_exist = 0
    #     for file_html in complicate_code:
    #         for cl in complicate_code[file_html]:
    #             for me in complicate_code[file_html][cl]:
    #                 if complicate_code[file_html][cl][me]:
    #                     repo_exist = 1
    #                     for code in complicate_code[file_html][cl][me]:
    #                         # print("html: ",file_html,cl,me,ast.unparse(code1[0]))
    #                         #                code_index_start_end_list.append([node,assign_stmt,node.lineno, node.end_lineno,assign_stmt_lineno,assign_block_list_str])
    #                         ass_str=[]
    #                         for ass in code[0]:
    #                             ass_str.append(ast.unparse(ass))
    #
    #                         result_compli_for_else_list.append(
    #                             [repo_name, file_html, cl, me,code[0][0].lineno, "\n".join(ass_str), code[1]])
    #
    #         # print(f"{file_html} of {repo_name} has  {len(code_list)} code1 fragments")
    #     count_repo += repo_exist
    #
    # # a=dict(sorted(repo_code_num.items(), key=lambda item: item[1], reverse=True))
    # # print(a)
    # # print(np.median(list(a.values())), np.max(list(a.values())), np.min(list(a.values())))
    # # print(np.median(files_num_list), np.max(files_num_list), np.min(files_num_list))
    # # print(np.median(star_num_list), np.max(star_num_list), np.min(star_num_list))
    # # print(np.median(contributor_num_list), np.max(contributor_num_list), np.min(contributor_num_list))
    # print("count: ", count_repo, code_count, file_count, me_count, all_count_repo, all_file_count, all_me_count)
    # import random

    # random.shuffle(result_compli_for_else_list)
    # util.save_csv(util.data_root + "result_csv/multiple_assign.csv",
    #               result_compli_for_else_list[:400],
    #               ["repo_name", "file_html", "class_name", "me_name","line_no", "old_code", "new_code"])

    # 1 156 2943 100 1 2990 40102 salt
    # 791 2010 103165 1291 800 121348 1192868
    # util.save_csv(util.data_root + "multiple_ass_complicated.csv",
    #               result_compli_for_else_list,
    #               ["repo_name", "file_html", "class_name", "me_name", "for_code", "assign_code"])

# import random
    # random.shuffle(result_compli_for_else_list)
    # util.save_csv(util.data_root+"complicated_code_dir/multip_assign_complicated_sample.csv",result_compli_for_else_list[:385],["repo_name","code1","file_html","file_path"])
   #'''











    # print("----------------------------\n")
    # for code1 in for_else_filter_redundant_code_list:
    #     print("each code1: ", code1[0])
