import ast
import tokenize
import traceback

import os

p_name="python-ast-explorer-master"
abs_path=os.path.abspath(os.path.dirname(__file__))
abs_path=abs_path[:abs_path.index("extract_transform_complicate_code_new")]
# print()
import sys
sys.path.append(abs_path)
sys.path.append(abs_path+"extract_transform_complicate_code_new/")
sys.path.append(abs_path+"extract_transform_complicate_code_new/comprehension/")
from RefactoringIdioms.extract_simp_cmpl_data import ast_util
# from code1.extract_simp_cmpl_data import ast_util
import extract_compli_for_comprehension_logic
from RefactoringIdioms.transform_c_s import transform_comprehension_compli_to_simple
from tokenize import tokenize
from io import BytesIO
# from pathos.multiprocessing import ProcessingPool as newPool
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
const_empty=" = []"
def find_complicate_list_comprehension(code):

    pass
def whether_block_call_assign(node_list,assign_block_list):
    contain_append_flag=0
    #print(ast.unparse(node_list))
    for e_body in node_list:
        #print("code1: ",ast.unparse(e_body),e_body.__dict__)

        if (not (isinstance(e_body, ast.Expr) and isinstance(e_body.value, ast.Call))) and (not isinstance(e_body, ast.Assign)):
            #print("the for sentences has other stmts so cannot transform such as try stmt: ", type(e_body),ast.unparse(e_body))

            return False
        if isinstance(e_body, ast.Expr) and isinstance(e_body.value, ast.Call):
            call_name = ""
            call_front=e_body.value.func
            # print(call_front.__dict__,ast.unparse(call_front))
            if isinstance(call_front, ast.Name):
                call_name = ast.unparse(call_front)
            elif isinstance(call_front, ast.Attribute):
                call_name = call_front.attr
            else:
                call_name = ast.unparse(call_front)
            if call_name=="append":
                contain_append_flag=1

    if contain_append_flag:
        assign_block_list.append(node_list)
        return True
    return False
def get_func_name(one_body):
    pre_name,call_name=None,None
    if isinstance(one_body, ast.Expr) and isinstance(one_body.value, ast.Call):
        # print("come here")
        call_front = one_body.value.func
        if isinstance(call_front, ast.Name):
            call_name = ast.unparse(call_front)
        elif isinstance(call_front, ast.Attribute):
            call_name = call_front.attr
            pre_name=ast.unparse(call_front.value)
        else:
            call_name = ast.unparse(call_front)
    return pre_name,call_name


def whether_fun_is_append(one_body,assign_block_list):
    #print("one_body: ",ast.unparse(one_body),one_body.__dict__)
    if isinstance(one_body, ast.Expr) and isinstance(one_body.value, ast.Call) :
        # print("come here")
        call_front = one_body.value.func

        # print("call dict: ", call_front.__dict__)
        call_name = ""
        if isinstance(call_front, ast.Name):
            call_name = ast.unparse(call_front)
        elif isinstance(call_front, ast.Attribute):
            call_name = call_front.attr
        else:
            call_name = ast.unparse(call_front)
        #print("the func name: ", call_name)
        if call_name == "append":
            assign_block_list.append([one_body])
            return True
    elif isinstance(one_body,ast.Call):
        call_front = one_body.func

        # print("call dict: ", call_front.__dict__)
        call_name = ""
        if isinstance(call_front, ast.Name):
            call_name = ast.unparse(call_front)
        elif isinstance(call_front, ast.Attribute):
            call_name = call_front.attr
        else:
            call_name = ast.unparse(call_front)
        # print("the func name: ", call_name)
        if call_name == "append":
            assign_block_list.append([one_body])
            return True

    return False

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
       # print("come here")
        return False
    if len(for_body_list) == 1:
        one_body=for_body_list[0]
        if isinstance(one_body, ast.For):
            #print("come here for_traverse")
            return for_traverse(one_body,assign_block_list)
        elif isinstance(one_body, ast.If):
            #print("it is if node")
            return if_traverse(one_body,assign_block_list)

        elif isinstance(one_body, ast.Expr):
            #print("come here for_traverse and it is an Expr",whether_fun_is_append(one_body,assign_block_list))
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
def filter_overlap(code_index_list):
    no_overlap_list=[]
    if len(code_index_list)==1:
        return code_index_list
    for i in range(len(code_index_list)):
        code=code_index_list[i]
        beg=code[0].lineno
        end=code[0].end_lineno
        for j in range(len(code_index_list)):
            if i==j:
                continue
            fuzhu_beg = code_index_list[j][0].lineno
            fuzhu_end = code_index_list[j][0].end_lineno
            if beg>=fuzhu_beg and end<=fuzhu_end:
                break
        else:
            no_overlap_list.append(code)

    return no_overlap_list
