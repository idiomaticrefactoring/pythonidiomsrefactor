import ast

# sys.path.append("/mnt/zejun/smp/code1/")
import copy

from RefactoringIdioms.extract_simp_cmpl_data import ast_util

from RefactoringIdioms.transform_c_s import transform_var_unpack_for_target_compli_to_simple
# from pathos.multiprocessing import ProcessingPool as newPool
import traceback
'''
1. for.body 中不包含对target的写操作，即在assign的左边
2. 对于for.body 中只包含对target的读操作，subscript，并且slice是常量
'''
def whether_slice_is_constant(slice,var):
    # print("slice: ",ast.unparse(slice),slice)
    if isinstance(slice, ast.Constant):
        slice_value = slice.value
        if isinstance(slice_value, int):
           return True
        else:
            return False
    elif isinstance(slice, ast.Slice):
        # print("slice: ", slice.__dict__, ast.unparse(slice))
        lower = -1
        upper = -1
        step = -1
        if slice.lower:
            if isinstance(slice.lower, ast.Constant):
                lower = ast.unparse(slice.lower)
            else:
                return False
        else:
            lower = 0
        if slice.upper:
            if isinstance(slice.upper, ast.Constant):
                upper = ast.unparse(slice.upper)
            else:
                return False
        else:
            upper = ''.join(['len(', var, ')'])
        if slice.step:
            if isinstance(slice.step, ast.Constant):
                if isinstance(slice.step.value, int) and slice.step.value == 1:
                    step = 1
            else:
                return False
        else:
            step = 1
    return False

def is_var_subscript(node,var):

    if isinstance(node, ast.Subscript):
        value = node.value

        if ast.unparse(value) == var:
            # return True
            slice = node.slice
            return whether_slice_is_constant(slice,var)


        elif  isinstance(value, ast.Subscript):
            return is_var_subscript(value,var)
        else:
            return False
    return False
def is_var(node,var_ast):
    if isinstance(node, type(var_ast)) and ast.unparse(node) == ast.unparse(var_ast):
        return True
    return False
'''
判断给定节点是否只包含var的subscript使用，并且subscript的slice都是常量
'''
def whether_var_subscript(node,target,var_list=[]):
    # print("node: ", ast.unparse(node))
    var=ast.unparse(target)
    if is_var_subscript(node,var):
        # var_list.add(ast.unparse(node))
        var_list.add(node)
        return True
        pass
    elif is_var(node,target):
        return False
        pass
    else:

        for e in ast.iter_child_nodes(node):
            if not whether_var_subscript(e,target,var_list):
                return False

                # var_list.add(ast.unparse(e))
        return True
