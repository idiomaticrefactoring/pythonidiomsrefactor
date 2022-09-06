import sys,ast,os
pro_root="/".join(os.path.abspath(__file__).split("/")[:-3])+"/"
sys.path.append(pro_root+"code/")
import time,complicated_code_util
import util
from pathos.multiprocessing import ProcessingPool as newPool
from transform_c_s import transform_truth_value_test_compli_to_simple
from extract_simp_cmpl_data import ast_util
from pathos.multiprocessing import ProcessingPool as newPool
import traceback

def decide_compare_complicate_truth_value(test):
    flag=0
    ops = test.ops
    left = ast.unparse(test.left)
    comparators = test.comparators
    comp_str = ast.unparse(comparators[0])

    empty_list = ["None", "True", "False", "0", "0.0", "0j", "Decimal(0)", "Fraction(0, 1)", '', "()","[]", "{}", "dict()", "set()", "range(0)"]

    if len(ops) == 1 and isinstance(ops[0], (ast.Eq, ast.NotEq)):
        if left in empty_list or comp_str in empty_list:
            flag=1
    return flag
def get_truth_value_test(tree):
    code_list = []

    for node in ast.walk(tree):

        if isinstance(node, (ast.If, ast.While, ast.Assert)):
            test = node.test
            if isinstance(test, ast.Compare):
                if decide_compare_complicate_truth_value(test):
                    new_code = transform_truth_value_test_compli_to_simple.transform_c_s_truth_value_test_no_len(test)
                    code_list.append([test,new_code])


        elif isinstance(node, ast.BoolOp):
            for value in node.values:
                if isinstance(value, ast.Compare):
                    if decide_compare_complicate_truth_value(value):
                        new_code = transform_truth_value_test_compli_to_simple.transform_c_s_truth_value_test_no_len(value)
                        code_list.append([value,new_code])

    # for e in code_list:
    #     print("code: ", e)
    return code_list
def save_repo_for_else_complicated(repo_name):
    start=time.time()
    count_complicated_code = 0
    print("come the repo: ", repo_name)
    one_repo_for_else_code_list = []

    dict_file=dict()
    # if os.path.exists(save_complicated_code_dir_pkl + repo_name + ".pkl"):
    #     print("the repo has been saved before")
    #     return None
    if 1:#not os.path.exists(save_complicated_code_dir_pkl + repo_name + ".pkl"):
        for ind,file_info in enumerate(dict_repo_file_python[repo_name]):

            file_path = file_info["file_path"]

            file_html = file_info["file_html"]
            # if file_html != "https://github.com/google/TensorNetwork/tree/master/tensornetwork/block_sparse/blocksparsetensor.py":  # "https://github.com/tanghaibao/goatools/tree/master/goatools/go_enrichment.py":#"https://github.com/microsoft/msticpy/tree/master/msticpy/sectools/syslog_utils.py":#"https://github.com/chezou/tabula-py/tree/master/tabula/io.py":#"https://github.com/astorfi/speechpy/tree/master/speechpy/feature.py":#"https://github.com/pytoolz/toolz/tree/master/toolz/functoolz.py":#"https://github.com/smicallef/spiderfoot/tree/master//sfwebui.py":#"https://github.com/huggingface/transformers/tree/master/src/transformers/trainer_pt_utils.py":#"https://github.com/pytransitions/transitions/tree/master/transitions/core.py":#"https://github.com/google/yapf/tree/master/yapf/yapflib/file_resources.py":#"https://github.com/zalando/patroni/tree/master/patroni/ctl.py":#"https://github.com/pymc-devs/pymc/tree/master/pymc/sampling.py":#"https://github.com/smicallef/spiderfoot/tree/master//sflib.py":#"https://github.com/smicallef/spiderfoot/tree/master//sfwebui.py":#
            #     continue
            # if file_html != "https://github.com/chezou/tabula-py/tree/master/tabula/io.py":  # "https://github.com/astorfi/speechpy/tree/master/speechpy/feature.py":#"https://github.com/pytoolz/toolz/tree/master/toolz/functoolz.py":#"https://github.com/smicallef/spiderfoot/tree/master//sfwebui.py":#"https://github.com/huggingface/transformers/tree/master/src/transformers/trainer_pt_utils.py":#"https://github.com/pytransitions/transitions/tree/master/transitions/core.py":#"https://github.com/google/yapf/tree/master/yapf/yapflib/file_resources.py":#"https://github.com/zalando/patroni/tree/master/patroni/ctl.py":#"https://github.com/pymc-devs/pymc/tree/master/pymc/sampling.py":#"https://github.com/smicallef/spiderfoot/tree/master//sflib.py":#"https://github.com/smicallef/spiderfoot/tree/master//sfwebui.py":#
            #     continue
            # if file_html!="":#"https://github.com/astorfi/speechpy/tree/master/speechpy/feature.py":#"https://github.com/vt-vl-lab/3d-photo-inpainting/tree/master//mesh.py":
            #     continue

            try:
                content = util.load_file_path(file_path)
            except:
                print(f"{file_path} is not existed!")
                continue

            # print("content: ",content)
            try:
                # print("come here")
                file_tree = ast.parse(content)
                ana_py = ast_util.Fun_Analyzer()
                ana_py.visit(file_tree)
                # print("ana_py.func_def_list ", ana_py.func_def_list)
                # dict_file["repo_name"]=repo_name


                dict_class=dict()
                for tree, class_name in ana_py.func_def_list:

                    new_code_list=get_truth_value_test(tree)
                    # print("new_code_list ", new_code_list)
                    #
                    # for old_code,new_code in new_code_list:
                    #      print("old_code,new_code: ",ast.unparse(old_code),ast.unparse(new_code))
                    ast_util.set_dict_class_code_list(tree,dict_class, class_name, new_code_list)


                dict_file[file_html]=dict_class



            except SyntaxError:
                print("the file has syntax error")
                continue
            except ValueError:
                print("the file has value error: ", content, file_html)
                continue
            # break
        end = time.time()
        #'''
        if dict_file:
            count_complicated_code = count_complicated_code + len(one_repo_for_else_code_list)
            # print("it exists for else complicated code: ", len(one_repo_for_else_code_list))
            util.save_pkl(save_complicated_code_dir_pkl, repo_name, dict_file)
            # util.save_json(save_complicated_code_dir, repo_name, one_repo_for_else_code_list)
            print(end-start," save successfully! ", save_complicated_code_dir_pkl + repo_name)
        else:
            print(end-start," the repo has no for else")
            util.save_pkl(save_complicated_code_dir_pkl, repo_name, dict_file)
            # util.save_json(save_complicated_code_dir, repo_name, one_repo_for_else_code_list)
        #'''
        # return count_complicated_code
