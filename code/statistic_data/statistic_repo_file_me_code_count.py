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
def get_total_name(file_html,cl,me_name):
    map_file_name = file_html.split("/")[-1][:-3]
    real_file_html = file_html.replace("//", "/")
    rela_path = ".".join(real_file_html.split("/")[6:-1])

    if rela_path:
        total_name = ".".join([rela_path, map_file_name, cl, me_name])
    else:
        total_name = ".".join([map_file_name, cl, me_name])
    total_name = total_name.replace("..", ".")
    return total_name
'''
def get_code_count(complicate_code,repo_name):
    repo_list=set([])
    file_list = set([])
    me_list=set([])
    code_count=0
    for file_html in complicate_code:

        if complicate_code[file_html]:
            file_exist = 0
            # cl_count +=len(list(complicate_code[file_html].keys()))
            for cl in complicate_code[file_html]:
                if complicate_code[file_html][cl]:
                    for me in complicate_code[file_html][cl]:
                        if complicate_code[file_html][cl][me]:

                            me_list.add(get_total_name(file_html,cl,me))
                            file_list.add(file_html)
                            code_count += len(complicate_code[file_html][cl][me])
    if file_list:
        repo_list.add(repo_name)
    return  repo_list,file_list,me_list,code_count
'''
def get_complicated_repo_file_me_code_info(complicate_code_dir_list):
    all_files_list = set([])
    all_repo_list = set([])
    all_me_list = set([])
    all_code_count = 0
    for save_complicated_code_dir_pkl in complicate_code_dir_list:
        the_type_all_repo_name_list, the_type_all_file_with_test_list, the_type_all_me_with_test_list, the_type_all_code_with_test_count = set(
            []), set(
            []), set([]), 0
        for file_name in os.listdir(save_complicated_code_dir_pkl):
            repo_name = file_name[:-4]

            complicate_code = util.load_pkl(save_complicated_code_dir_pkl, repo_name)

            repo_list, file_list, me_list, code_count = complicated_code_util.get_code_info(
                complicate_code, repo_name)
            all_repo_list |= repo_list
            all_files_list |= file_list
            all_me_list |= me_list
            all_code_count += code_count
            the_type_all_repo_name_list |= repo_list
            the_type_all_file_with_test_list |= file_list
            the_type_all_me_with_test_list |= me_list
            the_type_all_code_with_test_count += code_count
        print(save_test_acc_dir, " has can run test case number: ", len(the_type_all_repo_name_list),
              len(the_type_all_file_with_test_list),
              len(the_type_all_me_with_test_list), the_type_all_code_with_test_count)

    count_repo, file_count, me_count = len(all_repo_list), len(all_files_list), len(all_me_list)
    print("count: ", count_repo, file_count, me_count, all_code_count)
'''
def get_code_count_contain_test(complicate_code,repo_name):
    code_no_test_count=0,0,0
    repo_name_list,file_no_test_list, me_no_test_list, code_no_test_list=set([]),set([]),set([]),set([])
    for file_html in complicate_code:
        no_test_flag=0
        map_file_name = file_html.split("/")[-1][:-3]
        # filter out test files
        if not (map_file_name.startswith("test_") or map_file_name.endswith("_test")):
            no_test_flag=1
        if complicate_code[file_html]:
            for cl in complicate_code[file_html]:
                if complicate_code[file_html][cl]:
                    for me in complicate_code[file_html][cl]:
                        if complicate_code[file_html][cl][me]:
                            if no_test_flag:
                                file_no_test_list.add(file_html)
                                me_no_test_list.add(get_total_name(file_html, cl, me))
                                code_no_test_count += len(complicate_code[file_html][cl][me])
    if file_no_test_list:
        repo_name_list.add(repo_name)

    return repo_name_list, file_no_test_list, me_no_test_list, code_no_test_count
'''
def get_no_test_method_complicated_repo_file_me_code_info(compl_code_no_test_dir_list):
        all_repo_name_list, all_file_no_test_list, all_me_no_test_list, all_code_no_test_count=set([]),set([]),set([]),0
        for compl_code_no_test_dir in compl_code_no_test_dir_list:
            the_type_all_repo_name_list, the_type_all_file_with_test_list, the_type_all_me_with_test_list, the_type_all_code_with_test_count = set(
                []), set(
                []), set([]), 0
            for file_name in os.listdir(compl_code_no_test_dir):
                repo_name = file_name[:-4]
                complicate_code = util.load_pkl(compl_code_no_test_dir, repo_name)
                repo_name_list, file_no_test_list, me_no_test_list, code_no_test_count=\
                    complicated_code_util.get_code_info_contain_test(complicate_code, repo_name)
                all_repo_name_list|=repo_name_list
                all_file_no_test_list|=file_no_test_list
                all_me_no_test_list|=me_no_test_list
                all_code_no_test_count+=code_no_test_count
                the_type_all_repo_name_list |= repo_name_list
                the_type_all_file_with_test_list |= file_no_test_list
                the_type_all_me_with_test_list |= me_no_test_list
                the_type_all_code_with_test_count += code_no_test_count
            print(save_test_acc_dir, " has can run test case number: ", len(the_type_all_repo_name_list),
                  len(the_type_all_file_with_test_list),
                  len(the_type_all_me_with_test_list), the_type_all_code_with_test_count)

        print("count except for test files: ",len(all_repo_name_list),len(all_file_no_test_list),
              len(all_me_no_test_list),all_code_no_test_count)
