import sys,ast
import tokenize
# sys.path.append("/Users/zhangzejunzhangzejun/PycharmProjects/pythonProject/python-ast-explorer-master/extract_transform_complicate_code_new/comprehension/")

import extract_compli_for_comprehension_logic
from RefactoringIdioms.extract_simp_cmpl_data import ast_util
from RefactoringIdioms.transform_c_s import transform_comprehension_dict_compli_to_simple
from tokenize import tokenize
from io import BytesIO
# from pathos.multiprocessing import ProcessingPool as newPool
import traceback
'''
get comprehension node
Block=> Assign;...; For
For=>”for” ( For| If|If-else|body)
If=>”if” (body| For| If| If-else)
If-else=>”if” body “else” (body| If-else)
body=> (Assign|Call)*;Append*
并且里面只有一个写变量
for

    b.append()
    
    a.append(b)

'''

const_empty_list=[" = dict()"," = {}"]


def get_var(one_body):
    var_name=None
    if isinstance(one_body, ast.Assign):
        targets = one_body.targets
        if len(targets) > 1:
            return False

        left_node = targets[0]
        if isinstance(left_node, ast.Subscript):
            var_name=ast.unparse(left_node.value)
    return var_name



def whether_fun_is_append(one_body,assign_block_list):
    #print("one_body: ",ast.unparse(one_body),one_body.__dict__)
    if isinstance(one_body, ast.Assign):
        #print("come here")
        targets=one_body.targets
        if len(targets)>1:
            return False
        left_node=targets[0]
        if isinstance(left_node, ast.Subscript):
            assign_block_list.append([one_body])
            return True
    return False
def is_use_var(next_child, vars):
    s = ast.unparse(next_child)
    if s != list(vars)[0]:
        g = tokenize(BytesIO(s.encode('utf-8')).readline)  # tokenize the string
        for toknum, to_child, _, _, _ in g:
            if to_child.strip() == list(vars)[0]:
                return 1
    return 0
