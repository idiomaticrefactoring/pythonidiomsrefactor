import sys, ast, os, copy
import tokenize
import sys
sys.path.append("..")
sys.path.append("../../")
pro_root="/".join(os.path.abspath(__file__).split("/")[:-3])+"/"
sys.path.append(pro_root+"code/")
import time
import util, github_util,get_test_case_acc_util,configure_pro_envir_util
from extract_simp_cmpl_data import ast_util
from extract_simp_cmpl_data.extract_compli_truth_value_test_code import decide_compare_complicate_truth_value
from pathos.multiprocessing import ProcessingPool as newPool
from transform_c_s.transform_truth_value_test_compli_to_simple import transform_c_s_truth_value_test
import format_api_call


def get_fail_projects(save_me_test_me_dir,save_test_acc_dir):
    dict_repo_test_case = dict()
    count = 0
    for file in os.listdir(save_me_test_me_dir):
        repo_name = file[:-4]
        # if repo_name != "salt":#"sympy":
        #     continue
        dict_repo_test_case[repo_name] = 0
        dict_me_test_me_pair = util.load_pkl(save_me_test_me_dir, repo_name)
        # print("dict_me_test_me_pair: ", dict_me_test_me_pair)
        for file_html in dict_me_test_me_pair:
            for full_name in dict_me_test_me_pair[file_html]:
                # print(dict_me_test_me_pair[full_name])
                dict_repo_test_case[repo_name] += dict_me_test_me_pair[file_html][full_name][
                    "complica_num"]  # len(dict_me_test_me_pair)
                count += dict_me_test_me_pair[file_html][full_name]["complica_num"]
    a = sorted(dict_repo_test_case.items(), key=lambda x: x[1], reverse=True)
    print(a)
    dict_repo_test_acc = get_test_case_acc_util.get_test_acc_info(save_test_acc_dir)
    again_repo_list = []
    for old_repo in dict_repo_test_case:
        if old_repo in dict_repo_test_acc and os.path.exists(save_me_test_me_dir+old_repo+".pkl"):
            if dict_repo_test_acc[old_repo]==0:
                again_repo_list.append(old_repo)
            dict_repo_test_case[old_repo] -= dict_repo_test_acc[old_repo]

        elif os.path.exists(save_me_test_me_dir+old_repo+".pkl"):
            again_repo_list.append(old_repo)
    return again_repo_list