'''
1. 当前for_node中处理对vars进行append操作外，不应该使用vars
    如果节点中存在Call节点还需要判断Call中是否使用了vars
2. 判断tree中在for_node之前的节点是否有vars的赋值语句，如果存在这样的赋值语句，还需要判断在这个赋值语句父母中for_node节点后面是否还使用了vars
    如果使用了vars则这个赋值节点不应该被删除

    
'''
def whether_first_var_is_empty_assign(tree,for_node,vars):
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
        if isinstance(child, ast.Call):
            a = []
            append_time += whether_fun_is_append(child, a)

            def is_call_use_vars(tree, fun_name, vars):
                # print(">>>>>>.come is_call_use_vars: ", fun_name)
                ana_py_fun = ast_util.Fun_Analyzer()
                ana_py_fun.visit(tree)
                for tree_fun, class_name in ana_py_fun.func_def_list:
                    if hasattr(tree_fun, "name"):
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
    remove_ass_flag=1
    for node in ast.walk(tree):
        if not hasattr(node,"lineno"):
            continue

        if node.lineno==for_node.lineno:
            break
        if hasattr(node,'body') and isinstance(node.body, list) and node.lineno<for_node.lineno:
            # print("come here node: ",node,ast.unparse(node),isinstance(node,ast.Expr), )
            for child in node.body:
                if isinstance(child, ast.Assign):
                    if ast.unparse(child).strip().split("=")[0].strip() == list(vars)[0] and ast.unparse(child.value) == "[]":
                        assign_stmt = child
                        assign_stmt_lineno = child.lineno
                        flag = 2


                elif assign_stmt_lineno:
                    for next_child in ast.walk(child):
                        if not hasattr(next_child,"lineno"):
                            continue
                        if next_child.lineno>for_node.end_lineno:
                            s = ast.unparse(next_child)
                            if s != list(vars)[0]:
                                g = tokenize(BytesIO(s.encode('utf-8')).readline)  # tokenize the string
                                for toknum, to_child, _, _, _ in g:
                                    if to_child.strip() == list(vars)[0]:
                                        remove_ass_flag =0
                                        # print("yes in the assign block it use more than one time: ", vars, s, "\n>>>>>>>>>", ast.unparse(for_node))
                                        break
                                else:
                                    continue
                                break

        if assign_stmt_lineno and node!=assign_stmt and node.end_lineno<for_node.lineno and node.lineno>assign_stmt_lineno :
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
        # 判断跟compreh不属于同一个父母的在for_node后面的代码片段是否使用了变量vars
        # if assign_stmt_lineno and node!=assign_stmt and node.lineno>ass_parent.end_lineno:
        #     s = ast.unparse(node)
        #
        #     if s != list(vars)[0]:
        #         g = tokenize(BytesIO(s.encode('utf-8')).readline)  # tokenize the string
        #         for toknum, child, _, _, _ in g:
        #             if child.strip() == list(vars)[0]:
        #                 remove_ass_flag = 0
        #                 print("no we cannot remove the ass: ","\n>>>>>>>>>",ast.unparse(for_node),"\n>>>>>>>>>",ast.unparse(node))
        #                 break
        #         if remove_ass_flag == 0:
        #             break

    return flag,assign_stmt_lineno,assign_stmt,remove_ass_flag