def whether_first_var_is_empty_assign(tree,for_node,vars,const_empty_list=["[]"]):
    assign_stmt=None
    assign_stmt_lineno=None
    flag=0
    # start_lineno=0
    # print("the var: ",vars)

    def visit_single_vars(target, list_vars):
        # print(">>>>>>>target: ",target.__dict__)
        if isinstance(target, (ast.Name)):
            list_vars.append(ast.unparse(target))
        elif isinstance(target, ast.Subscript):
            list_vars.append(ast.unparse(target))
            visit_single_vars(target.value, list_vars)
        elif isinstance(target, ast.Attribute):
            # print("attr: ", ast.unparse(target))
            list_vars.append(ast.unparse(target))
            visit_single_vars(target.value, list_vars)

    def get_time_var(vars):
        all_var_list = []
        for ind,e_var in enumerate(ast.walk(ast.parse(list(vars)[0]))):

            if ast.unparse(e_var)==list(vars)[0] and isinstance(e_var,(ast.Subscript,ast.Attribute,ast.Name)):
                # print("var: ",e_var,ast.unparse(e_var))
                visit_single_vars(e_var, all_var_list)
                break
        return all_var_list
    def whether_contain_var(node,vars,time_var_list):
        count=0
        s = ast.unparse(node)
        if s != list(vars)[0]:
            g = tokenize(BytesIO(s.encode('utf-8')).readline)  # tokenize the string

            for toknum, child, _, _, _ in g:
                if child in time_var_list:
                    count+=1
                    # print("yes use more than one time: ", s)
        return count

    time_var_list = get_time_var(vars)
    remove_ass_flag = 0
    time=whether_contain_var(for_node,vars, time_var_list)

    append_time = 0
    for child in ast.walk(for_node):

        # if ast.unparse(child)==list(vars)[0]:
        #     time+=1
        #     if time-append_time > 0:
        #         print("come here the for node use var more than one time ",list(vars)[0])
        #         flag = 1
        #         break
        if isinstance(child,ast.Assign):
            a = []
            append_time += whether_fun_is_append(child, a)
        if isinstance(child, ast.Call):

            def is_call_use_vars(tree, fun_name, time_var_list):
                # print(">>>>>>.come is_call_use_vars: ", fun_name)
                ana_py_fun = ast_util.Fun_Analyzer()
                ana_py_fun.visit(tree)
                for tree_fun, class_name in ana_py_fun.func_def_list:
                    if hasattr(tree_fun, "name"):
                        each_fun_name = tree_fun.name
                        # print(">>>>>>each_fun_name: ", fun_name)
                        if each_fun_name == fun_name:
                            for child in ast.walk(tree_fun):
                                if ast.unparse(child) in time_var_list:
                                    # print("yes the call use vars: ", each_fun_name)
                                    return 1
                return 0

            fun_name = ast.unparse(child.func).split(".")[-1]
            call_use_var_flag = is_call_use_vars(tree, fun_name, time_var_list)
            if call_use_var_flag:
                flag = 1
                return flag, assign_stmt_lineno, assign_stmt,remove_ass_flag
        # time += whether_contain_var(child, vars)
    if time - append_time > 0:
            # print("come here the for node use var more than one time ", list(vars)[0])
            flag = 1
            return flag, assign_stmt_lineno, assign_stmt,remove_ass_flag
            # break
    for_node_block_record=None
    for node in ast.walk(tree):


        if hasattr(node,"lineno") and node.lineno==for_node.lineno:
            break
        if hasattr(node, 'body') and isinstance(node.body, list) and \
                ((hasattr(node, 'lineno') and node.lineno < for_node.lineno <= node.end_lineno) or (
                        hasattr(node.body[0], 'lineno') and node.body[0].lineno < for_node.lineno < node.body[
                    -1].end_lineno)):
            for child in node.body:
                # print("come here node: ",child,ast.unparse(child),isinstance(child,ast.Expr))

                if isinstance(child, ast.Assign):
                    if ast.unparse(child).strip().split("=")[0].strip() == list(vars)[0] and ast.unparse(child.value) in const_empty_list:
                        assign_stmt = child
                        assign_stmt_lineno = child.lineno
                        ass_block_end_lineno=node.end_lineno if hasattr(node,'lineno') else node.body[0].lineno
                        # if ass_block_end_lineno < for_node.lineno:
                        #     remove_ass_flag = 0

                        for_node_block_record = node
                        flag = 2
    if for_node_block_record:
        # print(">>>>>>>come here for_node_block_record:\n ",ast.unparse(for_node_block_record))
        for child in ast.iter_child_nodes(for_node_block_record):  # .body:
            if child == for_node:
                remove_ass_flag = 1
        for node in ast.walk(for_node_block_record):
            # 在ass和for_node之间不可以使用变量vars
            if hasattr(node, "end_lineno") and hasattr(node, "lineno"):
                if node != assign_stmt and node.end_lineno < for_node.lineno and node.lineno > assign_stmt_lineno:
                    s = ast.unparse(node)

                    if s != list(vars)[0]:
                        g = tokenize(BytesIO(s.encode('utf-8')).readline)  # tokenize the string
                        for toknum, child, _, _, _ in g:
                            if child.strip() in time_var_list:  # list(vars)[0]:
                                flag = 1
                                # print("yes use more than one time: ",vars,s,"\n>>>>>>>>>",ast.unparse(for_node))
                                return flag, assign_stmt_lineno, assign_stmt, remove_ass_flag
            if isinstance(node, (ast.For, ast.While,
                                 ast.AsyncFor)) and for_node.lineno > node.lineno > assign_stmt.lineno and node.end_lineno >= for_node.end_lineno:
                # print(">>>>>>>>come here ")
                return 1, assign_stmt_lineno, assign_stmt, remove_ass_flag

    else:
        return 1, assign_stmt_lineno, assign_stmt, remove_ass_flag

            # if s!=list(vars)[0]:
            #     g = tokenize(BytesIO(s.encode('utf-8')).readline)  # tokenize the string
            #     for toknum, child, _, _, _ in g:
            #         if child.strip() == list(vars)[0]:
            #             flag = 1
            #             # print("yes use more than one time: ",vars,s,"\n>>>>>>>>>",ast.unparse(for_node))
            #             break
            #     if flag==1:
            #         break

    return flag,assign_stmt_lineno,assign_stmt,remove_ass_flag
