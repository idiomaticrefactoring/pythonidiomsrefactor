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

        complicate_code = util.load_pkl(save_complicated_code_dir_pkl, repo_name)


        repo_exist = 0

        for file_html in complicate_code:
            file_exist=0
            for cl in complicate_code[file_html]:
                for me in complicate_code[file_html][cl]:

                    if complicate_code[file_html][cl][me]:
                        total_me = "".join([file_html, cl, me])
                        repo_exist = 1
                        me_exist=1
                        file_exist=1

                        if total_me in dict_met_num_type:
                                    dict_met_num_type[total_me] += 1
                        else:
                                    dict_met_num_type[total_me] = 1
            if file_exist:
                if file_html in dict_file_num_type:
                    dict_file_num_type[file_html] += 1
                else:
                    dict_file_num_type[file_html] = 1


                            # print("html: ",file_html,cl,me,ast.unparse(code[0]))
                            #                code_index_start_end_list.append([node,assign_stmt,node.lineno, node.end_lineno,assign_stmt_lineno,assign_block_list_str])

                            # result_compli_for_else_list.append(
                            #     [repo_name, file_html, cl, me, ast.unparse(code[0]), ast.unparse(code[1])])

            # print(f"{file_html} of {repo_name} has  {len(code_list)} code fragments")
        count_repo += repo_exist
        if repo_exist:
            if repo_name in dict_repo_num_type:
                dict_repo_num_type[repo_name]+=1
            else:
                dict_repo_num_type[repo_name] =1


# a=dict(sorted(repo_code_num.items(), key=lambda item: item[1], reverse=True))
# print(a)
# print(np.median(list(a.values())), np.max(list(a.values())), np.min(list(a.values())))
# print(np.median(files_num_list), np.max(files_num_list), np.min(files_num_list))
# print(np.median(star_num_list), np.max(star_num_list), np.min(star_num_list))
# print(np.median(contributor_num_list), np.max(contributor_num_list), np.min(contributor_num_list))
# print("count: ", count_repo, code_count, file_count, me_count, all_count_repo, all_file_count, all_me_count)
end_time = time.time()
print("total time: ", end_time - start_time)


util.save_pkl(util.data_root+"boxplot/", "dict_repo_num_type",dict_repo_num_type)
util.save_pkl(util.data_root+"boxplot/", "dict_file_num_type",dict_file_num_type)
util.save_pkl(util.data_root+"boxplot/", "dict_me_num_type",dict_met_num_type)
'''

dict_repo_num_type = util.load_pkl(util.data_root+"boxplot/", "dict_repo_num_type")
res_csv_list_num=[]
dict_num_type={i+1:0 for i in range(9)}
for repo in dict_repo_num_type:
    dict_num_type[dict_repo_num_type[repo]]+=1
for key,v in dict_num_type.items():
    res_csv_list_num.append([v])
print(dict_num_type)
dict_num_type={i+1:0 for i in range(9)}

dict_file_num_type = util.load_pkl(util.data_root+"boxplot/", "dict_file_num_type")

for file in dict_file_num_type:
    dict_num_type[dict_file_num_type[file]]+=1
    if dict_file_num_type[file]==9:
        print("9 types of code file: ",file)
print(dict_num_type)

for i in range(1,len(res_csv_list_num)+1):
    res_csv_list_num[i-1].append(dict_num_type[i])

dict_num_type={i+1:0 for i in range(9)}
dict_met_num_type = util.load_pkl(util.data_root+"boxplot/", "dict_me_num_type")

for file in dict_met_num_type:
    dict_num_type[dict_met_num_type[file]]+=1
    if dict_met_num_type[file]==9:
        print("9 types of methods: ",file)

for i in range(1,len(res_csv_list_num)+1):
    res_csv_list_num[i-1].append(dict_num_type[i])
print(dict_num_type)
# util.save_csv(util.data_root + "boxplot/"+"dict_repo_file_me_type_num.csv",
#                   res_csv_list_num)

'''
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams["figure.figsize"] = [3, 3.5]
plt.rcParams["figure.autolayout"] = True
#https://blog.csdn.net/weixin_43584807/article/details/101268400
plt.rcParams["axes.spines.right"] = False
plt.rcParams["axes.spines.top"] = False

all_diff_ratio_list=[list(dict_repo_num_type.values()),list(dict_file_num_type.values()),list(dict_met_num_type.values())]

x_position_fmt=["repo","file","met"]
x_position=[0.1+i*1 for i in range(3)]

# plt.xticks([1], [x_position_fmt[0]])
plt.boxplot(all_diff_ratio_list,positions=x_position,widths=0.2)
plt.xticks([i for i in x_position] ,x_position_fmt )
plt.ylim(0,9)
# plt.xticks([1], ["Set Compre"])
# plt.text(0.7, np.median(diff_ratio_list), str(np.round(np.median(diff_ratio_list),2)))
plt.ylabel("number of type of python code")
plt.show()
'''
#
'''
 for choice in choice_list:
                            if choice[2] is None:
                                continue
                            if choice[2] in true_values:
                                logmessage("do_sms: " + choice[2] + " is in true_values")
                                the_string = 'if ' + choice[2] + ' not in ' + the_saveas + '.elements:\n    ' + the_saveas + '.append(' + choice[2] + ')'
                            else:
                                the_string = 'if ' + choice[2] + ' in ' + the_saveas + '.elements:\n    ' + the_saveas + '.remove(' + choice[2] + ')'
'''
base_file_html="https://github.com/jhpyle/docassemble/tree/master/docassemble_webapp/docassemble/webapp/server.py"#"https://github.com/PaddlePaddle/Paddle/tree/master/python/paddle/fluid/framework.py"#"https://github.com/jhpyle/docassemble/tree/master/docassemble_base/docassemble/base/parse.py"
for complicated_code_dir_pkl in code_list[:]:
    print(">>>>>complicated_code_dir_pkl: ",complicated_code_dir_pkl)
    save_complicated_code_dir_pkl=util.data_root +complicated_code_dir_pkl
    for file_name in os.listdir(save_complicated_code_dir_pkl):
        all_count_repo += 1
        repo_name = file_name[:-4]
        if repo_name!="docassemble":#"Paddle":
            continue
        complicate_code = util.load_pkl(save_complicated_code_dir_pkl, repo_name)


        repo_exist = 0

        for file_html in complicate_code:
            if file_html==base_file_html:
                for cl in complicate_code[file_html]:
                    for me in complicate_code[file_html][cl]:

                        if complicate_code[file_html][cl][me]:


                            print("file_html,cl,me: ",file_html,cl,me,complicate_code[file_html][cl][me])
                            #break