def get_complicated_for_comprehen_code_list(tree,content):
    #code1 = ast.unparse(tree)
    # print("come get java-style python code",ast.unparse(tree))
    code_index_start_end_list = []

    start_lineno=tree.body[0].lineno
    #code1 = "\n".join(content.split("\n")[start_lineno - 1:])
    for ind_line,node in enumerate(ast.walk(tree)):
        # print("come walk the tree",ast.unparse(node))
            #print("start_line: ",node.lineno)
        if isinstance(node, ast.For):
            # print("node_line: ",ast.unparse(node),node.lineno, node.end_lineno)
            # if node.lineno!=1674:
            #     continue

            assign_block_list=[]
            #print("it is what: ",for_traverse(node,assign_block_list))
            if for_traverse(node,assign_block_list):#判断for语句是否满足For_Match
                # print("maybe comrephension: ",ast.unparse(node))
                '''
                判断是否是同一个变量的append
                '''
                vars = set([])
                for each_block in assign_block_list:
                    pre_name,call_name=get_func_name(each_block[0])
                    vars.add(pre_name)
                if len(vars)!=1:
                    continue
                # print("for node: ",ast.unparse(node),node.lineno)
                '''
                判断是否是同一个变量的append
                '''
                flag,assign_stmt_lineno,assign_stmt,remove_ass_flag= extract_compli_for_comprehension_logic.whether_first_var_is_empty_assign(tree, node, vars)
                if flag!=2:
                    print("it does not have the var or the var has been used more than one time",remove_ass_flag)
                    continue
                #print("flag: ", assign_stmt,assign_stmt_lineno,suite)
                assign_block_list_str = []
                for one_block in assign_block_list:
                    one_block_str = []
                    for e in one_block:
                        one_block_str.append(ast.unparse(e))
                    assign_block_list_str.append(one_block_str)
                # print(">>>>>>>>>>>>>>>>>>>>>>it is complicated comprehension code1\n", remove_ass_flag,ast.unparse(assign_stmt),"\n",ast.unparse(node),node.lineno, node.end_lineno,assign_stmt_lineno,assign_block_list_str,assign_stmt)
                # print(assign_stmt+"\n"+ast.unparse(node))
                code_index_start_end_list.append([node,assign_stmt,remove_ass_flag])
                # code_index_start_end_list.append([ast.unparse(node),node.lineno, node.end_lineno,assign_stmt_lineno,assign_block_list_str, assign_stmt])
    #print("len: ", len(code_index_start_end_list))
    code_index_start_end_list = filter_overlap(code_index_start_end_list)
    # print("len: ",len(code_index_start_end_list))

    return code_index_start_end_list

def get_list_compreh(content):
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
                me_name=tree.name
            except:
                me_name=""
            new_code_list = get_complicated_for_comprehen_code_list(tree, content)
            # print("come method", new_code_list,ast.unparse(tree))
            for ind, (for_node, assign_node, remove_ass_flag) in enumerate(new_code_list):
                new_code= transform_comprehension_compli_to_simple.transform(for_node, assign_node)
                complete_new_code=ast.unparse(new_code) if remove_ass_flag else ast.unparse(assign_node) + "\n"+ast.unparse(new_code)
                line_list = []
                line_list.append([assign_node.lineno,assign_node.end_lineno])
                line_list.append([for_node.lineno, for_node.end_lineno])
                code_pair_list.append([class_name,me_name,ast.unparse(assign_node) + "\n" + ast.unparse(for_node), complete_new_code,line_list])
        return code_pair_list

    except:
        traceback.print_exc()
        code_pair_list=["syntax error in code"]
        return code_pair_list