'''
def whether_first_var_is_empty_assign(tree,for_node,vars,const_empty_list=["[]"]):
    assign_stmt=None
    assign_stmt_lineno=None
    flag=0
    # start_lineno=0
    # print("the var: ",vars)


    def whether_contain_var(node,vars):
        count=0
        s = ast.unparse(node)
        if s != list(vars)[0]:
            g = tokenize(BytesIO(s.encode('utf-8')).readline)  # tokenize the string

            for toknum, child, _, _, _ in g:
                if child == list(vars)[0]:
                    count+=1
                    # print("yes use more than one time: ", s)
        return count

    time=whether_contain_var(for_node, vars)
    append_time = 0
    for child in ast.walk(for_node):

        # if ast.unparse(child)==list(vars)[0]:
        #     time+=1
        #     if time-append_time > 0:
        #         print("come here the for node use var more than one time ",list(vars)[0])
        #         flag = 1
        #         break
        if isinstance(child,ast.Assign):
            a = []
            append_time += whether_fun_is_append(child, a)
        if isinstance(child, ast.Call):



            def is_call_use_vars(tree, fun_name, vars):
                # print(">>>>>>.come is_call_use_vars: ", fun_name)
                ana_py_fun = ast_util.Fun_Analyzer()
                ana_py_fun.visit(tree)
                for tree_fun, class_name in ana_py_fun.func_def_list:
                    if hasattr(tree_fun,"name"):
                        each_fun_name = tree_fun.name
                        # print(">>>>>>each_fun_name: ", fun_name)
                        if each_fun_name == fun_name:
                            for child in ast.walk(tree_fun):
                                if ast.unparse(child) == list(vars)[0]:
                                    # print("yes the call use vars: ", each_fun_name)
                                    return 1
                return 0

            fun_name = ast.unparse(child.func).split(".")[-1]
            call_use_var_flag = is_call_use_vars(tree, fun_name, vars)
            if call_use_var_flag:
                flag = 1
                return flag, assign_stmt_lineno, assign_stmt
        # time += whether_contain_var(child, vars)
    if time - append_time > 0:
            # print("come here the for node use var more than one time ", list(vars)[0])
            flag = 1
            return flag, assign_stmt_lineno, assign_stmt
            # break
    for node in ast.walk(tree):
        if not hasattr(node,"lineno"):
            continue

        if node.lineno==for_node.lineno:
            break
        if isinstance(node, ast.Assign):
            # print("the assign: ",ast.unparse(node),ast.unparse(node).strip().split("=")[0].strip())
            if ast.unparse(node).strip().split("=")[0].strip()==list(vars)[0] and ast.unparse(node.value) in const_empty_list:
                assign_stmt=node
                assign_stmt_lineno=node.lineno
                flag = 2
        if assign_stmt_lineno and node.end_lineno<for_node.lineno and node.lineno>assign_stmt_lineno :
            s=ast.unparse(node)

            if s!=list(vars)[0]:
                g = tokenize(BytesIO(s.encode('utf-8')).readline)  # tokenize the string
                for toknum, child, _, _, _ in g:
                    if child.strip() == list(vars)[0]:
                        flag = 1
                        # print("yes use more than one time: ",vars,s,"\n>>>>>>>>>",ast.unparse(for_node))
                        break
                if flag==1:
                    break
    return flag,assign_stmt_lineno,assign_stmt
'''
def else_traverse(if_body,assign_block_list):
    else_body_list = if_body.orelse
    if len(else_body_list) > 1:
        return False
    else:
        else_body_one = else_body_list[0]
        if isinstance(else_body_one, ast.If):
            or_else = else_body_one.orelse
            if not or_else:
                return False
            else:
                return if_else_traverse(else_body_one,assign_block_list)
        return whether_fun_is_append(else_body_one,assign_block_list)



