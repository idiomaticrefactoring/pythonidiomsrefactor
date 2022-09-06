import sys, ast, os, copy
import tokenize
import sys
sys.path.append("..")
sys.path.append("../../")
pro_root="/".join(os.path.abspath(__file__).split("/")[:-3])+"/"
sys.path.append(pro_root+"code/")
sys.path.append(pro_root+"code/transform_c_s")

import time
import util,github_util
from extract_simp_cmpl_data import ast_util
from extract_simp_cmpl_data.extract_compli_truth_value_test_code import decide_compare_complicate_truth_value
from pathos.multiprocessing import ProcessingPool as newPool
from transform_c_s.transform_truth_value_test_compli_to_simple import transform_c_s_truth_value_test
def seek_test_file(cur_dir,name):
    for root,dirs,files in os.walk(cur_dir):
        test_name_1="test_"+name
        test_name_2="".join([name[:-3],"_test",name[-3:]])
        for file in files:
            if test_name_1 == file or test_name_2 == file:
                # print(">>>>file exist: ",root,file)
                return 1,root+"/" + file

    return 0,None
def seek_test_file_list(cur_dir,file_list):
    intersect_files=set([])
    for root,dirs,files in os.walk(cur_dir):
        intersect_files|=(set(files)&set(file_list))


    return intersect_files
def get_test_num_quick(save_complicated_code_dir):
    count_file_exist = 0
    count_file=0
    repo_exist=0
    repo_count=0
    count_code=0
    count_code_exist=0
    for repo_file in os.listdir(save_complicated_code_dir):
        cur_repo_file_absolute_list=[]
        cur_repo_file_list=[]
        dict_files_code_count = dict()
        # files_num_list.append(repo_files_info[repo_name])
        # star_num_list.append(repo_star_info[repo_name])
        # contributor_num_list.append(repo_contributor_info[repo_name])
        if repo_file.endswith(".pkl"):
            complicate_code = util.load_pkl(save_complicated_code_dir, repo_file[:-4])
            repo_name = repo_file[:-4]
            pro_repo_dir = pro_dir + repo_name + "/"
            if complicate_code:
                repo_count+=1
            for each_file in complicate_code:

                code_map = each_file[0]
                file_path = each_file[1]
                file_name = file_path.split("/")[-1]
                test_1_file_name="test_"+file_name
                test_2_file_name = "".join([file_name[:-3], "_test", file_name[-3:]])
                cur_repo_file_list.extend([test_1_file_name,test_2_file_name])
                file_html = each_file[2]
                # print(file_html, file_name)
                for node, item in code_map.items():
                    dict_files_code_count[test_1_file_name]=len(item)
                    dict_files_code_count[test_2_file_name] = len(item)
                    count_code+=len(item)
        else:
            repo_name = repo_file[:-5]
            pro_repo_dir = pro_dir + repo_name + "/"
            complicate_code = util.load_json(save_complicated_code_dir, repo_name)
            if complicate_code:
                repo_count+=1
            for code_list, file_path, file_html in complicate_code:
                file_name = file_path.split("/")[-1]
                cur_repo_file_absolute_list.append(file_path)
                test_1_file_name = "test_" + file_name
                test_2_file_name = "".join([file_name[:-3], "_test", file_name[-3:]])
                dict_files_code_count[test_1_file_name] = len(code_list)
                dict_files_code_count[test_2_file_name] = len(code_list)
                count_code += len(code_list)
                cur_repo_file_list.extend([test_1_file_name, test_2_file_name])
        if cur_repo_file_list:
            pass
            # print("file list set: ",len(cur_repo_file_list),len(set(cur_repo_file_list)),len(cur_repo_file_absolute_list),len(set(cur_repo_file_absolute_list)))
        intersect_files = seek_test_file_list(pro_repo_dir, cur_repo_file_list)
        if intersect_files:
            repo_exist+=1
        count_file_exist+=len(intersect_files)
        count_file+=len(cur_repo_file_list)/2
        for file in intersect_files:
            count_code_exist+=dict_files_code_count[file]
        # for file in dict_files_code_count:
        #     count_code+=dict_files_code_count[file]


    print(save_complicated_code_dir,">>>>count: ", count_code/2,count_code_exist,repo_count,repo_exist,count_file_exist,count_file)

