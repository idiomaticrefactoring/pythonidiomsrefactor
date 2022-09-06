import sys,ast,os
pro_root="/".join(os.path.abspath(__file__).split("/")[:-3])+"/"
sys.path.append(pro_root+"code/")

import time,complicated_code_util
import util
start_time = time.time()
save_complicated_code_dir_pkl = util.data_root + "transform_complicate_to_simple_pkl/var_unpack_for_target_complicated/"
save_complicated_code_dir_pkl = util.data_root + "transform_complicate_to_simple_pkl/var_unpack_call_star_complicated/"
# save_complicated_code_dir_pkl = util.data_root + "transform_complicate_to_simple_pkl/var_unpack_call_star_complicated_strict/"

save_complicated_code_dir_pkl = util.data_root + "transform_complicate_to_simple_pkl/for_compre_list/"
# save_complicated_code_dir_pkl = util.data_root + "transform_complicate_to_simple_pkl/for_compre_set/"
save_complicated_code_dir_pkl = util.data_root + "transform_complicate_to_simple_pkl/for_compre_dict/"
save_complicated_code_dir_pkl = util.data_root + "transform_complicate_to_simple_pkl/chain_comparison/"
# save_complicated_code_dir_pkl = util.data_root + "transform_complicate_to_simple_pkl/truth_value_test_complicated_remove_is_is_not/"
# save_complicated_code_dir_pkl = util.data_root + "transform_complicate_to_simple_pkl/for_else/"
# save_complicated_code_dir_pkl = util.data_root + "transform_complicate_to_simple_pkl/multip_assign_complicated/"

dict_repo_file_python = util.load_json(util.data_root, "python3_1000repos_files_info")
print("num of repos: ",len(list(dict_repo_file_python.keys())))
repo_name_list=[]

for repo_name in dict_repo_file_python:
        if os.path.exists(save_complicated_code_dir_pkl + repo_name + ".pkl"):

            continue
        #     return None
        # if repo_name!="spiderfoot":
        #     continue
        repo_name_list.append(repo_name)

print("repo num: ", len(repo_name_list))
repo_num_list=[]
dict_repo_num_type=dict()
dict_file_num_type=dict()
dict_met_num_type=dict()
file_num_list=[]
met_num_list=[]
files_num_list = []
star_num_list = []
contributor_num_list = []
count_repo, file_count, me_count, code_count = 0, 0, 0, 0
file_list = set([])
repo_code_num = dict()
result_compli_for_else_list = []
all_count_repo, all_file_count, all_me_count = 0, 0, 0
code_list=["transform_complicate_to_simple_pkl/for_compre_list/", "transform_complicate_to_simple_pkl/for_compre_set/",
           "transform_complicate_to_simple_pkl/for_compre_dict/","transform_complicate_to_simple_pkl/chain_comparison/",
           "transform_complicate_to_simple_pkl/for_else/",
           "transform_complicate_to_simple_pkl/multip_assign_complicated/",
           "transform_complicate_to_simple_pkl/var_unpack_for_target_complicated/",
           "transform_complicate_to_simple_pkl/var_unpack_call_star_complicated/",
           "transform_complicate_to_simple_pkl/truth_value_test_complicated_remove_is_is_not_no_len/"]