def if_else_traverse(if_body,assign_block_list):
    if_body_list=if_body.body
    # else_body_list=if_body.orelse
    if len(if_body_list)==1:
        if_body_flag =whether_fun_is_append(if_body_list[0],assign_block_list)
    else:
        return False
    #print("if body flag: ",if_body_flag)

    return if_body_flag and else_traverse(if_body,assign_block_list)

def if_traverse(one_body,assign_block_list):
    orelse = one_body.orelse
    if_body=one_body.body
    if not orelse:
        return for_traverse(one_body,assign_block_list)
    else:
        #print("it is if-else node: ", ast.unparse(one_body))
        return if_else_traverse(one_body,assign_block_list)


def for_traverse(node,assign_block_list):
    for_body_list = node.body
    if isinstance(node, ast.For) and node.orelse:
        #print("come here")
        return False
    if len(for_body_list) == 1:
        one_body=for_body_list[0]
        if isinstance(one_body, ast.For):
            return for_traverse(one_body,assign_block_list)
        elif isinstance(one_body, ast.If):
            #print("it is if node")
            return if_traverse(one_body,assign_block_list)

        elif isinstance(one_body, ast.Assign):
            #print("it is one stmt")
            return whether_fun_is_append(one_body,assign_block_list)
        else:

            #print("the for/if sentences has other stmts so cannot transform such as try stmt", ast.unparse(one_body),type(one_body))
            return False
    else:
        return False
'''
beg1 end1
beg2 end2
'''


def get_complicated_for_comprehen_code_list(tree,content):

    #tree = ast.parse(code1)
    code_index_start_end_list = []

    start_lineno=1
    #print("tree: ",tree.body[0].__dict__)
    start_lineno=tree.body[0].lineno
    #print("start_lineno: ",start_lineno)
    #code1 = "\n".join(content.split("\n")[start_lineno-1:])

    for ind_line,node in enumerate(ast.walk(tree)):

        if isinstance(node, ast.For):
            #print("node_line: ",ast.unparse(node),node.lineno, node.end_lineno)
            # if node.lineno!=1674:
            #     continue

            assign_block_list=[]
            #print("it is what: ",node.lineno)
            if for_traverse(node,assign_block_list):
                #print("maybe comrephension")
                vars = set([])
                #print("maybe comrephension: ",node.lineno,ast.unparse(assign_block_list[0][0]))
                for each_block in assign_block_list:
                    var_name=get_var(each_block[0])
                    vars.add(var_name)
                if len(vars)!=1:
                    continue
                # print("vars: ",vars,ind_line,start_lineno)
                # print("node: ", ast.unparse(node))
                flag,assign_stmt_lineno,assign_stmt,remove_ass_flag=whether_first_var_is_empty_assign(tree, node, vars,["dict()","{}"])
                # print("flag: ", flag)
                if flag!=2:
                    print("flag: ")#, ast.unparse(node)
                    continue

                assign_block_list_str = []
                for one_block in assign_block_list:
                    one_block_str = []
                    for e in one_block:
                        one_block_str.append(ast.unparse(e))
                    assign_block_list_str.append(one_block_str)
                code_index_start_end_list.append(
                        [node, assign_stmt,remove_ass_flag])#, node.lineno, node.end_lineno, assign_stmt_lineno, assign_block_list_str])

                # print(">>>>>>>>>>>>>>>>>>>>>>it is comprehension code1\n", remove_ass_flag,node.lineno, node.end_lineno,assign_stmt_lineno,ast.unparse(node))
                # code_index_start_end_list.append([ast.unparse(node), node.lineno, node.end_lineno,assign_stmt_lineno,assign_block_list_str])
    #print("len: ", len(code_index_start_end_list))
    code_index_start_end_list = extract_compli_for_comprehension_logic.filter_overlap(code_index_start_end_list)
    # code_index_start_end_list = filter_overlap(code_index_start_end_list)
    # print("len: ",len(code_index_start_end_list))
    return code_index_start_end_list