def get_complicate_with_test_case_code_info(complicate_code_with_test_case_dir_list):
    all_repo_name_list, all_file_with_test_list, all_me_with_test_list, all_code_with_test_count = set([]), set([]), set([]), 0
    for compl_code_no_test_dir in complicate_code_with_test_case_dir_list:
        the_type_all_repo_name_list, the_type_all_file_with_test_list, the_type_all_me_with_test_list, the_type_all_code_with_test_count = set(
            []), set(
            []), set([]), 0
        for file_name in os.listdir(compl_code_no_test_dir):
            repo_name = file_name[:-4]
            complicate_code = util.load_pkl(compl_code_no_test_dir, repo_name)
            repo_name_list, file_no_test_list, me_no_test_list, code_no_test_count = \
                complicated_code_util.get_code_info_with_test_case(complicate_code, repo_name)
            all_repo_name_list |= repo_name_list
            all_file_with_test_list |= file_no_test_list
            all_me_with_test_list |= me_no_test_list
            all_code_with_test_count += code_no_test_count
            the_type_all_repo_name_list |= repo_name_list
            the_type_all_file_with_test_list |= file_no_test_list
            the_type_all_me_with_test_list |= me_no_test_list
            the_type_all_code_with_test_count += code_no_test_count
        print(save_test_acc_dir, " has can run test case number: ", len(the_type_all_repo_name_list),
              len(the_type_all_file_with_test_list),
              len(the_type_all_me_with_test_list), the_type_all_code_with_test_count)

    print("has test case number: ", len(all_repo_name_list), len(all_file_with_test_list),
          len(all_me_with_test_list), all_code_with_test_count)
def get_complicate_test_case_success_code_info(save_test_acc_dir_list):
        all_repo_name_list, all_file_with_test_list, all_me_with_test_list, all_code_with_test_count = set([]), set(
            []), set([]), 0

        for save_test_acc_dir in save_test_acc_dir_list:
            the_type_all_repo_name_list, the_type_all_file_with_test_list, the_type_all_me_with_test_list, the_type_all_code_with_test_count = set(
                []), set(
                []), set([]), 0
            for file_name in os.listdir(save_test_acc_dir):
                repo_name = file_name[:-4]
                complicate_code = util.load_pkl(save_test_acc_dir, repo_name)
                repo_name_list, file_no_test_list, me_no_test_list,code_count=\
                    complicated_code_util.get_code_info_with_success_test_case(complicate_code, repo_name)
                all_repo_name_list |= repo_name_list
                all_file_with_test_list |= file_no_test_list
                all_me_with_test_list |= me_no_test_list
                all_code_with_test_count += code_count
                the_type_all_repo_name_list |= repo_name_list
                the_type_all_file_with_test_list |= file_no_test_list
                the_type_all_me_with_test_list |= me_no_test_list
                the_type_all_code_with_test_count += code_count
            print(save_test_acc_dir, " has can run test case number: ", len(the_type_all_repo_name_list),
                  len(the_type_all_file_with_test_list),
                  len(the_type_all_me_with_test_list), the_type_all_code_with_test_count)

        print("has successful test case number: ", len(all_repo_name_list), len(all_file_with_test_list),
          len(all_me_with_test_list), all_code_with_test_count)
def get_compl_test_case_can_run(save_test_can_run_list):
    all_repo_name_list, all_file_with_test_list, all_me_with_test_list, all_code_with_test_count = 0,0,0,0
    for ind,save_test_file_res_dir in enumerate(save_test_can_run_list):
        the_type_all_repo_name_list, the_type_all_file_with_test_list, the_type_all_me_with_test_list, the_type_all_code_with_test_count =0, 0, 0, 0
        for file_name in os.listdir(save_test_file_res_dir):
            repo_name = file_name[:-4]

            repo_name_list, file_no_test_list, me_no_test_list, code_count = \
                complicated_code_util.get_code_info_with_can_run_test_case(repo_name,save_test_file_res_dir,complicate_code_with_test_case_dir_list[ind],complicate_code_dir_list[ind])
            all_repo_name_list += repo_name_list
            all_file_with_test_list += file_no_test_list
            all_me_with_test_list += me_no_test_list
            all_code_with_test_count += code_count
            the_type_all_repo_name_list += repo_name_list
            the_type_all_file_with_test_list += file_no_test_list
            the_type_all_me_with_test_list += me_no_test_list
            the_type_all_code_with_test_count += code_count
        print(save_test_file_res_dir, " has can run test case number: ", the_type_all_repo_name_list, the_type_all_file_with_test_list,
              the_type_all_me_with_test_list, the_type_all_code_with_test_count)
    print("has can run test case number: ", all_repo_name_list, all_file_with_test_list,
          all_me_with_test_list, all_code_with_test_count)