'''
for complicated_code_dir_pkl in code_list[:]:
    save_complicated_code_dir_pkl=util.data_root +complicated_code_dir_pkl
    for file_name in os.listdir(save_complicated_code_dir_pkl):
        all_count_repo += 1
        repo_name = file_name[:-4]
        code_count = 0

        complicate_code = util.load_pkl(save_complicated_code_dir_pkl, repo_name)

        repo_exist = 0

        for file_html in complicate_code:
            file_exist = 0
            file_code_count=0
            for cl in complicate_code[file_html]:
                if complicate_code[file_html][cl]:
                    all_me_count += len(complicate_code[file_html][cl].keys())
                    for me in complicate_code[file_html][cl]:
                        if complicate_code[file_html][cl][me]:

                            file_exist = 1
                            repo_exist=1
                            code_count += len(complicate_code[file_html][cl][me])
                            file_code_count+= len(complicate_code[file_html][cl][me])
                            total_me = "".join([file_html, cl, me])
                            if total_me in dict_met_num_type:
                                dict_met_num_type[total_me] += len(complicate_code[file_html][cl][me])
                            else:
                                dict_met_num_type[total_me] = len(complicate_code[file_html][cl][me])


            if file_exist:
                if file_html in dict_file_num_type:
                    dict_file_num_type[file_html] += file_code_count
                else:
                    dict_file_num_type[file_html] = file_code_count

        count_repo += repo_exist
        if repo_exist:
            if repo_name in dict_repo_num_type:
                dict_repo_num_type[repo_name]+=code_count
            else:
                dict_repo_num_type[repo_name] =code_count

util.save_pkl(util.data_root+"boxplot/", "dict_repo_num_code",dict_repo_num_type)
util.save_pkl(util.data_root+"boxplot/", "dict_file_num_code",dict_file_num_type)
util.save_pkl(util.data_root+"boxplot/", "dict_met_num_code",dict_met_num_type)
'''
dict_repo_num_type = util.load_pkl(util.data_root+"boxplot/", "dict_repo_num_code")

dict_file_num_type = util.load_pkl(util.data_root+"boxplot/", "dict_file_num_code")
dict_met_num_type = util.load_pkl(util.data_root+"boxplot/", "dict_met_num_code")

# a=dict(sorted(repo_code_num.items(), key=lambda item: item[1], reverse=True))
# print(a)
# print(np.median(list(a.values())), np.max(list(a.values())), np.min(list(a.values())))
# print(np.median(files_num_list), np.max(files_num_list), np.min(files_num_list))
# print(np.median(star_num_list), np.max(star_num_list), np.min(star_num_list))
# print(np.median(contributor_num_list), np.max(contributor_num_list), np.min(contributor_num_list))
# print("count: ", count_repo, code_count, file_count, me_count, all_count_repo, all_file_count, all_me_count)
end_time = time.time()
print("total time: ", end_time - start_time)
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams["figure.figsize"] = [3, 3.5]
plt.rcParams["figure.autolayout"] = True
#https://blog.csdn.net/weixin_43584807/article/details/101268400
plt.rcParams["axes.spines.right"] = False
plt.rcParams["axes.spines.top"] = False

res_csv_list_num=[]
all_diff_ratio_list=[list(dict_repo_num_type.values()),list(dict_file_num_type.values()),list(dict_met_num_type.values())]

x_position_fmt=["repo","file","met"]
x_position=[0.1+i*1 for i in range(3)]

# plt.xticks([1], [x_position_fmt[0]])
plt.boxplot(all_diff_ratio_list[:3],positions=x_position,widths=0.2,autorange=True)
plt.xticks([i for i in x_position] ,x_position_fmt )
# plt.text(0.7, np.median(diff_ratio_list), str(np.round(np.median(diff_ratio_list), 2)))
for i in range(len(all_diff_ratio_list)):
    plt.text(0.25+i*1, np.median(all_diff_ratio_list[i]), str(int(np.median(all_diff_ratio_list[i]))))

# plt.ylim(0,10)
# plt.xticks([1], ["Set Compre"])
# plt.text(0.7, np.median(diff_ratio_list), str(np.round(np.median(diff_ratio_list),2)))
plt.ylabel("the number of code instances")
plt.yscale("log")
plt.show()
print("median: ",np.median(all_diff_ratio_list[0]))
print("median: ",np.median(all_diff_ratio_list[1]))
for i in range(3):
    plt.boxplot(all_diff_ratio_list[i:i+1],positions=[x_position[0]],widths=0.2)
    plt.xticks([x_position[0]] ,[x_position_fmt[i]] )
    plt.yscale("log")
    # plt.ylim(0,10)
    # plt.xticks([1], ["Set Compre"])
    plt.text(0.7, np.median(all_diff_ratio_list[i]), str(int(np.median(all_diff_ratio_list[i]))))
    plt.ylabel("the number of code instances")
    plt.show()
# util.save_csv(util.data_root + "boxplot/"+"dict_repo_file_me_code_num.csv",
#                   all_diff_ratio_list)