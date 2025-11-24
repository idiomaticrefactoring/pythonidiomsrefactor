import sys,ast,os


abs_path=os.path.abspath(os.path.dirname(__file__))
abs_path=abs_path[:abs_path.index("extract_transform_complicate_code_new")]

sys.path.append(abs_path)
sys.path.append(abs_path+"extract_transform_complicate_code_new/")
sys.path.append(abs_path+"extract_transform_complicate_code_new/comprehension/")
import extract_compli_for_comprehension_logic
from RefactoringIdioms.extract_simp_cmpl_data import ast_util
from RefactoringIdioms.transform_c_s import transform_comprehension_set_compli_to_simple
import traceback
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
const_func_name="add"
const_empty=["set()"]

def get_set_compreh(content):
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
            new_code_list = extract_compli_for_comprehension_logic.get_complicated_for_comprehen_code_list(tree,
                                                                                                           content,
                                                                                                           ["set()"],
                                                                                                           "add")
            # print("come method", new_code_list,ast.unparse(tree))
            for ind, (for_node, assign_node, remove_ass_flag) in enumerate(new_code_list):
                new_code= transform_comprehension_set_compli_to_simple.transform(for_node, assign_node)
                complete_new_code=ast.unparse(new_code) if remove_ass_flag else ast.unparse(assign_node) + "\n"+ast.unparse(new_code)
                line_list = []
                line_list.append([assign_node.lineno, assign_node.end_lineno])
                line_list.append([for_node.lineno, for_node.end_lineno])
                code_pair_list.append([class_name,me_name,ast.unparse(assign_node) + "\n" + ast.unparse(for_node), complete_new_code,line_list])
        return code_pair_list

    except:
        traceback.print_exc()
        return code_pair_list

        # break
