import sys,ast,os
abs_path=os.path.abspath(os.path.dirname(__file__))
# print("abs_path: ",abs_path)
pack_path="/".join(abs_path.split("/")[:-1])
# print(pack_path)
sys.path.append(pack_path)


import copy,complicated_code_util,util
# from code1 import util
from RefactoringIdioms.extract_simp_cmpl_data import ast_util
# from code1.extract_simp_cmpl_data import ast_util
import time
from pathos.multiprocessing import ProcessingPool as newPool


def get_pos(ele, one_var):
    if one_var[0] == ele:
        return "l"
    else:
        return "r"

def merge(node1, node2):
    ops = node2.ops
    comparator = node2.comparators

    for op,e in zip(ops,comparator):
        node1.ops.append(op)
        node1.comparators.append(e)

    #print("code1 list: ",code1, ast.unparse(node2),ast.unparse(node1))
    return ast.unparse(node1)
def change_compare_node(node1):
    new_node = copy.deepcopy(node1)
    new_node.left = node1.comparators[-1]
    new_node.comparators = node1.comparators[::-1][1:]
    # new_node.comparators.extend(node1.comparators[:-1][::-1])
    new_node.comparators.append(node1.left)
    for ind, op in enumerate(node1.ops[::-1]):
        if isinstance(op, ast.Gt):
            new_node.ops[ind] = ast.Lt()
            # new_node.ops.append(ast.Lt)
        elif isinstance(op, ast.Lt):
            new_node.ops[ind] = ast.Gt()
            # new_node.ops.append(ast.Gt)
        elif isinstance(op, ast.GtE):
            new_node.ops[ind] = ast.LtE()
            # new_node.ops.append(ast.LtE)
        elif isinstance(op, ast.LtE):
            new_node.ops[ind] = ast.GtE()
            # new_node.ops.append(ast.GtE)
        else:
            continue
    return new_node

def transform_left_right(pos1, pos2, node1, node2):
    code = ""
    if pos1 == 'r' and pos2 == 'l':  # 右左
        # 不变
        code = merge(node1, node2)
        # print("c->s: ", code1)
        pass
    elif pos1 == 'l' and pos2 == 'r':  # 左右
        code = merge( node2,node1)
        # 交换两个节点
        pass
    elif pos1 == 'l' and pos2 == 'l':  # 左左
        # change node1
        if isinstance(node1.ops[-1],(ast.NotIn,ast.In)) and isinstance(node2.ops[-1],(ast.NotIn,ast.In)) :
            return ""
        elif isinstance(node1.ops[-1],(ast.NotIn,ast.In)):
            new_node = change_compare_node(node2) # change node2 变成右
            code = merge(new_node,node1)
        else:
            new_node = change_compare_node(node1)
            code = merge(new_node, node2)
            pass
        # new_node=change_compare_node(node1)
        # code1 = merge(new_node, node2)
    else:  # 右右
        #print("come here")
        if isinstance(node1.ops[-1],(ast.NotIn,ast.In)) and isinstance(node2.ops[-1],(ast.NotIn,ast.In)) :
            return ""
        elif isinstance(node2.ops[-1],(ast.NotIn,ast.In)):
            #print("come here")
            new_node = change_compare_node(node1) # change 左
            code = merge(node2, new_node)
        else:
            #print("come here")
            new_node = change_compare_node(node2)
            code = merge(node1, new_node)
            pass
    return code


def transform_remain_code(remain_vars_list, ignore_ind_list):
    code = []
    for ind, e in enumerate(remain_vars_list):
        if ind in ignore_ind_list:
            continue
        code.append(ast.unparse(e[1]) + " and ")
    # code1.append(ast.unparse(remain_vars_list[-1]))
    return "".join(code)
def transform_chained_comparison(node):
    if not (isinstance(node,ast.BoolOp) and isinstance(node.op,ast.And)):
        return 0,node

    vars_list = []
    values = node.values
    other_code = []
    for value in values:
        if isinstance(value, ast.Compare):
            left = value.left
            comparator = value.comparators[-1]
            vars = [[ast.unparse(left), ast.unparse(comparator)], value]
            vars_list.append(vars)
        else:
            other_code.append(ast.unparse(value))
    if other_code:

        other_code = " and " + " and ".join(other_code)
    else:
        other_code = ""

    remain_vars_list = copy.deepcopy(vars_list)
    overlap_ind_list = []
    for ind, one_var in enumerate(vars_list):
        if ind in overlap_ind_list:
            continue

        for ind_next in range(ind + 1, len(vars_list)):
            if ind_next in overlap_ind_list:
                continue
            another_var = vars_list[ind_next]
            if set(one_var[0]) & set(another_var[0]):
                ele = list(set(one_var[0]) & set(another_var[0]))[0]
                # print("intersect var: ",ele)

                one_pos = get_pos(ele, one_var[0])
                another_pos = get_pos(ele, another_var[0])

                # print("code1 of node1 and node2: ",ast.unparse(one_var[1]),ast.unparse(another_var[1]))
                transform_code = transform_left_right(one_pos, another_pos, one_var[1], another_var[1])
                if not transform_code:
                    # print("come here")
                    return 0,node
                remain_code = transform_remain_code(remain_vars_list, [ind, ind_next])
                # print("all_code: ", remain_code + transform_code + other_code)
                for node in ast.walk(ast.parse(remain_code + transform_code + other_code)):
                    if isinstance(node,ast.BoolOp) and isinstance(node.op, ast.And):

                        return 1, node
                    elif isinstance(node,ast.Compare):
                        return 1,node
            # else:
            #     return 0,node

    return 0,node
