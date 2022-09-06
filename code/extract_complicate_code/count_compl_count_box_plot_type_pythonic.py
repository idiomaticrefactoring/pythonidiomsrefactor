import sys,ast,os
pro_root="/".join(os.path.abspath(__file__).split("/")[:-3])+"/"
sys.path.append(pro_root+"code/")

import time,complicated_code_util
import util
start_time = time.time()
code_list=["idiom_code_dir_pkl/dict_comprehension_idiom_code/", "idiom_code_dir_pkl/set_comprehension_idiom_code/",
           "idiom_code_dir_pkl/list_comprehension_idiom_code/","idiom_code_dir_pkl/chained_comparison_idiom_code/",
           "idiom_code_dir_pkl/for_else_idiom_code_fragments/",
           "idiom_code_dir_pkl/multi_assign_idiom_code/",
           "idiom_code_dir_pkl/var_unpack_call_idiom_code_subscript_slice/",
            "idiom_code_dir_pkl/multi_targets_for/", "idiom_code_dir_pkl/truth_value_test_idiom_code_improve/"
]


dict_repo_num_type=dict()
dict_file_num_type=dict()
dict_met_num_type=dict()
'''
for complicated_code_dir_pkl in code_list[:]:
    save_complicated_code_dir_pkl=util.data_root +complicated_code_dir_pkl
    for file_name in os.listdir(save_complicated_code_dir_pkl):
        repo_name=file_name[:-4]
        complicate_code = util.load_pkl(save_complicated_code_dir_pkl, repo_name)
        repo_exist = 0
        for file_html in complicate_code:

            if complicate_code[file_html]:
                file_exist = 0
                # cl_count +=len(list(complicate_code[file_html].keys()))
                for cl in complicate_code[file_html]:
                    if complicate_code[file_html][cl]:

                        for me in complicate_code[file_html][cl]:

                            if complicate_code[file_html][cl][me]:
                                total_me = "".join([file_html, cl, me])
                                repo_exist = 1
                                me_exist = 1
                                file_exist = 1

                                if total_me in dict_met_num_type:
                                    dict_met_num_type[total_me] += 1
                                else:
                                    dict_met_num_type[total_me] = 1
                if file_exist:
                    if file_html in dict_file_num_type:
                        dict_file_num_type[file_html] += 1
                    else:
                        dict_file_num_type[file_html] = 1


        if repo_exist:
            if repo_name in dict_repo_num_type:
                dict_repo_num_type[repo_name] += 1
            else:
                dict_repo_num_type[repo_name] = 1
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
plt.ylabel("number of pythonic idioms")
plt.show()
util.save_pkl(util.data_root+"boxplot/", "dict_repo_num_type_pythonic",dict_repo_num_type)
util.save_pkl(util.data_root+"boxplot/", "dict_file_num_type_pythonic",dict_file_num_type)
util.save_pkl(util.data_root+"boxplot/", "dict_me_num_type_pythonic",dict_met_num_type)
'''
dict_repo_num_type = util.load_pkl(util.data_root+"boxplot/", "dict_repo_num_type_pythonic")
res_csv_list_num=[]
dict_num_type={i+1:0 for i in range(9)}
for repo in dict_repo_num_type:
    dict_num_type[dict_repo_num_type[repo]]+=1
for key,v in dict_num_type.items():
    res_csv_list_num.append([v])
print(dict_num_type)
dict_num_type={i+1:0 for i in range(9)}

dict_file_num_type = util.load_pkl(util.data_root+"boxplot/", "dict_file_num_type_pythonic")

for file in dict_file_num_type:
    dict_num_type[dict_file_num_type[file]]+=1
    if dict_file_num_type[file]==9 :

        print("9 types of code file: ",file)
print(dict_num_type)

# dict_file_num_type_non_pythonic = util.load_pkl(util.data_root+"boxplot/", "dict_file_num_type")
#
# for file in dict_file_num_type_non_pythonic:
#     dict_num_type[dict_file_num_type_non_pythonic[file]]+=1

# print(dict_num_type)

for i in range(1,len(res_csv_list_num)+1):
    res_csv_list_num[i-1].append(dict_num_type[i])

dict_num_type={i+1:0 for i in range(9)}
dict_met_num_type = util.load_pkl(util.data_root+"boxplot/", "dict_me_num_type_pythonic")

for file in dict_met_num_type:
    dict_num_type[dict_met_num_type[file]]+=1

for i in range(1,len(res_csv_list_num)+1):
    res_csv_list_num[i-1].append(dict_num_type[i])
print(dict_num_type)
base_file_html="https://github.com/spesmilo/electrum/tree/master/electrum/wallet.py"#"https://github.com/mne-tools/mne-python/tree/master/mne/utils/numerics.py"#"https://github.com/python/mypy/tree/master/mypy/semanal.py"#"https://github.com/ponyorm/pony/tree/master/pony/orm/sqltranslation.py"#"https://github.com/yt-dlp/yt-dlp/tree/master/yt_dlp/YoutubeDL.py"#"https://github.com/platomav/MEAnalyzer/tree/master//MEA.py"#"https://github.com/holoviz/holoviews/tree/master/holoviews/core/util.py"#"https://github.com/sympy/sympy/tree/master/sympy/solvers/solvers.py"#"https://github.com/sympy/sympy/tree/master/sympy/combinatorics/perm_groups.py"#"https://github.com/sympy/sympy/tree/master/sympy/core/function.py"#"https://github.com/sympy/sympy/tree/master/sympy/tensor/tensor.py"#165#"https://github.com/ansible/galaxy/tree/master/lib/galaxy/workflow/modules.py"#"https://github.com/derrod/legendary/tree/master/legendary/core.py"#"https://github.com/nltk/nltk/tree/master/nltk/corpus/reader/framenet.py"#"https://github.com/jhpyle/docassemble/tree/master/docassemble_webapp/docassemble/webapp/server.py"#"https://github.com/PaddlePaddle/Paddle/tree/master/python/paddle/fluid/framework.py"#"https://github.com/jhpyle/docassemble/tree/master/docassemble_base/docassemble/base/parse.py"
for complicated_code_dir_pkl in code_list[:]:
    print(">>>>>complicated_code_dir_pkl: ",complicated_code_dir_pkl)
    save_complicated_code_dir_pkl=util.data_root +complicated_code_dir_pkl
    for file_name in os.listdir(save_complicated_code_dir_pkl):

        repo_name = file_name[:-4]
        if repo_name!="electrum":#"mne-python":#"mypy":#"pony":#"yt-dlp":#"MEAnalyzer":#"holoviews":#"sympy":#"galaxy":#"legendary":#"nltk":#"Paddle":
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



# util.save_csv(util.data_root + "boxplot/"+"dict_repo_file_me_type_num_pythonic_idiom.csv",
#                   res_csv_list_num)
