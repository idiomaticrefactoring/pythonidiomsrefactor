import sys,ast,os
import traceback
abs_path=os.path.abspath(os.path.dirname(__file__))

# abs_path=os.getcwd()
# print("abs_path: ",abs_path)
pack_path="/".join(abs_path.split("/")[:-1])
# print(pack_path)
sys.path.append(pack_path)

import copy,time,complicated_code_util
import util
from sympy import *
from RefactoringIdioms.extract_simp_cmpl_data import ast_util

from RefactoringIdioms.transform_c_s import transform_var_unpack_call_compli_to_simple
from pathos.multiprocessing import ProcessingPool as newPool


def whether_add_end(slice_list, each_seq, arg_seq,step,new_arg_same_list, beg, end):
    if end == len(slice_list[1:]) and end > beg:
        new_arg_same_list.append(
            [each_seq[beg:end + 1], arg_seq[1][beg:end + 1], arg_seq[2], step]) # arg_list, ind_list, call node, step
def whether_add(each_seq, arg_seq,step,new_arg_same_list, beg, end):
    if end > beg:
        new_arg_same_list.append(
            [each_seq[beg:end + 1], arg_seq[1][beg:end + 1], arg_seq[2], step])
def get_func_call_by_args(tree):
    code_list = []
    arg_same_list=[]
    new_arg_same_list = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            args_list = node.args
            var_set = []
            ind_list = []
            arg_one_list=[]
            # arg_same_list = []
            for ind_elts,e in enumerate(args_list):
                # print(args_list)

                '''
                找参数中连续使用同一变量的subscript
                '''

                if isinstance(e, ast.Subscript):
                    #print("arg: ",ast.unparse(e),ind_elts,var_set)
                    if isinstance(e.slice, ast.Slice):
                        if len(var_set) > 1:
                            arg_same_list.append([arg_one_list, ind_list,node])
                            # code_list.append([ast.unparse(node), ind_list])
                        var_set = []
                        ind_list = []
                        arg_one_list = []
                        continue
                    e_value = e.value
                    value_str=ast.unparse(e_value)
                    if not var_set:
                        var_set.append(e_value)
                        ind_list.append(ind_elts)
                        arg_one_list.append(e)
                    else:
                        if value_str==ast.unparse(var_set[-1]):
                            var_set.append(e_value)
                            ind_list.append(ind_elts)
                            arg_one_list.append(e)
                            if ind_elts==len(args_list)-1:
                                arg_same_list.append([arg_one_list, ind_list, node])

                        else:
                            if len(var_set)>1:
                                arg_same_list.append([arg_one_list,ind_list,node])
                                # code_list.append([ast.unparse(node), ind_list])
                            var_set=[e_value]
                            ind_list=[ind_elts]
                            arg_one_list=[e]
                            #print(">>>>>>>arg: ", ast.unparse(e), ind_elts,var_set)
                else:
                    if len(var_set) > 1:
                        arg_same_list.append([arg_one_list, ind_list,node])
                        # code_list.append([ast.unparse(node), ind_list])
                    var_set = []
                    ind_list = []
                    arg_one_list = []

    '''
    提取下标是等差数列的node_list
    '''
   # each arg_seq is arg_list where each ele is an arg, corresponding ind_list where each ele is the index of arg in the args, corresponding node
    for arg_seq in arg_same_list:
        # print("each_arg: ",arg_seq)
        each_seq=arg_seq[0]
        #print(each_seq)
        slice_list=[]

        for e_child in ast.walk(tree):
            if hasattr(e_child,'lineno'):

                if e_child.lineno<each_seq[0].lineno and isinstance(e_child,(ast.Assign,ast.AnnAssign)):
                    if isinstance(e_child,ast.Assign):
                        tar_list=e_child.targets
                    else:
                        tar_list=[e_child.target]
                    for tar in tar_list:
                        try:
                            if ast.unparse(tar)==ast.unparse(each_seq[0].value) \
                                and hasattr(e_child,"value") and ast.unparse(e_child.value)[0] in ["[","(","set("]:
                                break
                        except:
                            traceback.print_exc()
                            print("e_child: ",e_child)
                            print("e_child_str: ",ast.unparse(e_child))
                            continue


                    else:
                        continue
                    break
        else:
            continue
        if 1:

            # delete slice of arg is str type
            for arg in each_seq:
                slice=arg.slice
                slice_list.append(slice)
                # if isinstance(slice,ast.Constant) and not isinstance(slice.value, int):
                #     #print(">>>>>>>>it is str: ",arg_seq)
                #     continue

            #else:
                # determine whether slice list of arg 是等差数列
            step=None
            #for i in range(1,len(slice_list)-1):
            beg = 0
            end=0
            for ind,e_node in enumerate(slice_list[1:]):
                pre_var= slice_list[ind]
                pre_var_str = ast.unparse(slice_list[ind])
                e_str=ast.unparse(e_node)
                # determine whether slice of arg is int constant
                if 1:#pre_var_str.isdigit() and e_str.isdigit():
                    # print(">>>>>>>>it is constant: ",arg_seq)
                    if not step:
                        try:
                            step=str(sympify(e_str+'-('+pre_var_str+")"))
                        except:
                            step="None"
                        # print("step: ",step,ast.unparse(e_node),ast.unparse(pre_var))
                        # step=int(e_str)-int(pre_var_str)

                        if not step.isdigit() or (step.isdigit() and int(step)==0):
                            whether_add(each_seq, arg_seq, step, new_arg_same_list, beg, end)
                            step=None
                            end += 1
                            beg=end
                        else:
                            step=int(step)
                            end+=1
                            whether_add_end(slice_list, each_seq, arg_seq, step, new_arg_same_list, beg, end)

                    else:
                        # new_step=int(e_str)-int(pre_var_str)
                        try:
                            new_step=str(sympify(e_str+'-('+pre_var_str+")"))
                        except:
                            new_step="None"
                        # new_step = str(sympify(e_str + '-(' + pre_var_str + ")"))
                        # print("new_step: ", new_step, ast.unparse(e_node), ast.unparse(pre_var))
                        if new_step.isdigit() and int(new_step)==step:
                            end+=1
                            whether_add_end(slice_list, each_seq, arg_seq, step, new_arg_same_list, beg, end)
                        else:

                            whether_add(each_seq, arg_seq, step, new_arg_same_list, beg, end)
                            step=None
                            end+=1
                            beg = end
                    #print(">>>>>>>>it is not the same step: ", slice_list,pre_var,e,arg_seq)
                    # continue
            # else:# determine whether not int constant slice is the same step
            #     # e_node=ast.parse(e)
            #     #if is not constant, it must BinOp, and all nodes has the same step
            #     #print(">>>>>>>>it is not the constant index in slice: ", slice_list, pre_var, e, arg_seq)
            #     if isinstance(e_node,ast.BinOp) and ast.unparse(e_node.right).isdigit():
            #         if not step:
            #             #print(">>>>>>>>the step: ", ast.unparse(e_node), pre_var, e, arg_seq)
            #             if isinstance(pre_var, ast.BinOp) and ast.unparse(pre_var.right).isdigit():
            #
            #             step=int(ast.unparse(e_node.right))
            #             if step <= 0:
            #                 whether_add(each_seq, arg_seq, step, new_arg_same_list, beg, end)
            #                 step = None
            #                 end += 1
            #                 beg = end
            #             else:
            #                 end += 1
            #                 whether_add_end(slice_list, each_seq, arg_seq, step, new_arg_same_list, beg, end)
            #         else:
            #             new_step = int(ast.unparse(e_node.right))
            #             if new_step == step:
            #                 end += 1
            #                 whether_add_end(slice_list, each_seq, arg_seq, step, new_arg_same_list, beg, end)
            #             else:
            #
            #                 whether_add(each_seq, arg_seq, step, new_arg_same_list, beg, end)
            #                 step = None
            #                 end += 1
            #                 beg = end
            #                 # continue
            #     else:
            #         step = None
            #         whether_add(each_seq, arg_seq, step, new_arg_same_list, beg, end)
            #         end+=1
            #         beg = end


    #print(code_list)
    return new_arg_same_list
    # code_map=dict()
    # for e in new_arg_same_list:
    #     copy_e=e[-2]
    #     # copy_e = copy.deepcopy(e[-2])
    #     # e[-2] = ast.unparse(e[-2])
    #     if copy_e in code_map:
    #
    #
    #         code_map[copy_e].append(e)
    #     else:
    #         code_map[copy_e]=[e]
    #     code_list.append([e[1],e[2],e[3]])
    # # print(code_map)
    # return code_map
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
        # if file_html!="https://github.com/quantumlib/OpenFermion/tree/master/src/openfermion/transforms/opconversions/bksf.py":#"https://github.com/flennerhag/mlens/tree/master/mlens/utils/id_train.py":#"https://github.com/google/budoux/tree/master/budoux/parser.py":#"https://github.com/django/django/tree/master/django/contrib/gis/gdal/raster/band.py":
        #     continue

        try:
            content = util.load_file_path(file_path)
        except:
            print(f"{file_path} is not existed!")
            continue

        # print("content: ",content)
        try:
            print("file_html: ", file_html)
            # print("come here")
            file_tree = ast.parse(content)
            ana_py = ast_util.Fun_Analyzer()
            ana_py.visit(file_tree)
            # print("ana_py.func_def_list ", ana_py.func_def_list)
            # dict_file["repo_name"]=repo_name
            dict_class=dict()
            for tree, class_name in ana_py.func_def_list:
                new_code_list=[]
                new_arg_same_list = get_func_call_by_args(tree)

                for ind, arg_info_list in enumerate(new_arg_same_list):
                    copy_arg_info_list=copy.deepcopy(arg_info_list)
                    star_node = transform_var_unpack_call_compli_to_simple.transform_var_unpack_call_each_args(
                        copy_arg_info_list)
                    new_code_list.append([arg_info_list, star_node])
                # print("new_code_list ", new_code_list)
                #
                # for old_code,new_code in new_code_list:
                #     print("old_code,new_code: ",old_code[1],ast.unparse(old_code[-2]),ast.unparse(new_code))
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
    code='''
upfirdn2d_native(input, kernel, up, up, down, down, pad[0], pad[1], pad[0], pad[1])
ConvBNLayer(out_channels[1], out_channels[1], 3, 1, act='relu', name='fpn_up_g1_1')
sort_by_key_ir(ins[0], ins[1], outs[0], outs[1], outs[2], outs[3], axis, is_ascend)
a=axes.text( rect.xy[1],rect.xy[0], rect.xy[1], labels[I:],labels[i+1],labels[2],bbox=dict(facecolor=color, lw=0))
# a=axes.text( rect.xy[0],rect.xy[1], rect.xy[1], labels[I:],labels[i+1],labels[2],bbox=dict(facecolor=color, lw=0))
# b=func(a[i],a[i+1],c[1])
# b=func(a[i+1],a[i],a[i+1],c[1])
# b=func(a['1'],a[i],a[i+1],c[2],c[0],c[1])
b=func(a['1'],a[i],a[i+1],c[2],c['1'],c[0],c[1])
# b=func(a,b,c[1])
self.ds_opt_adam.adam_update_copy(self.opt_id, state['step'], group['lr'], beta1, beta2, group['eps'], group['weight_decay'], group['bias_correction'], p.data, p.grad.data, state['exp_avg'], state['exp_avg_sq'], fp16_param_groups[group_id][param_id].data)

'''
    '''
    # get_func_call_by_args(tree)
    tree = ast.parse(code1)
    code_list=get_func_call_by_args(tree)
    test_save_complicated_code_dir =util.data_root + "test_complicated_code_dir/"
    file_name="var_unpack_func_call_only_same_dengcha_subscript_complicated"

    # util.save_pkl(test_save_complicated_code_dir,file_name,code_list)
    for code1 in code_list:
        print("code1: ",code1)
    '''
    # save_complicated_code_dir = util.data_root + "complicated_code_dir/var_unpack_func_call_only_same_dengcha_subscript_complicated/"

    save_complicated_code_dir = util.data_root + "complicated_code_dir/var_unpack_func_call_only_same_dengcha_subscript_complicated_pkl/"
    save_complicated_code_dir_pkl= util.data_root + "transform_complicate_to_simple_pkl/var_unpack_call_star_complicated_strict/"

    dict_repo_file_python= util.load_json(util.data_root, "python3_1000repos_files_info")
    repo_name_list=[]
    for repo_name in dict_repo_file_python:
        # if repo_name!="OpenFermion":#"mlens":#"OpenFermion":#"budoux":#"django":
        #     continue
        # if os.path.exists(save_complicated_code_dir_pkl + repo_name + ".pkl"):
        #
        #     continue
        repo_name_list.append(repo_name)
    print("repo num: ", len(list(dict_repo_file_python.keys())),len(repo_name_list))
    # save_repo_for_else_complicated(repo_name_list[0])

    start_time = time.time()
    #'''
    pool = newPool(nodes=30)
    pool.map(save_repo_for_else_complicated, repo_name_list)  # [:3]sample_repo_url ,token_num_list[:1]
    pool.close()
    pool.join()
    #'''
    end_time = time.time()
    print("total time: ", end_time - start_time)

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
                            pass
                            # print("html: ",file_html,cl,me,ast.unparse(code1[0]))
                            #                code_index_start_end_list.append([node,assign_stmt,node.lineno, node.end_lineno,assign_stmt_lineno,assign_block_list_str])

                            # result_compli_for_else_list.append(
                            #     [repo_name, file_html, cl, me, ast.unparse(code1[0][2]), ast.unparse(code1[1])])

            # print(f"{file_html} of {repo_name} has  {len(code_list)} code1 fragments")
        count_repo += repo_exist

    # a=dict(sorted(repo_code_num.items(), key=lambda item: item[1], reverse=True))
    # print(a)
    # print(np.median(list(a.values())), np.max(list(a.values())), np.min(list(a.values())))
    # print(np.median(files_num_list), np.max(files_num_list), np.min(files_num_list))
    # print(np.median(star_num_list), np.max(star_num_list), np.min(star_num_list))
    # print(np.median(contributor_num_list), np.max(contributor_num_list), np.min(contributor_num_list))
    print("count: ", count_repo, code_count, file_count, me_count, all_count_repo, all_file_count, all_me_count)
    end_time = time.time()
    print("total time: ", end_time - start_time)
    # 1 156 2943 100 1 2990 40102 salt
    # 791 2010 103165 1291 800 121348 1192868
    # util.save_csv(util.data_root + "transform_complicate_to_simple_pkl/var_unpack_call_star_complicated.csv", result_compli_for_else_list,
    #               ["repo_name", "file_html", "class_name", "me_name", "for_code", "assign_code"])
    #


    # print("len all_files: ", len(all_files))
    # count=0
    # count_file=0
    # for file_name in os.listdir(save_complicated_code_dir):
    #     complicate_code = util.load_pkl(save_complicated_code_dir, file_name[:-4])
    #     for each_file in complicate_code:
    #         # for code_list, file_path,file_html in each_file:
    #         #
    #         #     print("count: ",code_list)
    #         code_map = each_file[0]
    #         file_path = each_file[1]
    #         file_html = each_file[2]
    #         count_file+=1
    #         for  node, item in code_map.items():
    #             count+=len(item)
    # print("count: ", count, count_file,len(os.listdir(save_complicated_code_dir)))
    #

    '''
    count=0
    result_compli_for_else_list=[]
    for file_name in os.listdir(save_complicated_code_dir):
        complicate_code=util.load_json(save_complicated_code_dir,file_name[:-5])
        for each_file in complicate_code:

            # for code_list, file_path,file_html in each_file:
            #
            #     print("count: ",code_list)
                code_list=each_file[0]
                file_path=each_file[1]
                file_html=each_file[2]
                count += len(code_list)
                # print("count: ", count)
                for code1 in code_list:
                    repo_name = file_html.split("/")[4]
                    result_compli_for_else_list.append(
                        [repo_name, code1[1], code1[0] ,code1[2], file_html, file_path])

            #     print("one code1: ",repo_name,code1,file_html,file_path)
            #     break
            # break
        # print("file: ",file_name)
        # break
    print("count: ",count,len(os.listdir(save_complicated_code_dir)))
    util.save_csv(util.data_root+"complicated_code_dir/var_unpack_func_call_only_same_dengcha_subscript_complicated.csv",result_compli_for_else_list,["repo_name","code1","start_end","file_html","file_path"])
    '''



