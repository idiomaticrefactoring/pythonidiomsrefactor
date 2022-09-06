import sys, ast, os, copy
import tokenize
import sys,shutil
pro_root="/".join(os.path.abspath(__file__).split("/")[:-3])+"/"
sys.path.append(pro_root+"code/")
sys.path.append(pro_root+"code/test_case")
sys.path.append(pro_root+"code/transform_c_s")
sys.path.append("..")
sys.path.append("../../")

import time
import util, github_util
import replace_content_by_ast
import confiure_pro_envior_by_requirements
import subprocess
from pathos.multiprocessing import ProcessingPool as newPool
def get_comp_code_can_test_me(repo_name,save_test_file_res_dir,save_me_test_me_dir):
    dict_complica_me_list = dict()
    full_test_me_list = []
    dict_intersect_test_methods=dict()
    dict_test_html_each_me_res=dict()
    if os.path.exists(save_test_file_res_dir + repo_name + ".pkl"):
        dict_test_html_each_me_res = util.load_pkl(save_test_file_res_dir, repo_name)
    if os.path.exists(save_me_test_me_dir+repo_name+".pkl"):
        dict_intersect_test_methods = util.load_pkl(save_me_test_me_dir, repo_name)

    for test_html in dict_test_html_each_me_res:
        if dict_test_html_each_me_res[test_html]:
            full_test_me_list.extend(dict_test_html_each_me_res[test_html]['test_methods'])

    for file_html in dict_intersect_test_methods:
        dict_complica_me_list[file_html]=dict()
        for complic_me in dict_intersect_test_methods[file_html]:
            dict_complica_me_list[file_html][complic_me] = []
            dict_test_info = dict()
            # print(complic_me, dict_intersect_test_methods[file_html][complic_me])
            complica_code_fragments_num = dict_intersect_test_methods[file_html][complic_me]['complica_num']
            test_me_of_compl_code = []
            for test_case_html, cl, me in dict_intersect_test_methods[file_html][complic_me]["test_pair"]:
                real_file_html = test_case_html.replace("//", "/")
                path_list = real_file_html.split("/")[6:]
                path_list[-1] = path_list[-1][:-3]
                rela_path = ".".join(path_list)

                if cl:
                    total_test_me_name = ".".join([rela_path, cl, me])
                else:
                    total_test_me_name = ".".join([rela_path, me])
                test_me_of_compl_code.append(total_test_me_name)
                dict_test_info[total_test_me_name] = [test_case_html, rela_path, cl, me]
            for e in set(test_me_of_compl_code) & set(full_test_me_list):
                dict_complica_me_list[file_html][complic_me].append(dict_test_info[e])
    return dict_complica_me_list


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
def get_test_acc(save_test_acc_dir):
    me_count = 0
    file_count = 0
    repo_count = 0
    complic_code_count = 0
    total_count = 0
    total_acc_count = 0
    total_count_by_list = 0
    total_acc_count_by_list=0
    me_count_by_list=0
    file_count_by_list=0
    repo_list = []
    for file in os.listdir(save_test_acc_dir):
        repo_name = file[:-4]
        complicate_code = util.load_pkl(save_test_acc_dir, repo_name)

        total_count+=complicate_code['total_count']
        if complicate_code['total_count']:
            print("total_count and complic_code_count: ", complicate_code['total_count'],complicate_code['complic_code_count'])
        total_acc_count+=complicate_code['total_acc_count']
        repo_count+=complicate_code['repo_count']
        file_count+=complicate_code['file_count']

        me_count+=complicate_code['me_count']
        me_count_by_list+=len(complicate_code['me_list'])
        complic_code_count+=complicate_code['complic_code_count']
        if complicate_code['complic_code_count']:
            print("complic_code_count: ",complicate_code['complic_code_count'])
        file_count_by_list+=len(complicate_code['file_list'])
        repo_list.append(repo_name)
    print(sorted(repo_list))
    print("repo_count,file_count,me_count,complic_code_count:",repo_count,file_count,me_count,complic_code_count)
    # print("file_count_by_list,me_count_by_list: ",file_count_by_list,me_count_by_list)
    print("acc: ",total_acc_count,total_count,total_acc_count/total_count)
def get_test_acc_info(save_test_acc_dir):
    me_count = 0
    file_count = 0
    repo_count = 0
    complic_code_count = 0
    total_count = 0
    total_acc_count = 0
    total_count_by_list = 0
    total_acc_count_by_list=0
    me_count_by_list=0
    file_count_by_list=0
    repo_list = []
    dict_repo_me_count=dict()
    for file in os.listdir(save_test_acc_dir):
        repo_name = file[:-4]
        complicate_code = util.load_pkl(save_test_acc_dir, repo_name)

        total_count+=complicate_code['total_count']
        total_acc_count+=complicate_code['total_acc_count']
        repo_count+=complicate_code['repo_count']
        file_count+=complicate_code['file_count']

        me_count+=complicate_code['me_count']
        me_count_by_list+=len(complicate_code['me_list'])
        complic_code_count+=complicate_code['complic_code_count']
        file_count_by_list+=len(complicate_code['file_list'])
        dict_repo_me_count[repo_name]=complicate_code['complic_code_count']
        repo_list.append(repo_name)
    # print(sorted(repo_list))
    return dict_repo_me_count
    print("repo_count,file_count,me_count,complic_code_count:",repo_count,file_count,me_count,complic_code_count)
    # print("file_count_by_list,me_count_by_list: ",file_count_by_list,me_count_by_list)
    print("acc: ",total_acc_count,total_count,total_acc_count/total_count)