if __name__ == '__main__':
    pass
    pre_complicate_code_dir=util.data_root +"transform_complicate_to_simple_pkl/"
    complicate_code_dir_list=[
        pre_complicate_code_dir +"for_else/",
        pre_complicate_code_dir + "var_unpack_for_target_complicated/",
        pre_complicate_code_dir + "var_unpack_call_star_complicated/",
        pre_complicate_code_dir + "multip_assign_complicated/",
        pre_complicate_code_dir + "for_compre_list/",
        pre_complicate_code_dir + "for_compre_set/",
        pre_complicate_code_dir + "for_compre_dict/",
        pre_complicate_code_dir + "truth_value_test_complicated/",
        pre_complicate_code_dir + "chain_comparison/"
    ]
    # pre_compl_code_no_test_dir=util.data_root + "methods/"
    # compl_code_no_test_dir_list=[
    #     pre_compl_code_no_test_dir + "for_else/",
    #     pre_compl_code_no_test_dir + "var_unpack_for_target_complicated/",
    #     pre_compl_code_no_test_dir + "var_unpack_call_star_complicated/",
    #     pre_compl_code_no_test_dir + "multip_assign_complicated/",
    #     pre_compl_code_no_test_dir + "for_compre_list/",
    #     pre_compl_code_no_test_dir + "for_compre_set/",
    #     pre_compl_code_no_test_dir + "for_compre_dict/",
    #     pre_compl_code_no_test_dir + "truth_value_test_complicated/",
    #     pre_compl_code_no_test_dir + "chain_comparison/"
    # ]
    pre_compl_code_with_test_case_dir=util.data_root + "methods_test_method_pair/"
    complicate_code_with_test_case_dir_list=[
        pre_compl_code_with_test_case_dir + "for_else/",
        pre_compl_code_with_test_case_dir + "var_unpack_for_target_complicated/",
        pre_compl_code_with_test_case_dir + "var_unpack_call_star_complicated/",
        pre_compl_code_with_test_case_dir + "multip_assign_complicated/",
        pre_compl_code_with_test_case_dir + "for_compre_list/",
        pre_compl_code_with_test_case_dir + "for_compre_set/",
        pre_compl_code_with_test_case_dir + "for_compre_dict/",
        pre_compl_code_with_test_case_dir + "truth_value_test_complicated/",
        pre_compl_code_with_test_case_dir + "chain_comparison/"
    ]
    pre_test_can_run_dir = util.data_root + "save_test_file_res_dir/"
    save_test_can_run_list = [
        pre_test_can_run_dir + "for_else/",
        pre_test_can_run_dir + "var_unpack_for_target_complicated/",
        pre_test_can_run_dir + "var_unpack_call_star_complicated/",
        pre_test_can_run_dir + "multip_assign_complicated/",
        pre_test_can_run_dir + "for_compre_list/",
        pre_test_can_run_dir + "for_compre_set/",
        pre_test_can_run_dir + "for_compre_dict/",
        pre_test_can_run_dir + "truth_value_test_complicated/",
        pre_test_can_run_dir + "chain_comparison/"
    ]
    pre_test_acc_dir= util.data_root + "acc_res_compli_test_case/"
    save_test_acc_dir_list=[
        pre_test_acc_dir + "for_else_complicated_acc_dir/",
        pre_test_acc_dir + "var_unpack_for_target_complicated_acc_dir/",
        pre_test_acc_dir + "var_unpack_call_star_complicated_acc_dir/",
        pre_test_acc_dir + "multip_assign_complicated_acc_dir/",
        pre_test_acc_dir + "for_compre_list_complicated_acc_dir/",
        pre_test_acc_dir + "for_compre_set_acc_dir/",
        pre_test_acc_dir + "for_compre_dict_acc_dir/",
        pre_test_acc_dir + "truth_value_test_complicated_acc_dir/",
        pre_test_acc_dir + "chain_comparison_acc_dir/"
    ]
    save_test_acc_dir = util.data_root + "acc_res_compli_test_case/truth_value_test_complicated_acc_dir/"

    no_test_me_dir=[]
    # get_complicated_repo_file_me_code_info(complicate_code_dir_list)
    # get_no_test_method_complicated_repo_file_me_code_info(complicate_code_dir_list)
    # get_complicate_with_test_case_code_info(complicate_code_with_test_case_dir_list)
    get_compl_test_case_can_run(save_test_can_run_list)