# def save_one_repo(repo_name):
#     count=0
#     one_repo_chained_comparison_code_list = []
#     dict_file = dict()
#     for file_info in dict_repo_file_python[repo_name]:
#         file_path = file_info["file_path"]
#         file_html = file_info["file_html"]
#         # if file_html!="https://github.com/salesforce/policy_sentry/tree/master/policy_sentry/querying/all.py":#"https://github.com/bndr/pipreqs/tree/master/pipreqs/pipreqs.py":#"https://github.com/amperser/proselint/tree/master/proselint/tools.py":#"https://github.com/networkx/networkx/tree/master/networkx/readwrite/json_graph/adjacency.py":#"https://github.com/microsoft/nni/tree/master/nni/tools/nnictl/nnictl_utils.py":#"https://github.com/microsoft/nni/tree/master/nni/tools/nnictl/nnictl_utils.py":#:#"https://github.com/aws/aws-cli/tree/master/awscli/customizations/s3/subcommands.py":#"https://github.com/microsoft/nni/tree/master/nni/algorithms/hpo/networkmorphism_tuner/graph_transformer.py":##"https://github.com/ytdl-org/youtube-dl/tree/master/youtube_dl/utils.py":#"https://github.com/localstack/localstack/tree/master/localstack/utils/common.py":#"https://github.com/pytransitions/transitions/tree/master/transitions/extensions/nesting.py":##"https://github.com/HypothesisWorks/hypothesis/tree/master/hypothesis-python/examples/test_rle.py":
#         #     continue
#         # if file_html!="https://github.com/smicallef/spiderfoot/tree/master/spiderfoot/helpers.py":#"https://github.com/HypothesisWorks/hypothesis/tree/master/hypothesis-python/examples/test_rle.py":
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
#                 new_code_list = extract_compli_for_comprehension_logic.get_complicated_for_comprehen_code_list(tree, content, ["set()"], "add")
#                 for ind, (for_node, assign_node,remove_ass_flag) in enumerate(new_code_list):
#                     new_code_list[ind].append(
#                         transform_comprehension_set_compli_to_simple.transform(for_node, assign_node))
#                 #ode, assign_stmt, remove_ass_flag
#                 # for old_code,old_ass,remove_ass_flag,new_code in new_code_list:
#                 #     print("old_code,new_code: ",ast.unparse(old_code),ast.unparse(new_code))
#                 #
#                 # # one_file_chained_comparison_code_list.extend(get_complicated_for_comprehen_code_list(tree,content))
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
#             print("the file has syntax error")
#             continue
#         except ValueError:
#             traceback.print_exc()
#             print("the file has value error: ", file_html)#content,
#             continue
#         except:
#             traceback.print_exc()
#
#         # break
#     #print("count: ",count)
#     util.save_pkl(save_complicated_code_dir_pkl, repo_name, dict_file)
#     print("save successfully! ", count,save_complicated_code_dir_pkl + repo_name)
if __name__ == '__main__':
    code = '''
# a=[]
# for i in range(4):
#     a.append(i)
# a=[]
for i in range(3):
    call(a)
a=set()
b=set()
for i in range(4):
    if i>3:
        for j in range(5):
            # i=i**2
            # a.append(j)
            b.add(i)
#     # elif i>4:
#     #     a.append(i)
# for i in range(4):
#      if i>3:
#          if i>3:
#              a.append(i)
#          else:
#               a.append(i)
# for far_node in tmp_far_nodes:
#     if not (mesh.has_node(far_node) and mesh.nodes[far_node].get('inpaint_id') == 1):
#         rmv_tmp_far_nodes.add(far_node)
'''
    #'''
    tree = ast.parse(code)
    code_list= extract_compli_for_comprehension_logic.get_complicated_for_comprehen_code_list(tree, code, ["set()"], "add")
    print("len: ",len(code_list))

    #'''
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
    # save_complicated_code_dir_pkl= util.data_root + "transform_complicate_to_simple_pkl/for_compre_set/"
    #
    # save_complicated_code_dir = util.data_root + "complicated_code_dir/for_comrephension_set_complicated_only_one_stmt/"
    # #'''
    # dict_repo_file_python = util.load_json(util.data_root, "python3_1000repos_files_info")
    # # repo_name_list=[]
    # # for repo_name in dict_repo_file_python:
    # #
    # #     repo_name_list.append(repo_name)
    # print("repo num: ", len(list(dict_repo_file_python.keys())))
    # count_complicated_code = 0
    # count_repo = 0
    # repo_list=[]
    # for ind, repo_name in enumerate(dict_repo_file_python):
    #     # if repo_name!="policy_sentry":#"pipreqs":#"spiderfoot":#"salt":#"Real-Time-Voice-Cloning":#"keras-bert":#"Legofy":
    #     #     continue
    #     # print("repo_name: ",repo_name)
    #     repo_list.append(repo_name)
    # # save_one_repo(repo_list[0])
    # import time
    # start_time=time.time()
    # '''
    # pool = newPool(nodes=30)
    # pool.map(save_one_repo, repo_list)  # [:3]sample_repo_url ,token_num_list[:1]
    # pool.close()
    # pool.join()
    # '''
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
    #                         # print("html: ", file_html, cl, me, ast.unparse(code1[0]))
    #                         # print("code1", code1)
    #                         #code_index_start_end_list.append([node,assign_stmt,remove_ass_flag])
    #                         result_compli_for_else_list.append(
    #                             [repo_name, file_html, cl, me, code[1].lineno,ast.unparse(code[1])+"\n"+ast.unparse(code[0]),ast.unparse(code[-1]),code[2]])
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
    # util.save_csv(util.data_root + "result_csv/for_comprehen_set.csv",
    #               result_compli_for_else_list[:400],
    #               ["repo_name", "file_html", "class_name", "me_name", "line_no", "old_code", "new_code","remove_ass_flag"])
    # end_time = time.time()
    # print("total time: ", end_time - start_time)
    # 1 156 2943 100 1 2990 40102 salt
    # 791 2010 103165 1291 800 121348 1192868
    # util.save_csv(util.data_root + "complicated_code_dir_pkl/for_compre_set.csv", result_compli_for_else_list,
    #               ["repo_name", "file_html", "class_name", "me_name", "for_code", "assign_code"])

# util.save_csv(util.data_root + "complicated_code_dir/for_comrephension_set_complicated_only_one_stmt.csv",
    #               result_compli_for_else_list, ["repo_name", "code1", "start_end_assign_ind", "file_html", "file_path"])
    #'''