if __name__ == '__main__':
    code = '''
# a=[]
# for i in range(4):
#     a.append(i)
# a=[]
for i in range(3):
    call(a)
a=[]
b=[]
for i in range(4):
    if i>3:
        for j in range(a):
            # i=i**2
            # a.append(j)
            b.append(i)
#     # elif i>4:
#     #     a.append(i)
# for i in range(4):
#      if i>3:
#          if i>3:
#              a.append(i)
#          else:
#               a.append(i)

for i in range(4):
     # if i>3:
         if i>3:
             a.append(i)
         else:
              a.append(i)
# a=[]
for i in range(3):
    b=[]
    for i in range(3): # 这个节点里包含 除了assign和Call的节点 因为在comprehension的繁杂代码中不可以再有for语句
         if i>3:
             b.append(i)
    a.append(b)  
threads = []
for _ in range(4):
    threads.append(threading.Thread(target=test)) 
'''

    '''

    tree = ast.parse(code1)
    code_list=get_complicated_for_comprehen_code_list(tree, code1)
    #code_list=get_complicated_for_comprehen_code_list(code1)
    print("len: ",len(code_list))
    for e in code_list:
        print(">>>>>code1： ", e[0])
        print("block: ", e[-1])
        # for each in  e[-1]:
        #     print(each)

        print("----------END------------")
    # test_code="a=[]"
    # test_tree = ast.parse(test_code)
    # print(ast.unparse(test_tree))
    '''
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

    # save_complicated_code_dir_pkl = util.data_root + "transform_complicate_to_simple_pkl/for_compre_list/"

    # save_complicated_code_dir = util.data_root + "complicated_code_dir/for_comrephension_list_complicated_only_one_stmt/"
    #'''
    #dict_repo_file_python = util.load_json(util.data_root, "python3_repos_files_info")
    # dict_repo_file_python= util.load_json(util.data_root, "python3_1000repos_files_info")

    code='''
def f():
        a = []
        for e in range(10):
            a.append(e)
'''
    print(get_list_compreh(code))
    # repo_name_list=[]
    # for repo_name in dict_repo_file_python:
    #
    #     repo_name_list.append(repo_name)
    #     if repo_name=="hosts":
    #         print("Come here repo")
    #         save_one_repo(repo_name)

    # print("repo num: ", len(list(dict_repo_file_python.keys())))
    # count_complicated_code = 0
    # count_repo = 0
    # repo_list = []
    # for ind, repo_name in enumerate(dict_repo_file_python):
    #     # if repo_name!="pipreqs":#"proselint":#"networkx":#"nni":#"aws-cli":#"youtube-dl":#"localstack":#"transitions":#"youtube-dl":#"hypothesis":
    #     #     continue
    #     # if repo_name!="youtube-dl":#"transitions":#"metrics":##"youtube-dl":#"proselint":#"localstack":#"shuup":#"Real-Time-Voice-Cloning":#"keras-bert":#"Legofy":
    #     #     continue
    #     #print("repo_name: ", repo_name)
    #     repo_list.append(repo_name)
    # print("repo num: ", len(repo_list))
    import time
    start_time = time.time()
    # save_one_repo(repo_list[0])
    '''
    pool = newPool(nodes=30)
    pool.map(save_one_repo, repo_list)  # [:3]sample_repo_url ,token_num_list[:1]
    pool.close()
    pool.join()
    '''
    '''
    files_num_list = []
    star_num_list = []
    contributor_num_list = []
    count_repo, file_count, me_count, code_count = 0, 0, 0, 0
    file_list = set([])
    repo_code_num = dict()
    result_compli_for_else_list = []
    all_count_repo, all_file_count, all_me_count = 0, 0, 0
    for file_name in os.listdir(save_complicated_code_dir_pkl):
        all_count_repo += 1
        repo_name = file_name[:-4]
        # files_num_list.append(repo_files_info[repo_name])
        # star_num_list.append(repo_star_info[repo_name])
        # contributor_num_list.append(repo_contributor_info[repo_name])

        complicate_code = util.load_pkl(save_complicated_code_dir_pkl, repo_name)

        repo_file_count, repo_me_count, repo_code_count, repo_all_file_count, repo_all_me_count = complicated_code_util.get_code_count(
            complicate_code)
        # for code_list, file_path, file_html in complicate_code:
        code_count += repo_code_count
        file_count += repo_file_count
        me_count += repo_me_count
        all_file_count += repo_all_file_count
        all_me_count += repo_all_me_count
        repo_exist = 0
        for file_html in complicate_code:
            for cl in complicate_code[file_html]:
                for me in complicate_code[file_html][cl]:
                    if complicate_code[file_html][cl][me]:
                        repo_exist = 1
                        for code in complicate_code[file_html][cl][me]:
                            # print("html: ",file_html,cl,me,ast.unparse(code1[0]))
                            #                code_index_start_end_list.append([node,assign_stmt,node.lineno, node.end_lineno,assign_stmt_lineno,assign_block_list_str])
                            # result_compli_for_else_list.append(
                            #     [repo_name, file_html, cl, me, code1[1].lineno,
                            #      ast.unparse(code1[1]) +"\n"+ ast.unparse(code1[0]), ast.unparse(code1[-1]), code1[2]])
                            result_compli_for_else_list.append(
                                [repo_name, file_html, cl, me, code[1].lineno,
                                 ast.unparse(code[1]) + "\n" + ast.unparse(code[0]), ast.unparse(code[-1]), code[2]])

            # print(f"{file_html} of {repo_name} has  {len(code_list)} code1 fragments")
        count_repo += repo_exist

    # a=dict(sorted(repo_code_num.items(), key=lambda item: item[1], reverse=True))
    # print(a)
    # print(np.median(list(a.values())), np.max(list(a.values())), np.min(list(a.values())))
    # print(np.median(files_num_list), np.max(files_num_list), np.min(files_num_list))
    # print(np.median(star_num_list), np.max(star_num_list), np.min(star_num_list))
    # print(np.median(contributor_num_list), np.max(contributor_num_list), np.min(contributor_num_list))
    print("count: ", count_repo, code_count, file_count, me_count, all_count_repo, all_file_count, all_me_count)
    import random

    random.shuffle(result_compli_for_else_list)
    util.save_csv(util.data_root + "result_csv/for_comprehen_list.csv",
                  result_compli_for_else_list[:400],
                  ["repo_name", "file_html", "class_name", "me_name", "line_no", "old_code", "new_code",
                   "remove_ass_flag"])

    end_time = time.time()
    print("total time: ", end_time - start_time)
    '''
    # 1 156 2943 100 1 2990 40102 salt
    # 791 2010 103165 1291 800 121348 1192868
    # util.save_csv(util.data_root + "complicated_code_dir_pkl/for_else.csv", result_compli_for_else_list,
    #               ["repo_name", "file_html","class_name", "me_name", "for_code", "assign_code"])

    '''
    count = 0
    result_compli_for_else_list = []
    for file_name in os.listdir(save_complicated_code_dir):
        complicate_code = util.load_json(save_complicated_code_dir, file_name[:-5])
        for each_file in complicate_code:

            # for code_list, file_path,file_html in each_file:
            #
            #     print("count: ",code_list)
            code_list = each_file[0]
            file_path = each_file[1]
            file_html = each_file[2]
            count += len(code_list)
            # print("count: ", count)
            for code1 in code_list:
                #print("code1: ",code1)
                repo_name = file_html.split("/")[4]
                #print("code1: ",code1)
                result_compli_for_else_list.append(
                    [repo_name, code1[-2]+"\n"+ast.unparse()code1[0]+"\n"+code1[-1], str(code1[1])+" "+str(code1[2])+" "+str(code1[3]), file_html, file_path])

        #     print("one code1: ",repo_name,code1,file_html,file_path)
        #     break
        # break
        # print("file: ",file_name)
        # break
    print("count: ", count, len(os.listdir(save_complicated_code_dir)))#,result_compli_for_else_list)
    # util.save_csv(util.data_root + "complicated_code_dir/for_comrephension_list_complicated_only_one_stmt.csv",
    #               result_compli_for_else_list, ["repo_name", "code1", "start_end_assign_ind", "file_html", "file_path"])
    '''











