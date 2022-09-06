
import sys, ast, os, copy
import tokenize
import sys,shutil

sys.path.append("..")
sys.path.append("../../")
pro_root="/".join(os.path.abspath(__file__).split("/")[:-3])+"/"
sys.path.append(pro_root+"code/")
sys.path.append(pro_root+"code/test_case")
sys.path.append(pro_root+"code/transform_c_s")

import time
import util, github_util,get_test_case_acc_util,configure_pro_envir_util
if __name__ == '__main__':

    save_test_acc_dir = util.data_root + "test_case_benchmark_dir/for_compre_set_acc_dir/"
    save_test_acc_dir = util.data_root + "test_case_benchmark_dir/var_unpack_call_star_complicated_dir/"
    save_test_acc_dir = util.data_root + "test_case_benchmark_dir/var_unpack_for_target_complicated_dir/"
    save_test_acc_dir = util.data_root + "test_case_benchmark_dir/for_compre_dict_acc_dir/"
    save_test_acc_dir = util.data_root + "test_case_benchmark_dir/for_compre_list_acc_dir/"
    save_test_acc_dir = util.data_root + "test_case_benchmark_dir/chain_comparison_acc_dir/"
    save_test_acc_dir = util.data_root + "test_case_benchmark_dir/multip_assign_complicated_acc_dir/"
    save_test_acc_dir = util.data_root + "test_case_benchmark_dir/truth_value_test_complicated_remove_is_is_not_acc_dir_copy/"
    save_test_acc_dir = util.data_root + "test_case_benchmark_dir/for_else_acc_dir/"
    save_test_acc_dir = util.data_root + "test_case_benchmark_dir/truth_value_test_complicated_remove_len_dir/"

    # save_test_acc_dir = util.data_root + "acc_res_compli_test_case/for_compre_list_acc_dir/"
    #
    # #save_test_case_benchmark_dir
    # save_test_acc_dir = util.data_root + "test_case_benchmark_dir/for_compre_dict_acc_dir/"
    save_test_case_benchmark_dir=util.data_root + "test_case_benchmark_dir_csv/"
    result_csv=[]

    for file in os.listdir(save_test_acc_dir):
        repo_name = file[:-4]
        complicate_code = util.load_pkl(save_test_acc_dir, repo_name)
        res=complicate_code['record_res']
        result_csv.extend(res)


    save_test_acc_dir_list=[util.data_root + "test_case_benchmark_dir/for_compre_set_acc_dir/",
                            util.data_root + "test_case_benchmark_dir/var_unpack_call_star_complicated_dir/",
                            util.data_root + "test_case_benchmark_dir/var_unpack_for_target_complicated_dir/",
                            util.data_root + "test_case_benchmark_dir/for_compre_dict_acc_dir/",
                            util.data_root + "test_case_benchmark_dir/for_compre_list_acc_dir/",
                            util.data_root + "test_case_benchmark_dir/chain_comparison_acc_dir/",
                            util.data_root + "test_case_benchmark_dir/multip_assign_complicated_acc_dir/",

                            util.data_root + "test_case_benchmark_dir/for_else_acc_dir/",
                            util.data_root + "test_case_benchmark_dir/truth_value_test_complicated_remove_len_dir/" ]
    repos = set([])
    for save_test_acc_dir in save_test_acc_dir_list:
        for file in os.listdir(save_test_acc_dir):
            repo_name = file[:-4]
            complicate_code = util.load_pkl(save_test_acc_dir, repo_name)
            res=complicate_code['record_res']
            # result_csv.extend(res)
            for e in res:
                repos.add(e[0])
    # print(result_csv[0])
    print(len(repos))

    # util.save_csv(save_test_case_benchmark_dir+"for_compre_set.csv",
    #                   result_csv,
    #                   ["repo_name", "file_html", "class_name", "me_name", "line_no", "old_code", "new_code","remove_ass_flag",'success','test_case_info'])
    #
    # util.save_csv(save_test_case_benchmark_dir+"call_star.csv",
    #                   result_csv,
    #                   ["repo_name", "file_html", "class_name", "me_name", "line_no", "old_code", "new_code",'success','test_case_info'])
    #
    # util.save_csv(save_test_case_benchmark_dir+"for_compre_dict.csv",
    #                   result_csv,
    #                   ["repo_name", "file_html", "class_name", "me_name", "line_no", "old_code", "new_code","remove_ass_flag",'success','test_case_info'])
    #
    # util.save_csv(save_test_case_benchmark_dir+"for_compre_list.csv",
    #                   result_csv,
    #                   ["repo_name", "file_html", "class_name", "me_name", "line_no", "old_code", "new_code","remove_ass_flag",'success','test_case_info'])

    # util.save_csv(save_test_case_benchmark_dir+"chain_compare.csv",
    #               result_csv,
    #               ["repo_name", "file_html", "class_name", "me_name", "line_no", "old_code", "new_code",
    #               'success','test_case_info'])
    # util.save_csv(save_test_case_benchmark_dir+ "multiple_assign.csv",
    #               result_csv,
    #               ["repo_name", "file_html", "class_name", "me_name","line_no", "old_code", "new_code",
    #                'success','test_case_info'])
    # util.save_csv(save_test_case_benchmark_dir+ "truth_value_test_remove_len.csv",
    #               result_csv,
    #               ["repo_name", "file_html", "class_name", "me_name","line_no", "old_code", "new_code",
    #                'success','test_case_info'])

    # util.save_csv(save_test_case_benchmark_dir + "for_else.csv",
    #               result_csv,
    #               ["repo_name", "file_html", "class_name", "me_name", "line_no", "old_code", "new_code","init_ass_remove_flag",
    #                'success', 'test_case_info'])

   # util.save_csv(save_test_case_benchmark_dir+"for_compre_dict.csv",
    #                   result_csv,
    #                   ["repo_name", "file_html", "class_name", "me_name", "line_no", "old_code", "new_code","remove_ass_flag",'success','test_case_info'])
    # util.save_csv(save_test_case_benchmark_dir+"for_compre_list.csv",
    #                   result_csv,
    #                   ["repo_name", "file_html", "class_name", "me_name", "line_no", "old_code", "new_code","remove_ass_flag",'success','test_case_info'])
    # util.save_csv(save_test_case_benchmark_dir+"var_unpack_call_star_complicated.csv", result_csv,
    #               ["repo_name", "file_html", "class_name", "me_name", "line_no", "old_code", "new_code",'success','test_case_info'])
    # util.save_csv(save_test_case_benchmark_dir+"var_unpack_for_target_complicated.csv",
    #               result_csv,
    #               ["repo_name", "file_html", "class_name", "me_name", "line_no", "old_code", "new_code"
    #                   ,'success','test_case_info'])
    # util.save_csv(save_test_case_benchmark_dir+ "for_else.csv",
    #               result_csv,
    #               ["repo_name", "file_html", "class_name", "me_name", "line_no", "old_code", "new_code"
    #                   ,'success','test_case_info'])
    #

    #
    # util.save_csv(save_test_case_benchmark_dir+"truth_value_test.csv", result_csv,
    #               ["repo_name", "file_html", "class_name", "me_name", "line_no", "old_code", "new_code",
    #                'success','test_case_info'])




