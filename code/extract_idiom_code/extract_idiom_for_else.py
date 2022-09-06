import sys,ast,os
pro_root="/".join(os.path.abspath(__file__).split("/")[:-3])+"/"
sys.path.append(pro_root+"code/")
sys.path.append("../..")
sys.path.append("../../../")
import util,traceback
from extract_simp_cmpl_data import ast_util
import complicated_code_util

from pathos.multiprocessing import ProcessingPool as newPool


def find_for_else(for_code):
    e = for_code.orelse
    if e:
        return 1
    return 0
def get_idiom_for_else(tree):
    code_list=[]
    for node in ast.walk(tree):
        if isinstance(node, (ast.For,ast.While)):
            else_flag=find_for_else(node)
            if else_flag:
                #print("come here")
                body_list=node.body
                for body_stmt in body_list:
                    for child_stmt in ast.walk(body_stmt):

                        #print("come here",ast.unparse(body_stmt))
                        if not isinstance(child_stmt,  (ast.For,ast.While)):
                            if isinstance(child_stmt,ast.Break):
                                code_list.append(ast.unparse(node))
    return code_list
def save_repo_for_else_complicated(repo_name):
    count_complicated_code=0
    print("come the repo: ", repo_name)
    one_repo_for_else_code_list = []
    dict_file = dict()
    for file_info in dict_repo_file_python[repo_name]:

        file_path = file_info["file_path"]

        file_html = file_info["file_html"]
        #print("come this file: ", file_path)

        try:
            content = util.load_file_path(file_path)
        except:
            print(f"{file_path} is not existed!")
            continue
        #print("content: ",content)
        try:
            file_tree = ast.parse(content)
            ana_py = ast_util.Fun_Analyzer()
            ana_py.visit(file_tree)
            dict_class = dict()
            for tree, class_name in ana_py.func_def_list:
                code_list = get_idiom_for_else(tree)
                if code_list:
                    ast_util.set_dict_class_code_list(tree, dict_class, class_name, code_list)
            if dict_class:
                dict_file[file_html] = dict_class
            # file_tree = ast.parse(content)
            # ana_py = ast_util.Analyzer()
            # ana_py.visit(file_tree)
            # #print("func number: ",file_html,len(ana_py.func_def_list))
            # for tree in ana_py.func_def_list:
            #     #print("tree_ func_name",tree.__dict__)
            #
            #     code_list=get_idiom_for_else(tree)
            #     if code_list:
            #         one_repo_for_else_code_list.append([code_list, file_path, file_html])


        except SyntaxError:

            print("the file has syntax error")

            continue

        except ValueError:

            traceback.print_exc()

            print("the file has value error: ", file_html)

            continue
        except:
            traceback.print_exc()
            print("the file has other error: ", file_html)
        #break
    util.save_pkl(save_complicated_code_dir_pkl, repo_name, dict_file)

    # if one_repo_for_else_code_list:
    #     count_complicated_code=count_complicated_code+len(one_repo_for_else_code_list)
    #     # print("it exists for else complicated code: ", len(one_repo_for_else_code_list))
    #     util.save_json(save_complicated_code_dir, repo_name, one_repo_for_else_code_list)
    #     print("save successfully! ", save_complicated_code_dir + repo_name)

    # return count_complicated_code

if __name__ == '__main__':
    code='''
for i,(e,w) in enumerate(range(10)):
    print(i,e)
else:
    print("yes")
for i,(e,w) in enumerate(range(10)):
    print(i,e)
    for a in [1,2]:
        print(a)
    else:
        print("else")

    if i>1:
        break
else:
    print("yes")
'''
    #
    # tree = ast.parse(code)
    # code_list=get_idiom_for_else(tree)
    # print("find these codes: ",code_list)


    save_complicated_code_dir= util.data_root + "idiom_code_dir/for_else_idiom_code_fragments/"
    #dict_repo_file_python=util.load_json(util.data_root, "python3_repos_files_info" )
    save_complicated_code_dir_pkl= util.data_root + "idiom_code_dir_pkl/for_else_idiom_code_fragments/"
    dict_repo_file_python= util.load_json(util.data_root, "python3_1000repos_files_info")

    #dict_repo_file_python=util.load_json(util.data_root, "python3_1000repos_files_info_modify" )

    repo_list = []

    for ind, repo_name in enumerate(dict_repo_file_python):
        #print("repo infor: ",dict_repo_file_python[repo_name])
        if os.path.exists(save_complicated_code_dir_pkl + repo_name + ".pkl"):
            continue
        print("repo_name: ", repo_name)
        repo_list.append(repo_name)
    print("count: ", len(repo_list))
    
    '''

    pool = newPool(nodes=30)
    pool.map(save_repo_for_else_complicated, repo_list)  # [:3]sample_repo_url ,token_num_list[:1]
    pool.close()
    pool.join()
    print(">>>>>>>>len all_files: ", len(repo_list))
    '''
    '''
    count = 0
    file_list=set([])
    result_compli_for_else_list=[]
    for file_name in os.listdir(save_complicated_code_dir):
        complicate_code=util.load_json(save_complicated_code_dir,file_name[:-5])
        for code_list, file_path,file_html in complicate_code:
            count +=len(code_list)
            for code in code_list:
                repo_name=file_html.split("/")[4]
                file_list.add(file_html)
                result_compli_for_else_list.append([repo_name,code,file_html,file_path])
            #     print("one code: ",repo_name,code,file_html,file_path)
            #     break
            # break
        # print("file: ",file_name)
        # break
    print("count: ", count, len(os.listdir(save_complicated_code_dir)),len(file_list))

    util.save_csv(util.data_root+"idiom_code_dir/for_else_idiom_code_fragments.csv",result_compli_for_else_list,["repo_name","code","file_html","file_path"])
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
                        break
                        # for code in complicate_code[file_html][cl][me]:
                        #     # print("html: ",file_html,cl,me,ast.unparse(code[0]))
                        #     #                code_index_start_end_list.append([node,assign_stmt,node.lineno, node.end_lineno,assign_stmt_lineno,assign_block_list_str])
                        #
                        #     result_compli_for_else_list.append(
                        #         [repo_name, file_html, cl, me, code[0]])

            # print(f"{file_html} of {repo_name} has  {len(code_list)} code fragments")
        count_repo += repo_exist

    # a=dict(sorted(repo_code_num.items(), key=lambda item: item[1], reverse=True))
    # print(a)
    # print(np.median(list(a.values())), np.max(list(a.values())), np.min(list(a.values())))
    # print(np.median(files_num_list), np.max(files_num_list), np.min(files_num_list))
    # print(np.median(star_num_list), np.max(star_num_list), np.min(star_num_list))
    # print(np.median(contributor_num_list), np.max(contributor_num_list), np.min(contributor_num_list))
    print("count: ", count_repo, code_count, file_count, me_count, all_count_repo, all_file_count, all_me_count)

    # print("----------------------------\n")
    # for code in for_else_filter_redundant_code_list:
    #     print("each code: ", code[0])
