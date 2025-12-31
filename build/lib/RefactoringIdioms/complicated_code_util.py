import time

import sys, ast, os, copy
import tokenize
import sys,shutil
import util
def get_code_count(complicate_code):
    all_me_count = 0
    all_file_count = len(list(complicate_code.keys()))
    code_count = 0
    me_count = 0
    NULL_code_count = 0
    file_count = 0
    cl_count = 0
    for file_html in complicate_code:

        if complicate_code[file_html]:
            file_exist = 0
            # cl_count +=len(list(complicate_code[file_html].keys()))
            for cl in complicate_code[file_html]:
                if complicate_code[file_html][cl]:
                    all_me_count += len(complicate_code[file_html][cl].keys())
                    for me in complicate_code[file_html][cl]:
                        if complicate_code[file_html][cl][me]:
                            me_count += 1
                            file_exist = 1
                            code_count += len(complicate_code[file_html][cl][me])

            file_count += file_exist

    return file_count, me_count, code_count, all_file_count, all_me_count


def get_code_count_contain_test(complicate_code):
    all_me_count = 0
    all_file_count = len(list(complicate_code.keys()))
    code_count,me_count,file_count = 0,0,0


    file_no_test_count, me_no_test_count, code_no_test_count=0,0,0

    for file_html in complicate_code:
        no_test_flag=0
        map_file_name = file_html.split("/")[-1][:-3]
        # filter out test files
        if not (map_file_name.startswith("test_") or map_file_name.endswith("_test")):
            no_test_flag=1
        # file_no_test_count+=no_test_flag

        if complicate_code[file_html]:
            test_file_exist=0
            file_exist = 0
            # cl_count +=len(list(complicate_code[file_html].keys()))
            for cl in complicate_code[file_html]:
                if complicate_code[file_html][cl]:
                    all_me_count += len(complicate_code[file_html][cl].keys())
                    for me in complicate_code[file_html][cl]:
                        if complicate_code[file_html][cl][me]:
                            if no_test_flag:
                                test_file_exist=1
                                me_no_test_count+=1
                                code_no_test_count += len(complicate_code[file_html][cl][me])

                            me_count += 1
                            file_exist = 1
                            code_count += len(complicate_code[file_html][cl][me])

            file_count += file_exist
            file_no_test_count+=test_file_exist

    return file_count, me_count, code_count, all_file_count, all_me_count, file_no_test_count, me_no_test_count, code_no_test_count
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
def get_code_info(complicate_code,repo_name):
    repo_list=set([])
    file_list = set([])
    me_list=set([])
    code_count=0
    for file_html in complicate_code:

        if complicate_code[file_html]:

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
def get_code_info_contain_test(complicate_code,repo_name):
    code_no_test_count=0
    repo_name_list,file_no_test_list, me_no_test_list=set([]),set([]),set([])
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
def get_code_info_with_test_case(dict_comp_file, repo_name):
    repo_name_list, file_no_test_list, me_no_test_list, code_no_test = set([]), set([]), set([]), 0

    # dict_comp_file = util.load_pkl(save_me_test_me_dir, repo_name)
    for file_html in dict_comp_file:
            file_no_test_list.add(file_html)
            for full_me in dict_comp_file[file_html]:
                me_no_test_list.add(full_me)
                code_no_test += dict_comp_file[file_html][full_me]["complica_num"]
    if   code_no_test:
        repo_name_list.add(repo_name)
    return repo_name_list, file_no_test_list, me_no_test_list, code_no_test

def get_code_info_with_success_test_case(dict_test_acc, repo_name):
        repo_name_list, file_no_test_list, me_no_test_list, code_count = set([]), set(dict_test_acc['file_list']), set(
            dict_test_acc['me_list']), dict_test_acc['total_count']
        if code_count:
            repo_name_list.add(repo_name)
        return repo_name_list, file_no_test_list, me_no_test_list, code_count
def get_comp_code_can_test_me(repo_name,save_test_file_res_dir,save_me_test_me_dir):
    dict_complica_me_list = dict()
    full_test_me_list = []
    dict_test_html_each_me_res = util.load_pkl(save_test_file_res_dir, repo_name)
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
def get_code_info_with_can_run_test_case(repo_name,save_test_file_res_dir,save_me_test_me_dir,complicated_code_dir_pkl):
    repo_name_list, file_no_test_list, me_no_test_list, code_count = set([]), set([]), set([]),0

    me_count=0
    file_count=0
    complic_code_count=0
    repo_fla = 0
    # if repo_name != "cloud-custodian":#"spiderfoot":
    #     continue
    # print("come to the repo: ", repo_name)
    dict_complica_me_list = get_comp_code_can_test_me(repo_name,save_test_file_res_dir,save_me_test_me_dir)
    # print("dict_complica_me_list: ", dict_complica_me_list)
    complicate_code = util.load_pkl(complicated_code_dir_pkl, repo_name)
    for file_html in complicate_code:
        flag_file = 0
        if file_html in dict_complica_me_list:

            # if file_html!="https://github.com/pymc-devs/pymc/tree/master/pymc/sampling.py":#"https://github.com/smicallef/spiderfoot/tree/master//sflib.py":#"https://github.com/smicallef/spiderfoot/tree/master//sfwebui.py":#
            #     continue

            # print("come the file_html: ", file_html)
            for cl in complicate_code[file_html]:

                for me in complicate_code[file_html][cl]:
                    me_name = me.split("$")[0]
                    if me_name == "if_main_my":  # it is impossible for the main code1 have test cases
                        continue
                    total_name = get_total_name(file_html, cl, me_name)
                    # print("come total_name: ", cl,me_name,total_name)
                    if total_name in dict_complica_me_list[file_html]:
                        test_me_inf_list = dict_complica_me_list[file_html][total_name]
                        if complicate_code[file_html][cl][me] and test_me_inf_list:
                            repo_name_list.add(repo_name)
                            file_no_test_list.add(file_html)
                            me_no_test_list.add(total_name)
                            flag_file = 1
                            repo_fla = 1
                            me_count+= 1
                            complic_code_count += len(complicate_code[file_html][cl][me])

        file_count += flag_file

    # return repo_fla,file_count,me_count,complic_code_count
    return repo_name_list,file_no_test_list,me_no_test_list,complic_code_count