def get_for_target(tree):
    code_list=[]

    for node in ast.walk(tree):
        if isinstance(node, ast.For):
            var_list = set([])
            target = node.target
            var = ast.unparse(target)
            # print("var: ",var)
            # print("target: ",target.__dict__, type(target))
            count_obj = ast_util.get_basic_count(target)
            if count_obj == 1:

                for e_body in ast.walk(node):
                    # if isinstance(e_body, (ast.Assign)):
                    if isinstance(e_body, (ast.Assign,ast.AnnAssign,ast.AugAssign)):
                        if hasattr(e_body,'targets'):
                            left = e_body.targets
                        elif hasattr(e_body,'target'):
                            left = [e_body.target]

                        for left_e in left:
                            for ass_e in ast.walk(left_e):
                                # print("the ele: ",ast.unparse(left_e))
                                if ast.unparse(ass_e) == var:
                                    # print("it cannot be simplified because it contains write operation for the var ",var)
                                    break
                            else:
                                continue
                            break
                        else:
                            continue
                        break
                else:
                    '''
                    whether code1  use target
                    '''
                    flag=0
                    for stmt in node.body:
                        for e in ast.walk(stmt):
                            if is_var(e,target):
                                # print("come here: ",ast.unparse(stmt))
                                flag=1
                                break
                    else:
                        pass
                    if flag:
                        for stmt in node.body:
                            '''
                            whether code1  use target without subscript, if use it cannot simplify
                            '''
                            flag=whether_var_subscript(stmt, target,var_list)
                            if not flag:
                                # print("it cannot be simplified because it contains other operation for the var besides the subscript operation ", var,ast.unparse(stmt),flag)

                                break
                        else:
                            var_list_real = list(var_list)
                            #print("var_list_real: ",var_list_real)#['val[1]', 'val[1][0]', 'val[1][1]', 'val[0]']-->['val[1]', 'val[0]']
                            for i,var1 in enumerate(var_list):
                                for j,var2 in enumerate(var_list):
                                    if ast.unparse(var1) in ast.unparse(var2) and ast.unparse(var1)!=ast.unparse(var2):
                                        var_list_real.remove(var2)
                            # print("var_list_real: ",var_list_real)
                            Map_var=dict()
                            node_copy=copy.deepcopy(node)
                            # print(">>>>>>>>>>>node_copy: ", ast.unparse(node_copy),var_list_real)
                            # for var in var_list_real:
                            #     print("var: ",ast.unparse(var))
                            new_code= transform_var_unpack_for_target_compli_to_simple.transform_for_node_var_unpack(node_copy, var_list_real, Map_var)
                            if new_code:
                                # print("new_code: ",ast.unparse(new_code))
                                code_list.append([node,new_code])
                            else:
                                code_list.append([node])
                                # print(">>>>>>>>>>>the code1 I cannot transform: ",ast.unparse(node))
                        # print("it maybe simplified")
    return code_list
def transform_for_multiple_targets_code(content):
    code_pair_list = []
    # print(content)
    try:

        file_tree = ast.parse(content)
        ana_py = ast_util.Fun_Analyzer()
        ana_py.visit(file_tree)

        for tree, class_name in ana_py.func_def_list:
            try:
                me_name = tree.name
            except:
                me_name = ""
            new_code_list = get_for_target(tree)

            # print("new_code_list: ",new_code_list)
            for e in new_code_list:
                # print("new_tree: ",ast.unparse(e[0]),ast.unparse(e[1]))
                if len(e) < 2:
                    print(">>>>>>>>>>>the code1 I cannot transform: ", e, ast.unparse(e))
                    continue

                # new_file_content = replace_file_content_ass(content, each_assign_list, new_code)
                # assign_list[ind_ass].append(new_code)
                # complic_code_me_info_dir_pkl = util.data_root + "complic_code_me_info_dir_pkl/each_idiom_type_all_methods/multi_ass/"  # for_else
                # util.save_file(complic_code_me_info_dir_pkl, "test"+str(ind_ass), new_file_content, ".txt", "w")
                # util.save_file(complic_code_me_info_dir_pkl, "test_old"+str(ind_ass), content, ".txt", "w")
                line_list=[[e[0].lineno,e[0].end_lineno]]
                code_pair_list.append([class_name,me_name,ast.unparse(e[0]), ast.unparse(e[1]),line_list])

        return code_pair_list

    except:
        traceback.print_exc()
        return code_pair_list