# 对找到的代码片段不断进行转换直至不可以转换
def check_chained_comparison(tree,new_code_list):
    for node in ast.walk(tree):
        if isinstance(node, ast.BoolOp):
            op = node.op
            old_node=copy.deepcopy(node)
            if isinstance(op, ast.And):
                flag_code=0
                while 1:
                    flag,new_node = transform_chained_comparison(node)
                    # if new_node
                    if not flag:
                        break
                    else:
                        flag_code=1
                    node=new_node
                if flag_code:
                    # print(f"old_node:{ast.unparse(old_node)}, new_node:{ast.unparse(new_node)} ")
                    new_code_list.append([node,new_node])


def save_repo_for_else_complicated(repo_name):
    start=time.time()
    count_complicated_code = 0
    print("come the repo: ", repo_name)
    dict_file=dict()


    for ind,file_info in enumerate(dict_repo_file_python[repo_name]):
        # if file_path!="/mnt/zejun/smp/data/python_repo_1000/VideoPose3D//run.py":
        #     continue
        file_path = file_info["file_path"]
        file_html = file_info["file_html"]
        try:
            content = util.load_file_path(file_path)
        except:
            print(f"{file_path} is not existed!")
            continue

        try:
            file_tree = ast.parse(content)
            ana_py = ast_util.Fun_Analyzer()
            ana_py.visit(file_tree)

            dict_class=dict()
            for tree, class_name in ana_py.func_def_list:

                # print("tree_ func_name",tree.__dict__)
                new_code_list = []
                check_chained_comparison(tree, new_code_list)
                ast_util.set_dict_class_code_list(tree, dict_class, class_name, new_code_list)


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
        # print("it exists for else complicated code1: ", len(one_repo_for_else_code_list))
        util.save_pkl(save_complicated_code_dir_pkl, repo_name, dict_file)
        # util.save_json(save_complicated_code_dir, repo_name, one_repo_for_else_code_list)
        print(end-start," save successfully! ", save_complicated_code_dir_pkl + repo_name)
    else:
        print(end-start," the repo has no for else")
        util.save_pkl(save_complicated_code_dir_pkl, repo_name, dict_file)
        # util.save_json(save_complicated_code_dir, repo_name, one_repo_for_else_code_list)

if __name__ == '__main__':
    code='''

a>b and a>c and 1>=c # and c>1 and e
#len(cur_info['cont_end_pts']) == 0 and len(other_infos) == 0
#edge_canvas[x, y] != -1 and edge_canvas[x, y] != valid_edge_id
'up' in direc.lower() and direc.lower()>1
#'up' in direc.lower() and 1>direc.lower()
#'up' in direc.lower() and direc.lower() in a
#direc.lower() in a and 'up' not in direc.lower()
#a>1  and  direc.lower() in a 左，右
#1<a  and  direc.lower() in a 右，右
#1<a  and  a in direc.lower() #右，左
#b in a  and  a in direc.lower()  #右，左
b in a  and  direc.lower() in a
'''
    save_complicated_code_dir_pkl = util.data_root + "transform_complicate_to_simple_pkl/chain_comparison/"

    dict_repo_file_python = util.load_json(util.data_root, "python3_1000repos_files_info")
    new_code_list=[]
    tree = ast.parse(code)
    # check_chained_comparison(tree, new_code_list)


    #'''
    repo_list = []
    for ind, repo_name in enumerate(dict_repo_file_python):
        # if repo_name!="salt":
        #     continue
        # print("repo_name: ", repo_name)
        repo_list.append(repo_name)
    #save_repo_for_else_complicated(repo_list[0])
    #'''
    print("len: ", len(repo_list))
    pool = newPool(nodes=30)
    pool.map(save_repo_for_else_complicated, repo_list)  # [:3]sample_repo_url ,token_num_list[:1]
    pool.close()
    pool.join()
    #'''

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
                            result_compli_for_else_list.append(
                                [repo_name, cl, me, ast.unparse(code[0]), ast.unparse(code[1]), file_html])

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
    print("count: ", count_repo, code_count, file_count, me_count, all_count_repo, all_file_count, all_me_count)
    # 1 156 2943 100 1 2990 40102 salt
    # 791 2010 103165 1291 800 121348 1192868
    util.save_csv(util.data_root + "complicated_code_dir_1000_star/chain_comparison.csv", result_compli_for_else_list,
                  ["repo_name", "class_name", "me_name", "old_code", "new_code", "file_html", "file_path"])















