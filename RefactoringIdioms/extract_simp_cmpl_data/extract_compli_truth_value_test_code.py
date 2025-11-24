import sys,ast,os,copy
import tokenize
# sys.path.append("/mnt/zejun/smp/code1/")
abs_path=os.path.abspath(os.path.dirname(__file__))

# abs_path=os.getcwd()
# print("abs_path: ",abs_path)
pack_path="/".join(abs_path.split("/")[:-1])
# print(pack_path)
sys.path.append(pack_path)
import util
# from pathos.multiprocessing import ProcessingPool as newPool

'''
input: 代码片段 code1
if if,while,assert节点
    if test是compare节点
        
elif if boolOP节点
    if values 中含有compare 节点


'''
def decide_compare_complicate_truth_value(test):
    flag=0
    ops = test.ops
    left = ast.unparse(test.left)
    comparators = test.comparators
    comp_str = ast.unparse(comparators[0])

    empty_list = ["None", "True", "False", "0", "0.0", "0j", "Decimal(0)", "Fraction(0, 1)", '', "()","[]", "{}", "dict()", "set()", "range(0)"]

    if len(ops) == 1 and isinstance(ops[0], (ast.Eq, ast.NotEq, ast.Is, ast.IsNot)):
        if left in empty_list or comp_str in empty_list:
            flag=1
    return flag
def get_truth_value_test(code):
    code_list = []
    tree = ast.parse(code)
    for node in ast.walk(tree):

        if isinstance(node, (ast.If, ast.While, ast.Assert)):
            test = node.test
            if isinstance(test, ast.Compare):
                if decide_compare_complicate_truth_value(test):
                    code_list.append(ast.unparse(test))


        elif isinstance(node, ast.BoolOp):
            for value in node.values:
                if isinstance(value, ast.Compare):
                    if decide_compare_complicate_truth_value(value):
                        code_list.append(ast.unparse(value))

    # for e in code_list:
    #     print("code1: ", e)
    return code_list
def save_repo_for_else_complicated(repo_name):
    # for ind,repo_name in enumerate(dict_repo_file_python):
        # if "spotify" not in repo_name:
        #     continue
        # print("come here")
        one_repo_chained_comparison_code_list = []
        for file_info in dict_repo_file_python[repo_name]:
            file_path = file_info["file_path"]
            file_html = file_info["file_html"]
            try:
                content = util.load_file(file_path)
            except:
                print(f"{file_path} is not existed!")
                continue

            try:

                one_file_chained_comparison_code_list=get_truth_value_test(content)
                if one_file_chained_comparison_code_list:
                    one_repo_chained_comparison_code_list.append([one_file_chained_comparison_code_list, file_path, file_html])
                    # print("one_file_truth_value_test_code_list: ",one_file_truth_value_test_code_list)
                    # break
            except SyntaxError:
                print("the file has syntax error")
                continue
            except ValueError:
                print("the file content has some error",file_html)
                continue
            # break
        if one_repo_chained_comparison_code_list:
            # count_repo+=1
            # print("it exists truth value test complicated code1: ", len(one_repo_for_else_code_list))
            util.save_json(save_complicated_code_dir, repo_name, one_repo_chained_comparison_code_list)
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

    #dict_repo_file_python=util.load_json(util.data_root, "python3_repos_files_info" )
    # dict_repo_file_python=util.load_json(util.data_root, "python3_1000repos_files_info_modify" )
    dict_repo_file_python=util.load_json(util.data_root, "python3_1000repos_files_info" )


    repo_name_list=[]
    for repo_name in dict_repo_file_python:

        repo_name_list.append(repo_name)
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
    # print("len all_files: ", len(all_files))
    '''
    #'''
    count=0
    result_compli_for_else_list=[]
    for file_name in os.listdir(save_complicated_code_dir):
        complicate_code=util.load_json(save_complicated_code_dir,file_name[:-5])
        for code_list, file_path,file_html in complicate_code:
            count += len(code_list)
            for code in code_list:
                repo_name=file_html.split("/")[4]
                result_compli_for_else_list.append([repo_name,code,file_html,file_path])
            #     print("one code1: ",repo_name,code1,file_html,file_path)
            #     break
            # break
        # print("file: ",file_name)
        # break
    print("count: ",count,len(os.listdir(save_complicated_code_dir)))
    # util.save_csv(util.data_root+"complicated_code_dir/truth_value_test_complicated.csv",result_compli_for_else_list,["repo_name","code1","file_html","file_path"])
    #'''











    # print("----------------------------\n")
    # for code1 in for_else_filter_redundant_code_list:
    #     print("each code1: ", code1[0])
