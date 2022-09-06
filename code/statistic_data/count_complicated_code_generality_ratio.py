import sys,ast,os,copy
import tokenize

pro_root="/".join(os.path.abspath(__file__).split("/")[:-1])+"/"
sys.path.append(pro_root+"code/")
sys.path.append(pro_root+"code/transform_c_s")
sys.path.append("..")
sys.path.append("../../")

import util
from extract_simp_cmpl_data import ast_util
import complicated_code_util
from pathos.multiprocessing import ProcessingPool as newPool

dict_repo_file_python = util.load_json(util.data_root, "python3_1000repos_files_info")
# save_code_idiom_dir_pkl = util.data_root + "idiom_code_dir_pkl/multi_targets_for/"
save_code_idiom_dir_pkl = util.data_root + "idiom_code_dir_pkl/truth_value_test_idiom_code_improve/"

# save_code_idiom_dir_pkl = util.data_root + "idiom_code_dir_pkl/dict_comprehension_idiom_code/"
# save_code_idiom_dir_pkl = util.data_root + "idiom_code_dir_pkl/set_comprehension_idiom_code/"
# save_code_idiom_dir_pkl = util.data_root + "idiom_code_dir_pkl/list_comprehension_idiom_code/"
# save_code_idiom_dir_pkl = util.data_root + "idiom_code_dir_pkl/chained_comparison_idiom_code/"
save_code_idiom_dir_pkl = util.data_root + "idiom_code_dir_pkl/for_else_idiom_code_fragments/"
# save_code_idiom_dir_pkl = util.data_root + "idiom_code_dir_pkl/multi_assign_idiom_code/"
# save_code_idiom_dir_pkl = util.data_root + "idiom_code_dir_pkl/var_unpack_call_idiom_code_subscript_slice/"

save_complicated_code_dir_pkl = util.data_root + "transform_complicate_to_simple_pkl/var_unpack_for_target_complicated/"
# save_complicated_code_dir_pkl = util.data_root + "transform_complicate_to_simple_pkl/truth_value_test_complicated/"
# save_complicated_code_dir_pkl = util.data_root + "transform_complicate_to_simple_pkl/truth_value_test_complicated_remove_is_is_not/"
# save_complicated_code_dir_pkl = util.data_root + "transform_complicate_to_simple_pkl/truth_value_test_complicated_remove_is_is_not_no_len/"

# save_complicated_code_dir_pkl = util.data_root + "transform_complicate_to_simple_pkl/for_compre_dict/"
# save_complicated_code_dir_pkl=util.data_root + "transform_complicate_to_simple_pkl/for_compre_set/"
# save_complicated_code_dir_pkl = util.data_root + "transform_complicate_to_simple_pkl/for_compre_list/"
# save_complicated_code_dir_pkl = util.data_root + "transform_complicate_to_simple_pkl/chain_comparison/"
save_complicated_code_dir_pkl = util.data_root + "transform_complicate_to_simple_pkl/for_else/"
# save_complicated_code_dir_pkl = util.data_root + "transform_complicate_to_simple_pkl_improve_new_modify_bugs_final/for_else/"
# save_complicated_code_dir_pkl=util.data_root + "transform_complicate_to_simple_pkl/multip_assign_complicated/"
# save_complicated_code_dir_pkl = util.data_root + "transform_complicate_to_simple_pkl/var_unpack_call_star_complicated/"

total_count={'all_repo':set([]),'all_file':set([]),'all_me':set([]),'all_code':set([])}
for repo_name in dict_repo_file_python:
    if os.path.exists(save_complicated_code_dir_pkl+repo_name+'.pkl'):

        complicate_code = util.load_pkl(save_complicated_code_dir_pkl, repo_name)
        for file_html in complicate_code:

            if complicate_code[file_html]:
                file_exist = 0
                # cl_count +=len(list(complicate_code[file_html].keys()))
                for cl in complicate_code[file_html]:
                    if complicate_code[file_html][cl]:

                        for me in complicate_code[file_html][cl]:

                            if complicate_code[file_html][cl][me]:
                                total_count['all_repo'].add(repo_name)
                                total_count['all_file'].add(file_html)
                                me_name=complicated_code_util.get_total_name(file_html, cl, me)
                                total_count['all_me'].add(me_name)

    if os.path.exists(save_code_idiom_dir_pkl + repo_name + '.pkl'):

        complicate_code = util.load_pkl(save_code_idiom_dir_pkl, repo_name)
        for file_html in complicate_code:

            if complicate_code[file_html]:
                file_exist = 0
                # cl_count +=len(list(complicate_code[file_html].keys()))
                for cl in complicate_code[file_html]:
                    if complicate_code[file_html][cl]:

                        for me in complicate_code[file_html][cl]:

                            if complicate_code[file_html][cl][me]:
                                total_count['all_repo'].add(repo_name)
                                total_count['all_file'].add(file_html)
                                me_name = complicated_code_util.get_total_name(file_html, cl, me)
                                total_count['all_me'].add(me_name)
print(len(total_count['all_repo']),len(total_count['all_file']),len(total_count['all_me']))