def get_dict_compreh(content):
    code_pair_list=[]
    # print(content)

    try:

        file_tree = ast.parse(content)
        ana_py = ast_util.Fun_Analyzer()
        ana_py.visit(file_tree)
        # print("come here",ana_py.func_def_list)
        for tree, class_name in ana_py.func_def_list:
            # print("come method",ast.unparse(tree))
            try:
                me_name = tree.name
            except:
                me_name = ""
            new_code_list = get_complicated_for_comprehen_code_list(tree, content)

            for ind, (for_node, assign_node, remove_ass_flag) in enumerate(new_code_list):
                new_code= transform_comprehension_dict_compli_to_simple.transform(for_node, assign_node)
                complete_new_code=ast.unparse(new_code) if remove_ass_flag else ast.unparse(assign_node) + "\n"+ast.unparse(new_code)
                line_list = []
                line_list.append([assign_node.lineno, assign_node.end_lineno])
                line_list.append([for_node.lineno, for_node.end_lineno])
                code_pair_list.append([class_name,me_name,ast.unparse(assign_node) + "\n" + ast.unparse(for_node), complete_new_code,line_list])
        return code_pair_list

    except:
        traceback.print_exc()
        return code_pair_list
# def save_one_repo(repo_name):
#     count=0
#     one_repo_chained_comparison_code_list = []
#     dict_file = dict()
#     for file_info in dict_repo_file_python[repo_name]:
#         file_path = file_info["file_path"]
#         file_html = file_info["file_html"]
#         # if file_html != "https://github.com/networkx/networkx/tree/master/networkx/algorithms/connectivity/kcomponents.py":#"https://github.com/IDSIA/sacred/tree/master/sacred/observers/mongo.py":  # "https://github.com/cloud-custodian/cloud-custodian/tree/master/c7n/provider.py":#"https://github.com/networkx/networkx/tree/master/networkx/generators/joint_degree_seq.py":#"https://github.com/bndr/pipreqs/tree/master/pipreqs/pipreqs.py":#"https://github.com/amperser/proselint/tree/master/proselint/tools.py":#"https://github.com/networkx/networkx/tree/master/networkx/readwrite/json_graph/adjacency.py":##"https://github.com/microsoft/nni/tree/master/nni/tools/nnictl/nnictl_utils.py":#"https://github.com/networkx/networkx/tree/master/networkx/readwrite/json_graph/adjacency.py":#"https://github.com/amperser/proselint/tree/master/proselint/tools.py":#"https://github.com/aws/aws-cli/tree/master/awscli/customizations/s3/subcommands.py":#"https://github.com/nccgroup/ScoutSuite/tree/master/ScoutSuite/providers/aws/utils.py":#"https://github.com/microsoft/nni/tree/master/nni/algorithms/hpo/networkmorphism_tuner/graph_transformer.py":#"https://github.com/localstack/localstack/tree/master/localstack/services/awslambda/lambda_api.py":#"https://github.com/localstack/localstack/tree/master/localstack/utils/common.py":#"https://github.com/aws/aws-cli/tree/master/awscli/compat.py":#"https://github.com/spulec/moto/tree/master/moto/config/models.py":#"https://github.com/cookiecutter/cookiecutter/tree/master/cookiecutter/hooks.py":#"https://github.com/yt-dlp/yt-dlp/tree/master/yt_dlp/utils.py":#"https://github.com/ytdl-org/youtube-dl/tree/master/youtube_dl/utils.py":#"https://github.com/OmkarPathak/pygorithm/tree/master/pygorithm/greedy_algorithm/fractional_knapsack.py":#"https://github.com/OmkarPathak/pygorithm/tree/master/pygorithm/strings/anagram.py":#"https://github.com/amperser/proselint/tree/master/proselint/tools.py":#"https://github.com/cloudtools/troposphere/tree/master/troposphere/validators.py":#"https://github.com/pytransitions/transitions/tree/master/transitions/extensions/nesting.py":#"https://github.com/ytdl-org/youtube-dl/tree/master/youtube_dl/utils.py":#"https://github.com/microsoft/nni/tree/master/nni/algorithms/hpo/networkmorphism_tuner/graph_transformer.py":#"https://github.com/amperser/proselint/tree/master/proselint/tools.py":#"https://github.com/sympy/sympy/tree/master/sympy/crypto/crypto.py":#"https://github.com/ytdl-org/youtube-dl/tree/master/youtube_dl/utils.py":#"https://github.com/sympy/sympy/tree/master/sympy/crypto/crypto.py":#"https://github.com/yt-dlp/yt-dlp/tree/master/yt_dlp/utils.py":#"https://github.com/amperser/proselint/tree/master/proselint/tools.py":#"https://github.com/pytransitions/transitions/tree/master/transitions/extensions/nesting.py":#"https://github.com/microsoft/nni/tree/master/nni/algorithms/hpo/networkmorphism_tuner/graph_transformer.py":  # "https://github.com/pymc-devs/pymc/tree/master/pymc/sampling.py":#"https://github.com/smicallef/spiderfoot/tree/master//sflib.py":#"https://github.com/smicallef/spiderfoot/tree/master//sfwebui.py":#
#         #     continue
#         # if file_html != "https://github.com/networkx/networkx/tree/master/networkx/generators/joint_degree_seq.py":  #"https://github.com/cloud-custodian/cloud-custodian/tree/master/c7n/provider.py":  # "https://github.com/networkx/networkx/tree/master/networkx/generators/joint_degree_seq.py":#"https://github.com/bndr/pipreqs/tree/master/pipreqs/pipreqs.py":#"https://github.com/amperser/proselint/tree/master/proselint/tools.py":#"https://github.com/networkx/networkx/tree/master/networkx/readwrite/json_graph/adjacency.py":##"https://github.com/microsoft/nni/tree/master/nni/tools/nnictl/nnictl_utils.py":#"https://github.com/networkx/networkx/tree/master/networkx/readwrite/json_graph/adjacency.py":#"https://github.com/amperser/proselint/tree/master/proselint/tools.py":#"https://github.com/aws/aws-cli/tree/master/awscli/customizations/s3/subcommands.py":#"https://github.com/nccgroup/ScoutSuite/tree/master/ScoutSuite/providers/aws/utils.py":#"https://github.com/microsoft/nni/tree/master/nni/algorithms/hpo/networkmorphism_tuner/graph_transformer.py":#"https://github.com/localstack/localstack/tree/master/localstack/services/awslambda/lambda_api.py":#"https://github.com/localstack/localstack/tree/master/localstack/utils/common.py":#"https://github.com/aws/aws-cli/tree/master/awscli/compat.py":#"https://github.com/spulec/moto/tree/master/moto/config/models.py":#"https://github.com/cookiecutter/cookiecutter/tree/master/cookiecutter/hooks.py":#"https://github.com/yt-dlp/yt-dlp/tree/master/yt_dlp/utils.py":#"https://github.com/ytdl-org/youtube-dl/tree/master/youtube_dl/utils.py":#"https://github.com/OmkarPathak/pygorithm/tree/master/pygorithm/greedy_algorithm/fractional_knapsack.py":#"https://github.com/OmkarPathak/pygorithm/tree/master/pygorithm/strings/anagram.py":#"https://github.com/amperser/proselint/tree/master/proselint/tools.py":#"https://github.com/cloudtools/troposphere/tree/master/troposphere/validators.py":#"https://github.com/pytransitions/transitions/tree/master/transitions/extensions/nesting.py":#"https://github.com/ytdl-org/youtube-dl/tree/master/youtube_dl/utils.py":#"https://github.com/microsoft/nni/tree/master/nni/algorithms/hpo/networkmorphism_tuner/graph_transformer.py":#"https://github.com/amperser/proselint/tree/master/proselint/tools.py":#"https://github.com/sympy/sympy/tree/master/sympy/crypto/crypto.py":#"https://github.com/ytdl-org/youtube-dl/tree/master/youtube_dl/utils.py":#"https://github.com/sympy/sympy/tree/master/sympy/crypto/crypto.py":#"https://github.com/yt-dlp/yt-dlp/tree/master/yt_dlp/utils.py":#"https://github.com/amperser/proselint/tree/master/proselint/tools.py":#"https://github.com/pytransitions/transitions/tree/master/transitions/extensions/nesting.py":#"https://github.com/microsoft/nni/tree/master/nni/algorithms/hpo/networkmorphism_tuner/graph_transformer.py":  # "https://github.com/pymc-devs/pymc/tree/master/pymc/sampling.py":#"https://github.com/smicallef/spiderfoot/tree/master//sflib.py":#"https://github.com/smicallef/spiderfoot/tree/master//sfwebui.py":#
#         #     continue
#         # if file_html!="https://github.com/shuup/shuup/tree/master/shuup_tests/notify/utils.py":#"https://github.com/shuup/shuup/tree/master/shuup/admin/modules/orders/sections.py":#"https://github.com/Diaoul/subliminal/tree/master/subliminal/providers/addic7ed.py":#"https://github.com/capitalone/DataProfiler/tree/master/dataprofiler/profilers/profiler_options.py":#"https://github.com/Axelrod-Python/Axelrod/tree/master/axelrod/classifier.py":#"https://github.com/dpkp/kafka-python/tree/master/kafka/coordinator/assignors/sticky/sticky_assignor.py":#"https://github.com/dpkp/kafka-python/tree/master/kafka/coordinator/assignors/sticky/sticky_assignor.py":#"https://github.com/terraform-compliance/cli/tree/master/terraform_compliance/common/helper.py":#"https://github.com/python-poetry/poetry/tree/master/poetry/puzzle/solver.py":#"https://github.com/Rockyzsu/stock/tree/master//fupan.py":#"https://github.com/OctoPrint/OctoPrint/tree/master/src/octoprint/server/views.py":
#         #     continue
#         print("file_html: ", file_html)
#         try:
#             content = util.load_file_path(file_path)
#         except:
#             print(f"{file_path} is not existed!")
#             continue
#
#         try:
#             file_tree = ast.parse(content)
#             ana_py = ast_util.Fun_Analyzer()
#             ana_py.visit(file_tree)
#             # one_file_chained_comparison_code_list = []
#             #print("func number: ",file_html,len(ana_py.func_def_list))
#             dict_class = dict()
#             for tree, class_name in ana_py.func_def_list:
#                 # if 1:
#                 #print("come here",ast.unparse(tree))
#                 new_code_list = get_complicated_for_comprehen_code_list(tree,content)
#                 for ind, (for_node, assign_node,remove_ass_flag) in enumerate(new_code_list):
#                     new_code_list[ind].append(
#                         transform_comprehension_dict_compli_to_simple.transform(for_node, assign_node))
#                 # for old_code,old_ass,new_code in new_code_list:
#                 #     print("old_code,old_ass,new_code: ",ast.unparse(old_code),old_ass,ast.unparse(new_code))
#
#                 # one_file_chained_comparison_code_list.extend(get_complicated_for_comprehen_code_list(tree,content))
#                 ast_util.set_dict_class_code_list(tree,dict_class, class_name, new_code_list)
#
#                 # count+=len(one_file_chained_comparison_code_list)
#             dict_file[file_html] = dict_class
#             #print(dict_class)
#             # if one_file_chained_comparison_code_list:
#             #     one_repo_chained_comparison_code_list.append(
#             #         [one_file_chained_comparison_code_list, file_path, file_html])
#                 # print("one_file_truth_value_test_code_list: ",one_repo_chained_comparison_code_list)
#                     # break
#         except SyntaxError:
#
#             print("the file has syntax error")
#             continue
#         except ValueError:
#             traceback.print_exc()
#             print("the file has value error: ", file_html)#content,
#             continue
#         except:
#             traceback.print_exc()
#         # break
#     #print("count: ",count)
#     util.save_pkl(save_complicated_code_dir_pkl, repo_name, dict_file)
#     print("save successfully! ", count,save_complicated_code_dir_pkl + repo_name)