if __name__ == '__main__':
    save_me_test_me_dir= util.data_root + "methods_test_method_pair/for_else/"
    # save_me_test_me_dir= util.data_root + "methods_test_method_pair/chain_comparison/"
    # save_me_test_me_dir= util.data_root + "methods_test_method_pair/multip_assign_complicated/"
    # save_me_test_me_dir= util.data_root + "methods_test_method_pair/var_unpack_for_target_complicated/"
    # save_me_test_me_dir= util.data_root + "methods_test_method_pair/var_unpack_call_star_complicated/"
    # save_me_test_me_dir= util.data_root + "methods_test_method_pair/for_compre_dict/"
    # save_me_test_me_dir= util.data_root + "methods_test_method_pair/for_compre_list/"
    # save_me_test_me_dir= util.data_root + "methods_test_method_pair/for_compre_set/"
    # save_me_test_me_dir= util.data_root + "methods_test_method_pair/truth_value_test_complicated/"
    # save_me_test_me_dir = util.data_root + "methods_test_method_pair/chain_comparison/"
    save_me_test_me_dir1 = util.data_root + "methods_test_method_pair/for_else/"
    save_me_test_me_dir2 = util.data_root + "methods_test_method_pair/chain_comparison/"
    save_me_test_me_dir3 = util.data_root + "methods_test_method_pair/multip_assign_complicated/"
    save_me_test_me_dir4 = util.data_root + "methods_test_method_pair/var_unpack_for_target_complicated/"
    save_me_test_me_dir5 = util.data_root + "methods_test_method_pair/var_unpack_call_star_complicated/"
    save_me_test_me_dir6 = util.data_root + "methods_test_method_pair/for_compre_dict/"
    save_me_test_me_dir7 = util.data_root + "methods_test_method_pair/for_compre_list/"
    save_me_test_me_dir8 = util.data_root + "methods_test_method_pair/for_compre_set/"
    save_me_test_me_dir9 = util.data_root + "methods_test_method_pair/truth_value_test_complicated_remove_is_is_not/"
    save_me_test_me_dir_list = [save_me_test_me_dir1, save_me_test_me_dir2, save_me_test_me_dir3,
                                save_me_test_me_dir4, save_me_test_me_dir5, save_me_test_me_dir6,
                                save_me_test_me_dir7, save_me_test_me_dir8, save_me_test_me_dir9]
    save_test_acc_dir1= util.data_root + "acc_res_compli_test_case/for_else_complicated_acc_dir/"
    save_test_acc_dir2= util.data_root + "acc_res_compli_test_case/chain_comparison_acc_dir/"
    save_test_acc_dir3 = util.data_root + "acc_res_compli_test_case/multip_assign_complicated_acc_dir/"
    save_test_acc_dir4 = util.data_root + "acc_res_compli_test_case/var_unpack_for_target_complicated_acc_dir/"
    save_test_acc_dir5 = util.data_root + "acc_res_compli_test_case/var_unpack_call_star_complicated_acc_dir/"
    save_test_acc_dir6 = util.data_root + "acc_res_compli_test_case/for_compre_dict_acc_dir/"
    save_test_acc_dir7 = util.data_root + "acc_res_compli_test_case/for_compre_list_complicated_acc_dir/"
    save_test_acc_dir8 = util.data_root + "get_test_case_acc_for_compre_set_parallel.py/"
    save_test_acc_dir9 = util.data_root + "acc_res_compli_test_case/truth_value_test_complicated_remove_is_is_not_acc_dir_copy/"
    save_test_acc_dir_list = [save_test_acc_dir1, save_test_acc_dir2, save_test_acc_dir3,
                                save_test_acc_dir4, save_test_acc_dir5, save_test_acc_dir6,
                                save_test_acc_dir7, save_test_acc_dir8, save_test_acc_dir9]

    all_repo_list=[]
    for ind,save_me_test_me_dir in enumerate(save_me_test_me_dir_list):
        if ind>=1:
            break
        print(">>>>>>>>>>>>>>>>save_me_test_me_dir: ",save_me_test_me_dir)
        dict_repo_test_case=dict()
        count=0
        for file in os.listdir(save_me_test_me_dir):
            repo_name=file[:-4]
            if repo_name != "salt":  # "sympy":
                continue
            dict_repo_test_case[repo_name]=0
            dict_me_test_me_pair = util.load_pkl(save_me_test_me_dir, repo_name)
            print("dict_me_test_me_pair: ",dict_me_test_me_pair)
            for file_html in dict_me_test_me_pair:
                for full_name in dict_me_test_me_pair[file_html]:
                    # print(dict_me_test_me_pair[full_name])
                    dict_repo_test_case[repo_name]+=dict_me_test_me_pair[file_html][full_name]["complica_num"]#len(dict_me_test_me_pair)
                    count+=dict_me_test_me_pair[file_html][full_name]["complica_num"]
        a = sorted(dict_repo_test_case.items(), key=lambda x: x[1], reverse=True)
        print(a)
        save_test_acc_dir=save_test_acc_dir_list[ind]
        dict_repo_test_acc=get_test_case_acc_util.get_test_acc_info(save_test_acc_dir)
        for old_repo in dict_repo_test_case:
            if old_repo in dict_repo_test_acc:
                dict_repo_test_case[old_repo]-=dict_repo_test_acc[old_repo]
        all_repo_list.append(list(dict_repo_test_case.keys()))
        if ind==7:
            print("for else and set comprehension intersect: ",set(all_repo_list[0])&set(all_repo_list[7]))
        a=sorted(dict_repo_test_case.items(),key=lambda x:x[1],reverse=True)

        print(a)
        count_100=0
        for ind,(repo,num) in enumerate(a):
            count_100+=num
            if count_100>=100:
                print(ind)
                break

        print("count: ",count)