def get_test_num(save_complicated_code_dir):
    count_file_exist = 0
    count_file=0
    repo_exist=0
    repo_count=0
    count_code=0
    count_code_exist=0

    for file_name in os.listdir(save_complicated_code_dir):
        dict_file_file_html = dict()
        dict_test_file_file_html = dict()
        repo_name = file_name[:-5]
        pro_repo_dir = pro_dir + repo_name + "/"
        # files_num_list.append(repo_files_info[repo_name])
        # star_num_list.append(repo_star_info[repo_name])
        # contributor_num_list.append(repo_contributor_info[repo_name])
        if file_name.endswith(".pkl"):
            complicate_code = util.load_pkl(save_complicated_code_dir, file_name[:-4])
            if complicate_code:
                repo_count+=1
            count_code_fra = 0
            for each_file in complicate_code:
                count_file+=1
                # for code_list, file_path,file_html in each_file:
                #
                #     print("count: ",code_list)
                code_map = each_file[0]
                file_path = each_file[1]
                file_name = file_path.split("/")[-1]
                file_html = each_file[2]

                flag,test_file = seek_test_file(pro_repo_dir, file_name)
                # test_file_html="/".join(file_html.split("/")[:7]+test_file.split("/")[6:])
                # print("test_file_html: ",test_file_html)
                count_file_exist += flag
                count_code_fra += flag
                if flag:
                    # print(file_html, file_name)
                    if file_name not in dict_file_file_html:
                        dict_file_file_html[file_name] = [file_html]
                    else:
                        dict_file_file_html[file_name].append(file_html)
                    test_file_html = "/".join(file_html.split("/")[:7] + test_file.split("/")[7:])
                    if file_name not in dict_test_file_file_html:
                            dict_test_file_file_html[file_name] = [test_file_html]
                    else:
                            dict_test_file_file_html[file_name].append(test_file_html)


                for node, item in code_map.items():
                    count_code += len(item)
                    if flag:
                        count_code_exist +=len(item)
            if count_code_fra:
                repo_exist += 1

        else:
            complicate_code = util.load_json(save_complicated_code_dir, file_name[:-5])
            if complicate_code:
                repo_count+=1
            count_code_fra = 0
            for code_list, file_path, file_html in complicate_code:
                count_code+=len(code_list)
                file_name = file_path.split("/")[-1]

                count_file += 1
                # print("file_name: ", file_name, file_path)
                flag,test_file = seek_test_file(pro_repo_dir, file_name)

                count_file_exist += flag
                count_code_fra+=flag
                if flag:
                    if file_name not in dict_file_file_html:
                        dict_file_file_html[file_name] = [file_html]
                    else:
                        dict_file_file_html[file_name].append(file_html)
                    test_file_html = "/".join(file_html.split("/")[:7] + test_file.split("/")[7:])
                    if file_name not in dict_test_file_file_html:
                            dict_test_file_file_html[file_name] = [test_file_html]
                    else:
                            dict_test_file_file_html[file_name].append(test_file_html)
                    count_code_exist+=len(code_list)
                    # print("file is not existed ", file_path, file_name)
                    pass
            if count_code_fra:
                    repo_exist+=1

        for file_name in dict_file_file_html:
            if len(dict_file_file_html[file_name])>1:
                print("------------------>1------------------------")
                print(dict_file_file_html[file_name],dict_test_file_file_html[file_name])
            else:
                print("------------------=1------------------------")
                print(dict_file_file_html[file_name], dict_test_file_file_html[file_name])
    print(save_complicated_code_dir,">>>>count: ", count_code,count_code_exist,repo_count,repo_exist,count_file_exist,count_file)

if __name__ == '__main__':
    save_for_else_complicated_code_dir = util.data_root + "transform_complicate_to_simple/for_else_improve_5/"
    save_list_compre_complicated_code_dir = util.data_root + "complicated_code_dir/for_comrephension_list_complicated_only_one_stmt/"
    save_dict_compre_complicated_code_dir = util.data_root + "complicated_code_dir/for_comrephension_dict_complicated_only_one_stmt/"
    save_set_compre_complicated_code_dir = util.data_root + "complicated_code_dir/for_comrephension_set_complicated_only_one_stmt/"
    save_chained_compare_complicated_code_dir = util.data_root + "complicated_code_dir/chained_comparison_complicated/"
    save_truth_value_test_complicated_code_dir = util.data_root + "complicated_code_dir/truth_value_test_complicated/"
    save_call_fun_var_unpack_complicated_code_dir = util.data_root +  "complicated_code_dir/var_unpack_func_call_only_same_dengcha_subscript_complicated_pkl/"
    save_for_multi_targets_complicated_code_dir = util.data_root + "complicated_code_dir/var_unpack_for_target_complicated/"
    save_multi_assign_complicated_code_dir = util.data_root +  "complicated_code_dir/multip_assign_complicated_json/"
    pro_dir = util.data_root + "python_star_2000repo/"
    complica_code_dir_list=[save_for_else_complicated_code_dir,save_list_compre_complicated_code_dir,
                            save_dict_compre_complicated_code_dir,save_set_compre_complicated_code_dir,
                            save_chained_compare_complicated_code_dir,
                            save_for_multi_targets_complicated_code_dir,save_call_fun_var_unpack_complicated_code_dir,
                            save_multi_assign_complicated_code_dir,save_truth_value_test_complicated_code_dir ]
    for complica_code_dir in complica_code_dir_list[:1]:
        get_test_num(complica_code_dir)
        # get_test_num_quick(complica_code_dir)
            # relative_path
            # count += len(code_list)
            # count_code_fra += len(code_list)
            # file_num_list.append(len(code_list))
            # for code in code_list:
            #     repo_name = file_html.split("/")[4]
            #     file_list.add(file_html)
            #     result_compli_for_else_list.append([repo_name, code[0], code[1], file_html, file_path])
            # print(f"{file_html} of {repo_name} has  {len(code_list)} code fragments")