if __name__ == '__main__':
    code='''
if self . get_conf_value ( 'show' , header = header ) == [ ] :
    pass
elif stats_grab == { } :
    pass
assert policy . remember ( pretend . stub ( ) , pretend . stub ( ) ) == 0
while a!=[]:
    pass

'''



    # ana_py = Analyzer()
    # ana_py.visit(file_tree)
    # print("fun number: ",len(ana_py.func_def_list))

    save_complicated_code_dir= util.data_root + "complicated_code_dir/truth_value_test_complicated/"
    save_complicated_code_dir_pkl= util.data_root + "transform_complicate_to_simple_pkl/truth_value_test_complicated_remove_is_is_not/"
    save_complicated_code_dir_pkl= util.data_root + "transform_complicate_to_simple_pkl/truth_value_test_complicated_remove_is_is_not_no_len/"

    #dict_repo_file_python=util.load_json(util.data_root, "python3_repos_files_info" )
    # dict_repo_file_python=util.load_json(util.data_root, "python3_1000repos_files_info_modify" )
    dict_repo_file_python= util.load_json(util.data_root, "python3_1000repos_files_info")


    repo_name_list=[]
    for repo_name in dict_repo_file_python:
        # if repo_name!="3d-photo-inpainting":#anki
        #     continue
        # if repo_name!="TensorNetwork":#"tabula-py":#"speechpy":#"gdb-dashboard":
        #     continue
        if os.path.exists(save_complicated_code_dir_pkl + repo_name + ".pkl"):

            continue
        repo_name_list.append(repo_name)
    # save_repo_for_else_complicated(repo_name_list[0])
    print("len of repo: ",len(repo_name_list))
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
            # print("it exists truth value test complicated code: ", len(one_repo_for_else_code_list))
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
    # print("len all_files: ", len(all_files))
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
                            # print("html: ",file_html,cl,me,ast.unparse(code[0]))
                            #                code_index_start_end_list.append([node,assign_stmt,node.lineno, node.end_lineno,assign_stmt_lineno,assign_block_list_str])

                            result_compli_for_else_list.append(
                                [repo_name, file_html, cl, me, code[0].lineno,ast.unparse(code[0]), ast.unparse(code[1])])

            # print(f"{file_html} of {repo_name} has  {len(code_list)} code fragments")
        count_repo += repo_exist

    # a=dict(sorted(repo_code_num.items(), key=lambda item: item[1], reverse=True))
    # print(a)
    # print(np.median(list(a.values())), np.max(list(a.values())), np.min(list(a.values())))
    # print(np.median(files_num_list), np.max(files_num_list), np.min(files_num_list))
    # print(np.median(star_num_list), np.max(star_num_list), np.min(star_num_list))
    # print(np.median(contributor_num_list), np.max(contributor_num_list), np.min(contributor_num_list))
    '''
    import random

    random.shuffle(result_compli_for_else_list)
    util.save_csv(util.data_root + "result_csv/truth_value_test_remove_line.csv", result_compli_for_else_list[:400],
                  ["repo_name", "file_html", "class_name", "me_name", "line_no", "old_code", "new_code"])
    '''

    # util.save_csv(util.data_root + "result_csv/truth_value_test.csv", result_compli_for_else_list[:400],
    #               ["repo_name", "file_html", "class_name", "me_name", "line_no", "old_code", "new_code"])

    print("count: ", count_repo, code_count, file_count, me_count, all_count_repo, all_file_count, all_me_count)
    # 1 156 2943 100 1 2990 40102 salt
    # 791 2010 103165 1291 800 121348 1192868
    # util.save_csv(util.data_root + "transform_complicate_to_simple_pkl/truth_value_test_complicated_remove_is_isnot.csv", result_compli_for_else_list,
    #               ["repo_name", "file_html", "class_name", "me_name", "for_code", "assign_code"])