if __name__ == '__main__':
    code = '''
# def func_1():
components = {}
for i in range(2):
    print(1)
components['trend'] = get_forecast_component_plotly_props(
    m, fcst, 'trend', uncertainty, plot_cap)
if m.train_holiday_names is not None and 'holidays' in fcst:
    components['holidays'] = get_forecast_component_plotly_props(
        m, fcst, 'holidays', uncertainty)

regressors = {'additive': False, 'multiplicative': False}
for name, props in m.extra_regressors.items():
    regressors[props['mode']] = True
for mode in ['additive', 'multiplicative']:
    if regressors[mode] and 'extra_regressors_{}'.format(mode) in fcst:
        components['extra_regressors_{}'.format(mode)] = get_forecast_component_plotly_props(
            m, fcst, 'extra_regressors_{}'.format(mode))
payload={}
a={}
for field in model.__searchable__:
    for i in range(1):
        payload[field] = getattr(model, field)
'''
    # dict_repo_file_python = util.load_json(util.data_root, "python3_repos_files_info")
    #
    # save_one_repo("Real-Time-Voice-Cloning", code1)

    '''
    # print("code1: ",code1)
    tree = ast.parse(code1)
    #code1 = ast.unparse(tree)
    #print("code1: ", code1)

    code_list=get_complicated_for_comprehen_code_list(tree,code1)
    print("len: ",len(code_list))
    for e in code_list:
        print(">>>>>code1： ", e[0],ast.unparse(e[0]))
        print("block: ", e[-1])
        # for each in  e[-1]:
        #     print(each)

        print("----------END------------")
    '''
    # test_code="a=dict()"
    # test_tree = ast.parse(test_code)
    # print(ast.unparse(test_tree))

    # layer_node_list = []
    # ast_util.extract_ast_cur_layer_node(tree, layer_node_list)
    '''
    get comprehension node
    Block=> Assign;...; For
    For=>”for” ( For| If|If-else|body)
    If=>”if” (body| For| If| If-else)
    If-else=>”if” body “else” (body| If-else)
    body=> (Assign|Call)*;Append*
    '''
    # 对于
    # save_complicated_code_dir_pkl = util.data_root + "transform_complicate_to_simple_pkl/for_compre_dict/"
    # # save_complicated_code_dir = util.data_root + "complicated_code_dir/for_comrephension_dict_complicated_only_one_stmt/"
    # dict_repo_file_python = util.load_json(util.data_root, "python3_1000repos_files_info")
    #
    # #'''
    # # dict_repo_file_python = util.load_json(util.data_root, "python3_1000repos_files_info")
    # repo_list = []
    # for ind, repo_name in enumerate(dict_repo_file_python):
    #     # if repo_name!="shuup":#"subliminal":#"DataProfiler":#"Axelrod":#"kafka-python":#"cli":#"networkx":#"sacred":#"networkx":#"cloud-custodian":#"poetry":#"OctoPrint":#"keras-bert":#"Legofy":
    #     #     continue
    #     # print("repo_name: ", repo_name)
    #     repo_list.append(repo_name)
    # #save_one_repo(repo_list[0])
    # import time
    #
    # start_time = time.time()
    # '''
    # pool = newPool(nodes=30)
    # pool.map(save_one_repo, repo_list)  # [:3]sample_repo_url ,token_num_list[:1]
    # pool.close()
    # pool.join()
    # '''
    #
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
    #                         # print("code1",code1)
    #                         result_compli_for_else_list.append(
    #                             [repo_name, file_html, cl, me, code[1].lineno,
    #                              ast.unparse(code[1]) + "\n" + ast.unparse(code[0]), ast.unparse(code[-1]), code[2]])
    #
    #                         # result_compli_for_else_list.append(
    #                         #     [repo_name, file_html, cl, me, ast.unparse(code1[0]), ast.unparse(code1[1])])
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
    #
    # random.shuffle(result_compli_for_else_list)
    # util.save_csv(util.data_root + "result_csv/for_comprehen_dict.csv",
    #               result_compli_for_else_list[:400],
    #               ["repo_name", "file_html", "class_name", "me_name", "line_no", "old_code", "new_code",
    #                "remove_ass_flag"])
    # end_time = time.time()
    # print("total time: ", end_time - start_time)
    # 1 156 2943 100 1 2990 40102 salt
    # 791 2010 103165 1291 800 121348 1192868
    # util.save_csv(util.data_root + "complicated_code_dir_pkl/for_compre_dict.csv", result_compli_for_else_list,
    #               ["repo_name", "file_html", "class_name", "me_name", "for_code", "assign_code"])