# def save_repo_for_else_complicated(repo_name):
#     start=time.time()
#     count_complicated_code = 0
#     print("come the repo: ", repo_name)
#     one_repo_for_else_code_list = []
#
#     dict_file=dict()
#     # if os.path.exists(save_complicated_code_dir_pkl + repo_name + ".pkl"):
#     #     print("the repo has been saved before")
#     #     return None
#
#     for ind,file_info in enumerate(dict_repo_file_python[repo_name]):
#
#         file_path = file_info["file_path"]
#         # if file_path!="/mnt/zejun/smp/data/python_repo_1000/VideoPose3D//run.py":
#         #     continue
#         file_html = file_info["file_html"]
#         # print(file_html)
#         # if file_html!="https://github.com/nipy/nibabel/tree/master/nibabel/fileslice.py":  #
#         #     continue
#         # if file_html!="https://github.com/raphaelvallat/pingouin/tree/master/pingouin/regression.py":#"https://github.com/smicallef/spiderfoot/tree/master//sflib.py":#"https://github.com/smicallef/spiderfoot/tree/master//sfwebui.py":#"https://github.com/PaddlePaddle/Paddle/tree/master/python/paddle/dataset/tests/imikolov_test.py":
#         #     continue
#         # print("cone here")
#         try:
#             content = util.load_file_path(file_path)
#         except:
#             print(f"{file_path} is not existed!")
#             continue
#
#         # print("content: ",content)
#         try:
#             # print("come here")
#             file_tree = ast.parse(content)
#             ana_py = ast_util.Fun_Analyzer()
#             ana_py.visit(file_tree)
#             # print("ana_py.func_def_list ", ana_py.func_def_list)
#             # dict_file["repo_name"]=repo_name
#             dict_class=dict()
#             for tree, class_name in ana_py.func_def_list:
#
#                 new_code_list=get_for_target(tree)
#                 new_code_list_new=[]
#                 # print("new_code_list: ",new_code_list)
#                 for e in new_code_list:
#                     # print("new_tree: ",ast.unparse(e[0]),ast.unparse(e[1]))
#                     if len(e)<2:
#                         print(">>>>>>>>>>>the code1 I cannot transform: ", file_html,e,ast.unparse(e))
#                         continue
#                     new_code_list_new.append(e)
#                 # print("new_code_list ", new_code_list)
#                 #
#                 # for old_code,new_code in new_code_list:
#                 #     print("old_code,new_code: ",ast.unparse(old_code),ast.unparse(new_code))
#                 ast_util.set_dict_class_code_list(tree,dict_class, class_name, new_code_list_new)
#             dict_file[file_html]=dict_class
#         except SyntaxError:
#             print("the file has syntax error")
#             continue
#         except ValueError:
#             print("the file has value error: ", content, file_html)
#             continue
#         # break
#     end = time.time()
#     #'''
#     if dict_file:
#         count_complicated_code = count_complicated_code + len(one_repo_for_else_code_list)
#         # print("it exists for else complicated code1: ", len(one_repo_for_else_code_list))
#         util.save_pkl(save_complicated_code_dir_pkl, repo_name, dict_file)
#         # util.save_json(save_complicated_code_dir, repo_name, one_repo_for_else_code_list)
#         print(end-start," save successfully! ", save_complicated_code_dir_pkl + repo_name)
#     else:
#         print(end-start," the repo has no for else")
#         util.save_pkl(save_complicated_code_dir_pkl, repo_name, dict_file)
#         # util.save_json(save_complicated_code_dir, repo_name, one_repo_for_else_code_list)
#     #'''
#     return count_complicated_code
if __name__ == '__main__':
    code='''
for T in a:
    c=1
    d=c+1
    e=T[0]+T[1]
    f=funct(T[1],T[:3])
    if len(T)>1:
        print("nothing")
# for ne_node in ne_nodes:
#     store_tuple = [ne_node, ne_node[i], mesh_nodes[ne_node]['cur_id']]
#     ne_node[0][0]
#     ne_node[0][1]
#     if ne_node[0] == node[0]:
#         if ne_node[1] == ne_node[1] - 1:
#             four_dir_nes['left'].append(store_tuple)
# for _ in range(i):
#     result.append(s)            
# for ne_node in ne_nodes:
#     store_tuple = [ne_node[0], mesh_nodes['cur_id']]
# 
#     if ne_node[0] == node[0]:
#         if ne_node[1] == ne_node[1] - 1:
#             four_dir_nes['left'].append(store_tuple)
# for T  in model._meta.backrefs.items():
# 
#     if T[0].backref == '+':
#         continue
for val in sorted(npz.items()):
    logging.info('  Loading %s in %s' % (str(val[1][0].shape), val[0]))
    logging.info('  Loading %s in %s' % (str(val[1][1].shape), val[0]))
    weights.extend(val[1])
    if len(model.all_weights) == len(weights):
        break
'''
    # tree=ast.parse(code1)
    # code_list=get_for_target(tree)
    # for code1,new_code in code_list:
    #     print("code1:",ast.unparse(code1))
    #     print("new_code",ast.unparse(new_code))

 #    save_complicated_code_dir = util.data_root + "complicated_code_dir/var_unpack_for_target_complicated/"
 #    save_complicated_code_dir_pkl= util.data_root + "transform_complicate_to_simple_pkl/var_unpack_for_target_complicated/"
 #    # dict_repo_file_python = util.load_json(util.data_root, "python3_repos_files_info")
 #    dict_repo_file_python= util.load_json(util.data_root, "python3_1000repos_files_info")
 #    repo_name_list=[]
 #    for repo_name in dict_repo_file_python:
 #        # if os.path.exists(save_complicated_code_dir_pkl + repo_name + ".pkl"):
 #        #     continue
 #        #     return None
 #        # if repo_name!="nibabel":#"pingouin":#"spiderfoot":
 #        #     continue
 #        repo_name_list.append(repo_name)
 #
 #    print("repo num: ", len(list(dict_repo_file_python.keys())),len(repo_name_list))
 #    # save_repo_for_else_complicated(repo_name_list[0])
 #    '''
 #    count_complicated_code = 0
 #    count_repo = 0
 #    for ind, repo_name in enumerate(dict_repo_file_python):
 #        one_repo_chained_comparison_code_list = []
 #        for file_info in dict_repo_file_python[repo_name]:
 #            file_path = file_info["file_path"]
 #            file_html = file_info["file_html"]
 #            content = util.load_file(file_path)
 #            try:
 #                # if 1:
 #                one_file_chained_comparison_code_list = get_for_target(content)
 #                count_complicated_code += len(one_file_chained_comparison_code_list)
 #                if one_file_chained_comparison_code_list:
 #                    one_repo_chained_comparison_code_list.append(
 #                        [one_file_chained_comparison_code_list, file_path, file_html])
 #                    # print("one_file_truth_value_test_code_list: ",one_file_truth_value_test_code_list)
 #                    # break
 #            except SyntaxError:
 #                print("the file has syntax error")
 #                continue
 #            # break
 #        if one_repo_chained_comparison_code_list:
 #            # print(one_repo_chained_comparison_code_list)
 #            # break
 #            count_repo += 1
 #            # print("it exists truth value test complicated code1: ", len(one_repo_for_else_code_list))
 #            util.save_json(save_complicated_code_dir, repo_name, one_repo_chained_comparison_code_list)
 #                    # for righ_e in ast.walk(right):
 #                    #     if isinstance(node, ast.Subscript):
 #                    #         value = node.value
 #                    #         slice = node.slice
 #                    #         if ast.unparse(value) == var:
 #                    #             if isinstance(slice, ast.Constant):
 #                    #                 slice_value = slice.value
 #                    #                 if isinstance(slice_value, int):
 #
 #    print("count_complicated_code: ",ind,count_complicated_code)
 #    '''
 #
 #    start_time=time.time()
 #    '''
 #    pool = newPool(nodes=30)
 #    pool.map(save_repo_for_else_complicated, repo_name_list)  # [:3]sample_repo_url ,token_num_list[:1]
 #    pool.close()
 #    pool.join()
 #    end_time = time.time()
 #    print("total time: ", end_time - start_time)
 #    '''
 #    files_num_list = []
 #    star_num_list = []
 #    contributor_num_list = []
 #    count_repo, file_count, me_count, code_count = 0, 0, 0, 0
 #    file_list = set([])
 #    repo_code_num = dict()
 #    result_compli_for_else_list = []
 #    all_count_repo, all_file_count, all_me_count = 0, 0, 0
 #    for file_name in os.listdir(save_complicated_code_dir_pkl):
 #        all_count_repo += 1
 #        repo_name = file_name[:-4]
 #        # files_num_list.append(repo_files_info[repo_name])
 #        # star_num_list.append(repo_star_info[repo_name])
 #        # contributor_num_list.append(repo_contributor_info[repo_name])
 #
 #        complicate_code = util.load_pkl(save_complicated_code_dir_pkl, repo_name)
 #
 #        repo_file_count, repo_me_count, repo_code_count, repo_all_file_count, repo_all_me_count = complicated_code_util.get_code_count(
 #            complicate_code)
 #        # for code_list, file_path, file_html in complicate_code:
 #        code_count += repo_code_count
 #        file_count += repo_file_count
 #        me_count += repo_me_count
 #        all_file_count += repo_all_file_count
 #        all_me_count += repo_all_me_count
 #        repo_exist = 0
 #        for file_html in complicate_code:
 #            for cl in complicate_code[file_html]:
 #                for me in complicate_code[file_html][cl]:
 #                    if complicate_code[file_html][cl][me]:
 #                        repo_exist = 1
 #                        for code in complicate_code[file_html][cl][me]:
 #                            # print("html: ",file_html,cl,me,ast.unparse(code1[0]))
 #                            #                code_index_start_end_list.append([node,assign_stmt,node.lineno, node.end_lineno,assign_stmt_lineno,assign_block_list_str])
 #
 #                            result_compli_for_else_list.append(
 #                                [repo_name, file_html, cl, me, code[0].lineno,ast.unparse(code[0]), ast.unparse(code[1])])
 #
 #            # print(f"{file_html} of {repo_name} has  {len(code_list)} code1 fragments")
 #        count_repo += repo_exist
 #
 #    # a=dict(sorted(repo_code_num.items(), key=lambda item: item[1], reverse=True))
 #    # print(a)
 #    # print(np.median(list(a.values())), np.max(list(a.values())), np.min(list(a.values())))
 #    # print(np.median(files_num_list), np.max(files_num_list), np.min(files_num_list))
 #    # print(np.median(star_num_list), np.max(star_num_list), np.min(star_num_list))
 #    # print(np.median(contributor_num_list), np.max(contributor_num_list), np.min(contributor_num_list))
 #    print("count: ", count_repo, code_count, file_count, me_count, all_count_repo, all_file_count, all_me_count)
 #    import random
 #
 #    random.shuffle(result_compli_for_else_list)
 #    util.save_csv(util.data_root + "result_csv/var_unpack_for_target_complicated.csv", result_compli_for_else_list[:400],
 #                  ["repo_name", "file_html", "class_name", "me_name", "line_no", "old_code", "new_code"])
 #    end_time = time.time()
 #    print("total time: ",end_time-start_time)
 #    # 1 156 2943 100 1 2990 40102 salt
 #    # 791 2010 103165 1291 800 121348 1192868
 #    # util.save_csv(util.data_root + "transform_complicate_to_simple_pkl/var_unpack_for_target_complicated.csv", result_compli_for_else_list,
 #    #               ["repo_name", "file_html", "class_name", "me_name", "for_code", "assign_code"])
 #
 #    # count = 0
 #    # result_compli_for_else_list = []
 #    # for file_name in os.listdir(save_complicated_code_dir):
 #    #     complicate_code = util.load_json(save_complicated_code_dir, file_name[:-5])
 #    #     for each_file in complicate_code:
 #    #         code_list = each_file[0]
 #    #         file_path = each_file[1]
 #    #         file_html = each_file[2]
 #    #         count += len(code_list)
 #    #         # print("count: ", count)
 #    #         for code1 in code_list:
 #    #             repo_name = file_html.split("/")[4]
 #    #             result_compli_for_else_list.append([repo_name, code1[0],code1[1], file_html, file_path])
 #    #     #     print("one code1: ",repo_name,code1,file_html,file_path)
 #    #     #     break
 #    #     # break
 #    #     # print("file: ",file_name)
 #    #     # break
 #    # print("count: ", count, len(os.listdir(save_complicated_code_dir)))
 #    # util.save_csv(util.data_root + "complicated_code_dir/var_unpack_for_target_complicated.csv",
 #    #               result_compli_for_else_list, ["repo_name", "code1","var_list", "file_html", "file_path"])
 # #   '''






