
import sys, ast, os, copy
import tokenize
import sys
pro_root="/".join(os.path.abspath(__file__).split("/")[:-1])+"/"
sys.path.append(pro_root+"code/")
sys.path.append(pro_root+"code/transform_c_s")
sys.path.append("..")
sys.path.append("../../")

import time
import util,github_util,complicated_code_util
dict_repo_file_python = util.load_json(util.data_root, "python3_1000repos_files_info")

save_me_test_me_dir1= util.data_root + "methods_test_method_pair/for_else/"
save_me_test_me_dir2= util.data_root + "methods_test_method_pair/chain_comparison/"
save_me_test_me_dir3= util.data_root + "methods_test_method_pair/multip_assign_complicated/"
save_me_test_me_dir4= util.data_root + "methods_test_method_pair/var_unpack_for_target_complicated/"
save_me_test_me_dir5= util.data_root + "methods_test_method_pair/var_unpack_call_star_complicated/"
save_me_test_me_dir6= util.data_root + "methods_test_method_pair/for_compre_dict/"
save_me_test_me_dir7= util.data_root + "methods_test_method_pair/for_compre_list/"
save_me_test_me_dir8= util.data_root + "methods_test_method_pair/for_compre_set/"
save_me_test_me_dir9= util.data_root + "methods_test_method_pair/truth_value_test_complicated_remove_is_is_not/"
save_me_test_me_dir_list=[save_me_test_me_dir1,save_me_test_me_dir2,save_me_test_me_dir3,
                          save_me_test_me_dir4,save_me_test_me_dir5,save_me_test_me_dir6,
                          save_me_test_me_dir7,save_me_test_me_dir8,save_me_test_me_dir9]

count_code = 0
count_me = 0
count_repo = 0
repo_list=set([])
for save_me_test_me_dir in save_me_test_me_dir_list:
    dict_intersect_test_methods = dict()
    for repo_name in dict_repo_file_python:
        if not os.path.exists(save_me_test_me_dir+repo_name+".pkl"):
            continue
        dict_comp_file = util.load_pkl(save_me_test_me_dir, repo_name)
        dict_intersect_test_methods[repo_name]= dict_comp_file
    count_file = 0
    for repo_name in dict_intersect_test_methods:
        for file_html in dict_intersect_test_methods[repo_name]:
            count_file += 1
            for full_me in dict_intersect_test_methods[repo_name][file_html]:
                count_code += dict_intersect_test_methods[repo_name][file_html][full_me]["complica_num"]
                count_me += 1
        count_repo += 1
        repo_list.add(repo_name)
print("has test case of repos: ", len(repo_list))
