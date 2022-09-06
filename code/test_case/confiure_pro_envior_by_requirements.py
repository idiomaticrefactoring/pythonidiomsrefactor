import sys, ast, os, copy
import tokenize
import sys,shutil
pro_root="/".join(os.path.abspath(__file__).split("/")[:-3])+"/"
sys.path.append(pro_root+"code/")
sys.path.append("..")
sys.path.append("../../")
import time
import util, github_util
import subprocess
from pathos.multiprocessing import ProcessingPool as newPool
from subprocess import Popen, PIPE, STDOUT


def findfile(start, name):
    for file in os.listdir(start):
        # if "requirements" in file and ".txt" in file:
        if name in file:
            full_path = os.path.join(start, "", name)
            return (os.path.normpath(os.path.abspath(full_path)))
    return None
    # for relpath, dirs, files in os.walk(start):
    #     # print(relpath,dirs)
    #     if "venv_test" in relpath:
    #         continue
    #     if name in files:
    #         full_path = os.path.join(start, relpath, name)
    #         return (os.path.normpath(os.path.abspath(full_path)))
    # return None


def findreq(start, name=""):
    all_require = []
    for file in os.listdir(start):
        if file=="requirements_my_gen.txt":
            continue
        if "requirements" in file and ".txt" in file:
            full_path = os.path.join(start, "", file)
            all_require.append(os.path.normpath(os.path.abspath(full_path)))
    return all_require


def create_virtual_envi(pro_path, v_name, v="9"):
    return "".join(
        ["cd ", pro_path, " ; python3.", v, " -m venv ", v_name, v, " ; . ./", v_name, v, "/bin/activate;"])
    # return "".join(["cd ", pro_path, "&& python2 -m pip install virtualenv && python2 -m virtualenv venv_test && . ./venv_test/bin/activate"])


def export_python_path(pro_path, relative_test_file_path):
    dir_up = os.path.dirname(pro_path + relative_test_file_path)
    # print("first dir: ",dir_up)
    init_module = ["export PYTHONPATH=" + dir_up]
    all_own_modules = []
    while dir_up != pro_path[:-1]:
        dir_upup = os.path.dirname(dir_up)
        all_own_modules.append(dir_upup)
        # print(dir_up, dir_upup)
        dir_up = dir_upup
    return ":".join(init_module + all_own_modules + [";"])


def pip_install(pro_path,v):
    # cmd_pip_pack = ""
    split_install = "*************************install*************************"
    # require_full_path = findfile(pro_path, "setup.py")
    # cmd_pip_pack = ["echo '", split_install, "' ;","pip3 install pytest; pipreqs ./ --savepath requirements_pipreqs_gen.txt;"]

    cmd_pip_pack = ["echo '", split_install, "' ;","sudo apt-get install python3.",v,"-dev;pip3 install pytest pytest-mock requests yarg pytest-cov; python3 "+pro_root+"code/test_case/pipreqs.py; "]
    #'''
    all_requirements=findreq(pro_path)
    for req in all_requirements:
        if os.path.exists(req):
            # print("yes>>>>>>>>")
            # cmd_pip_pack += ["echo '>>>>>>>>>>>>>>>>>>>>>>>install packages by",req,"';" ]
            cmd_pip_pack += ["pip3 install -r ", req, ";"]
            # with open(req, "r") as file:
            #     pack_list=file.read().split("\n")
            #     for pack in pack_list:
            #         if not pack or not pack.strip()[0].isalpha():
            #             continue
            #         if "#" in pack:
            #             pack=pack[:pack.find("#")]
            #         if "python_version" in pack:
            #             print(">>>>>>>>>>>>>need to check the installed package: ",pro_path,pack)
            #         pack=pack.replace("\\","")
            #         cmd_pip_pack+=["pip3 install ",pack,";"]
            #         print("*********pip3 install ", pack, ";")
    #'''
    if os.path.exists(pro_path+"requirements_my_gen.txt"):
        cmd_pip_pack+=["echo '>>>>>>>>>>>>>>>>>>>>>>>install packages by requirements_my_gen.txt';", ]
        with open(pro_path+"requirements_my_gen.txt", "r") as file:
            pack_list=file.read().split("\n")
            for pack in pack_list:
                if not pack:
                    continue
                cmd_pip_pack+=["pip3 install ",pack,";"]
                print("*********pip3 install ", pack, ";")


    # pip3 install -r requirements_my_gen.txt;

    # if require_full_path:#1!=1:#
    #     # cmd_pip_pack = "".join(["python2 ", require_full_path, " install "])
    #     cmd_pip_pack += ["python3.",v, " ",require_full_path, " install "," ;"]

    # require_txt_full_path = findreq(pro_path)
    # if require_txt_full_path:
    #         for require in require_txt_full_path:
    #             cmd_pip_pack += ["pip3.", v, " install -r ", require, " ;"]

    cmd_pip_pack = "".join(cmd_pip_pack + ["echo '", split_install, "';"])
    # require_full_path = findfile(pro_path, "requirements.txt")
    # if require_full_path:
    #     cmd_pip_pack = "".join(["echo '",split_install,"' ; pip3.",v," install -r ", require_full_path," ; echo '",split_install,"'"])
    # if require_full_path or require_txt_full_path:
    #     return cmd_pip_pack
    return cmd_pip_pack


def make_pytest_test(pro_path, relative_test_file_path, file_name,v, fun_list=[]):
    split_test_str = "*************************test*************************"
    cmd_test = ["echo '", split_test_str, "' ; "]
    whether_same = relative_test_file_path.split("/")
    if 1:  # len(set(whether_same))==len(whether_same):#可能有同名的module名https://github.com/nodejs/node-gyp/tree/master/gyp/pylib/gyp/input_test.py

        # file_name = ".".join(relative_test_file_path.split("/")) + file_name[:-3]
        # file_name = "/".join(relative_test_file_path.split("/")) + file_name
        file_name = relative_test_file_path + file_name
        # print("file_name: ", file_name)
        for ind, e in enumerate(fun_list):
            # print("fun: ", e,relative_test_file_path.split("/"))
            fun_list[ind] = file_name + "::" + e
            # print("fun_list[ind]: ",fun_list[ind])
        relative_test_file_path = ""

    cmd_test += ["cd ", pro_path + relative_test_file_path,
                 " ;"]  # echo '", split_test_str, "' ; "]
    if not fun_list:
        cmd_test += ["python3.", v, " -m pytest -v ", file_name, " ;"]
        pass
    else:

        # cmd_test="".join(["cd ", pro_path+relative_test_file_path," && ","python2 -m unittest ",file_name])
        cmd_test += ["python3.", v, " -m pytest -v ", " ".join(fun_list), " ;"]
        # for fun in fun_list:
        #     cmd_test += ["python3.", v, " -m unittest -v ", file_name[:-3] + "." + fun, " ;"]
        # cmd_test = "".join(cmd_test + ["echo '", split_test_str, "'"])
    cmd_test = "".join(cmd_test + [" echo '", split_test_str, "';"])
    return cmd_test


def rerun_pytest(std_out_res):
    test_error = std_out_res.split("*************************test*************************")[1]
    import re
    patter = "No module named \'(.*)\'"
    module_list = re.findall(patter, std_out_res)

    if module_list:
        re_install_cmd = []
        for modu in module_list:
            re_install_cmd += ["pip3 install ", modu, ";"]

        # print(re_install_cmd)
        return re_install_cmd
    return None
def configure_pro(pro_path,relative_test_file_path,ven_name,v = "7"):

    ven_dir="".join([pro_path, ven_name, v])
    if not os.path.exists(ven_dir):

        cmd_virtu = create_virtual_envi(pro_path,
                                        ven_name,v)  # "".join(["cd ", pro_path," && python3.9 -m venv venv_test && . ./venv_test/bin/activate"])
        cmd_pip_pack = pip_install(pro_path,v)
        cmd_export_python = export_python_path(pro_path,
                                               relative_test_file_path)  # ":".join(init_module+all_own_modules)

    else:
        def activate_virtual_envi(pro_path,ven_name,v):
            return "".join(
                ["cd ", pro_path, " ; . ./",ven_name, v,
                 "/bin/activate;"])

        cmd_virtu =activate_virtual_envi(pro_path,ven_name,v)
        cmd_pip_pack =""
        # cmd_pip_pack=pip_install(pro_path,v)
        # cmd_export_python=""
        cmd_export_python = export_python_path(pro_path,
                                               relative_test_file_path)

    return cmd_virtu,cmd_pip_pack,cmd_export_python


def run_test_file(test_html, pro_path,ven_name= "venv_test_require_",v='7',fun_list=[]):
    output = ""
    # "cloud-custodian/"#"django/"#node-gyp#bert#sentence-transformers
    relative_test_file = "/".join(test_html.replace("//", "/").split("/")[6:])

    relative_test_file_path = "/".join(relative_test_file.split("/")[:-1]) + "/" if len(
        relative_test_file.split("/")) > 1 else ""
    # print("relative_test_file_path: ",relative_test_file_path)

    file_name = relative_test_file.split("/")[-1]
    # '''
    cmd_virtu,cmd_pip_pack,cmd_export_python=configure_pro(pro_path, relative_test_file_path, ven_name,v)



    cmd_test = make_pytest_test(pro_path, relative_test_file_path, file_name,v, fun_list)
    # cmd_test +=["python3.7 - m scripts.run_backend_tests --test_target = scripts.linters.codeowner_linter_test.CodeownerLinterTests.test_missing_important_codeowner_path_from_list;"]
    total_cmd = "".join([cmd_virtu, cmd_export_python, cmd_pip_pack, cmd_test, "deactivate;"])

    result = subprocess.run(total_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    std_out_res = result.stdout.decode("utf-8")
    # print("std_out_res: \n", std_out_res)
    std_error = result.stderr.decode("utf-8") if result.stderr else ""
    std_args = result.args
    # print("\n".join(result.stdout.decode("utf-8").split("*************************test*************************")))

    # print("std_error: \n", std_error)
    # print("std_args: \n", std_args)
    output = "\n".join([std_out_res, std_error, std_args])
    return output


def get_test_result(run_test_result):
    dict_one_file_res = dict()
    full_test_me_name_list=[]
    flag = 0
    test_res = run_test_result.split("*************************test*************************")[1]
    # print("test_res: ",test_res)
    test_session_str = "============================= test session starts =============================="
    test_session_str_index = test_res.find(test_session_str)
    if test_session_str_index:
        test_session_str_index += len(test_session_str)
    real_test_resul = test_res[test_session_str_index:].split("====================================")[0]
    # print("real_test_resul: ",real_test_resul)
    for line in real_test_resul.split("\n"):
        if "::" in line:
            eac_me_test = line.split("::")
            # total_name=".".join(eac_me_test[0].split("/")[:-1])
            path_list = eac_me_test[0].split("/")
            path_list[-1] = path_list[-1][:-3]

            rela_path = ".".join(path_list)

            if len(eac_me_test) == 3:
                cl_name = eac_me_test[1]
                me_name = eac_me_test[-1].split(" ")[0]
                total_name = ".".join([rela_path, cl_name, me_name])
            else:
                cl_name = ""
                me_name = eac_me_test[-1].split(" ")[0]
                total_name = ".".join([rela_path, me_name])
            if "PASSED" in line:
                flag = 1
                dict_one_file_res[total_name] = 1
                full_test_me_name_list.append(total_name)
                pass
            # else:
            #     dict_one_file_res[total_name] = 0
    #return dict_one_file_res, flag
    return full_test_me_name_list, flag
# 存储这个repo中可以运行成功的test file 信息

def save_repo_test_result(repo_name):
    if os.path.exists(save_me_test_me_dir + repo_name + ".pkl"):
        # return None
        pro_path = util.data_root + "python_star_2000repo/"
        pro_path += repo_name + "/"
        v = "7"
        ven_name = "venv_test_require_"
        ven_dir = "".join([pro_path, ven_name, v])
        dict_test_html_each_me_res = dict()
        dict_all_test_html = dict()
        dict_me_test_me_pair = util.load_pkl(save_me_test_me_dir, repo_name)

        for file_html in dict_me_test_me_pair:
            # if file_html!="https://github.com/pymc-devs/pymc/tree/master/pymc/sampling.py":#"https://github.com/cloud-custodian/cloud-custodian/tree/master/c7n/schema.py":
            #     continue
            dict_fullme_test_me_pair = dict_me_test_me_pair[file_html]
            for fullme in dict_fullme_test_me_pair:
                for test_html, cl, me in dict_fullme_test_me_pair[fullme]["test_pair"]:
                    if test_html in dict_all_test_html:
                        dict_all_test_html[test_html].add((cl, me))
                    else:
                        dict_all_test_html[test_html] = set([(cl, me)])
        # if dict_all_test_html:
        #     util.save_pkl(save_test_html_me_dir, repo_name, dict_all_test_html)

        for test_html in dict_all_test_html:
            dict_test_html_each_me_res[test_html] = dict()
            fun_list = []
            for cl, me in dict_all_test_html[test_html]:
                fun_list.append("::".join([cl, me]) if cl else me)
                # test_info.append([test_html, cl, me])
            run_test_result = run_test_file(test_html, pro_path, ven_name, v,fun_list)
            # print(run_test_result)

            dict_me_re, flag_pass = get_test_result(run_test_result)
            # print(flag_pass,dict_me_re)
            if flag_pass:
                dict_test_html_each_me_res[test_html]['flag_pass'] = flag_pass
                dict_test_html_each_me_res[test_html]['test_methods'] = dict_me_re
        if dict_test_html_each_me_res:
            util.save_pkl(save_test_file_res_dir, repo_name, dict_test_html_each_me_res)
            print("save succcessfully! ",save_test_file_res_dir, repo_name)
# 统计某一种化繁为简的代码中，有多少的repo, files, methods, complicated code fragments 中存在可以运行的测试用例
def get_test_success_count():
    file_count=0
    repo_count=0
    me_count=0
    repo_count_comp=0
    me_count_comp=0
    file_count_comp = 0
    compli_code_count=0
    for file in os.listdir(save_test_file_res_dir):
        full_test_me_list = []
        repo_name=file[:-4]
        flag_repo=0
        dict_test_html_each_me_res = util.load_pkl(save_test_file_res_dir, repo_name)
        dict_intersect_test_methods=util.load_pkl(save_me_test_me_dir, repo_name )

        for test_html in dict_test_html_each_me_res:
            if dict_test_html_each_me_res[test_html]:
                # print(dict_test_html_each_me_res[test_html])
                flag_test_html=dict_test_html_each_me_res[test_html]['flag_pass']
                file_count += flag_test_html
                if flag_test_html:
                    flag_repo=1
                me_count+=len(dict_test_html_each_me_res[test_html]['test_methods'])
                full_test_me_list.extend(list(dict_test_html_each_me_res[test_html]['test_methods']))
                for full_test_me in dict_test_html_each_me_res[test_html]['test_methods']:
                    # full_test_me
                    pass
        repo_flag=0
        for file_html in dict_intersect_test_methods:
            file_flag=0
            for complic_me in dict_intersect_test_methods[file_html]:
                # print(complic_me,dict_intersect_test_methods[file_html][complic_me])
                complica_code_fragments_num=dict_intersect_test_methods[file_html][complic_me]['complica_num']
                test_me_of_compl_code=[]
                for test_case_html,cl,me in dict_intersect_test_methods[file_html][complic_me]["test_pair"]:
                    real_file_html = test_case_html.replace("//", "/")
                    path_list=real_file_html.split("/")[6:]
                    path_list[-1] = path_list[-1][:-3]
                    rela_path = ".".join(path_list)

                    if cl:
                        total_test_me_name = ".".join([rela_path,cl, me])
                    else:
                        total_test_me_name = ".".join([rela_path, me])
                    test_me_of_compl_code.append(total_test_me_name)
                if set(test_me_of_compl_code)&set(full_test_me_list):
                    compli_code_count+=complica_code_fragments_num
                    me_count_comp+=1
                    file_flag=1
                    repo_flag=1
            file_count_comp+=file_flag
        repo_count_comp+=repo_flag



        # if flag_repo:
        #     print("full_test_me: ",len(full_test_me_list),len(set(full_test_me_list)))

        repo_count+=flag_repo
    print("file_count,repo_count,me_count,repo_count_comp,file_count_comp,me_count_comp,compli_code_count: ",file_count,repo_count,me_count,repo_count_comp,file_count_comp,me_count_comp,compli_code_count)

    return file_count,repo_count,me_count



if __name__ == '__main__':
    dict_repo_file_python = util.load_json(util.data_root, "python3_1000repos_files_info")
    save_me_test_me_dir0 = util.data_root + "methods_test_method_pair/for_else/"
    save_me_test_me_dir1= util.data_root + "methods_test_method_pair/var_unpack_for_target_complicated/"
    save_me_test_me_dir2= util.data_root + "methods_test_method_pair/var_unpack_call_star_complicated/"
    save_me_test_me_dir3= util.data_root + "methods_test_method_pair/for_compre_set/"
    save_me_test_me_dir4= util.data_root + "methods_test_method_pair/for_compre_list/"
    save_me_test_me_dir5= util.data_root + "methods_test_method_pair/for_compre_dict/"
    save_me_test_me_dir6= util.data_root + "methods_test_method_pair/truth_value_test_complicated/"
    save_me_test_me_dir7= util.data_root + "methods_test_method_pair/multip_assign_complicated/"
    #
    save_me_test_me_dir8 = util.data_root + "methods_test_method_pair/chain_comparison/"

    save_test_file_res_dir=util.data_root + "save_test_file_res_dir/for_else/"
    save_test_file_res_dir=util.data_root + "save_test_file_res_dir/var_unpack_for_target_complicated/"
    save_test_file_res_dir=util.data_root + "save_test_file_res_dir/var_unpack_call_star_complicated/"
    save_test_file_res_dir=util.data_root + "save_test_file_res_dir/for_compre_set/"
    #save_test_file_res_dir=util.data_root + "save_test_file_res_dir/for_compre_list/"
    save_test_file_res_dir=util.data_root + "save_test_file_res_dir/for_compre_dict/"
    #save_test_file_res_dir=util.data_root + "save_test_file_res_dir/truth_value_test_complicated/"
    #save_test_file_res_dir=util.data_root + "save_test_file_res_dir/multip_assign_complicated/"
    save_me_test_me_dir_list=[save_me_test_me_dir0,save_me_test_me_dir1,save_me_test_me_dir2,save_me_test_me_dir3,
                              save_me_test_me_dir4,save_me_test_me_dir5,save_me_test_me_dir6,save_me_test_me_dir7,
                              save_me_test_me_dir8]
    #save_test_file_res_dir=util.data_root + "save_test_file_res_dir/chain_comparison/"
    repo_list=[]
    for save_me_test_me_dir in save_me_test_me_dir_list:
        repo_list.extend(os.listdir(save_me_test_me_dir))
    repo_list = list(set(repo_list))
    print("we need to configrue ",len(repo_list)," repos")
    ven_name = "venv_test_require_"
    v = "7"
    def configure_all_repo(repo):
        pro_path = util.data_root + "python_star_2000repo/"
        pro_path += repo + "/"
        ven_name = "venv_test_require_"
        v = "7"
        ven_dir = "".join([pro_path, ven_name, v])
        if not os.path.exists(ven_dir):

            cmd_virtu = create_virtual_envi(pro_path,
                                            ven_name,
                                            v)  # "".join(["cd ", pro_path," && python3.9 -m venv venv_test && . ./venv_test/bin/activate"])
            cmd_pip_pack = pip_install(pro_path, v)
        total_cmd = "".join([cmd_virtu, cmd_pip_pack, "deactivate;"])

        result = subprocess.run(total_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        std_out_res = result.stdout.decode("utf-8")
        # print("std_out_res: \n", std_out_res)
        std_error = result.stderr.decode("utf-8") if result.stderr else ""
        std_args = result.args
        print("\n".join([">>>>>>>>>>>>>>",repo,std_out_res, std_error, std_args]))



    output=""
    # pool = newPool(nodes=30)
    # pool.map(configure_all_repo, repo_list)  # [:3]sample_repo_url ,token_num_list[:1]
    # pool.close()
    # pool.join()
    # for repo in repo_list:

        # print("\n".join(result.stdout.decode("utf-8").split("*************************test*************************")))
        #
        # print("std_error: \n", std_error)
        # print("std_args: \n", std_args)



    csv_result=[]
    #'''
    repo_list=[]
    for repo_name in dict_repo_file_python:
        # if repo_name!="pymc":
        #     continue
        if os.path.exists(save_me_test_me_dir + repo_name + ".pkl"):
            repo_list.append(repo_name)
            # if len(repo_list)>2:
            #     break
        # v = "7"
        # ven_name = "venv_test_require_"
        # pro_path = util.data_root + "python_star_2000repo/"
        # pro_path += repo_name + "/"
        # ven_dir = "".join([pro_path, ven_name, v])
        # if os.path.exists(ven_dir):
        #
        #     shutil.rmtree(ven_dir)
        #     print("remove the dir ",ven_dir)
    #'''
    # pool = newPool(nodes=30)
    # pool.map(save_repo_test_result, repo_list)  # [:3]sample_repo_url ,token_num_list[:1]
    # pool.close()
    # pool.join()
    #
    # get_test_success_count()
    #'''
    # get_test_success_count()
    #'''
    '''
    for repo_name in dict_repo_file_python:


        if not os.path.exists(save_me_test_me_dir+repo_name+".pkl"):
            continue
        dict_all_test_html = dict()
        # if repo_name!="horovod":#"boto3":#"rasa":#"allennlp":#"horovod":
        #     continue

        v="7"
        ven_name = "venv_test_require_"
        pro_path = util.data_root + "python_star_2000repo/"
        pro_path+=repo_name+"/"
        ven_dir="".join([pro_path, ven_name, v])
        # if os.path.exists(ven_dir) and repo_name!="trax":
        #     continue
        print("come to the repo: ", repo_name)
        # if os.path.exists(pro_path+"77"):
        #     shutil.rmtree(pro_path+"77")
        #     print("remove the dir ", pro_path+"77")

        # if os.path.exists(ven_dir):
        #
        #     shutil.rmtree(ven_dir)
        #     print("remove the dir ",ven_dir)

        dict_me_test_me_pair = util.load_pkl(save_me_test_me_dir, repo_name)
        for file_html in dict_me_test_me_pair:
            dict_fullme_test_me_pair = dict_me_test_me_pair[file_html]
            for fullme in dict_fullme_test_me_pair:
                for test_html, cl, me in dict_fullme_test_me_pair[fullme]["test_pair"]:
                    if test_html in dict_all_test_html:
                        dict_all_test_html[test_html].add((cl, me))
                    else:
                        dict_all_test_html[test_html] = set([(cl, me)])
        # if dict_all_test_html:
        #     util.save_pkl(save_test_html_me_dir, repo_name, dict_all_test_html)
        dict_test_html_each_me_res = dict()
        for test_html in dict_all_test_html:
            dict_test_html_each_me_res[test_html] = dict()
            run_test_result = run_test_file(test_html, pro_path, ven_name, v)
            # print(run_test_result)
            dict_me_re, flag_pass = get_test_result(run_test_result)
            if flag_pass:
                dict_test_html_each_me_res[test_html]['flag_pass'] = flag_pass
                dict_test_html_each_me_res[test_html]['test_methods'] = dict_me_re
        if dict_test_html_each_me_res:
            util.save_pkl(save_test_file_res_dir, repo_name, dict_test_html_each_me_res)

            # print(run_test_result)
        #     dict_me_re,flag_pass=get_test_result(run_test_result)
        #     if flag_pass:
        #         dict_test_html_each_me_res[test_html]['flag_pass']=flag_pass
        #         dict_test_html_each_me_res[test_html]['test_methods']=dict_me_re
        # if dict_test_html_each_me_res:
        #     pass
        #     util.save_pkl(save_test_file_res_dir, repo_name, dict_test_html_each_me_res)

            # csv_result.append([repo_name,test_html,run_test_result])
        # print(dict_test_html_each_me_res)
    '''
    # get_test_success_count()
    # util.save_csv(util.data_root + "test_case_run_result_csv/for_else_require.csv", csv_result,
    #               ["repo_name", "test_html", "run_test_result"])
    #'''
    '''
    pro_path = util.data_root + "python_star_2000repo/"  # "cloud-custodian/"#"django/"#node-gyp#bert#sentence-transformers
    pro_path += "oppia/"  # "ansible/"#"sentry/"#"security_monkey/"#"elastalert/"#"boto3/"#"cloud-custodian/"#"poetry/"#"sentence-transformers/"#"bert/"#"rasa/"#"node-gyp/"#"rtv/"#"django-extensions/"#"ungoogled-chromium/"##"allennlp/"#"django/"#"django-extensions/"#"cd/"#"boto3/"#"security_monkey/"#"oppia/"#"lbry-sdk/"#"node-gyp/"#"cloud-custodian/"#"security_monkey/"
    v = "7"
    # "gyp/pylib/gyp/input_test.py"#"tests/puzzle/test_transaction.py"#"tests/unit/resources/test_model.py"#"security_monkey/tests/core/test_auditor.py"#"scripts/linters/codeowner_linter_test.py"#"tests/unit/wallet/test_wallet.py"#"security_monkey/tests/core/test_auditor.py"#"gyp/pylib/gyp/input_test.py"#"tests/test_policy.py"#"gyp/pylib/gyp/input_test.py"

    relative_test_file = "scripts/linters/codeowner_linter_test.py"  # "test/units/plugins/connection/test_local.py"#"tests/sentry/eventstore/test_base.py"#"security_monkey/tests/core/test_auditor.py"#"tests/alerts_test.py"#"tests/unit/resources/test_model.py"#"tests/test_policy.py"#"tests/puzzle/test_transaction.py"#"tokenization_test.py"#"tests/core/policies/test_unexpected_intent_policy.py"#"gyp/pylib/gyp/input_test.py"#"tests/test_objects.py"#"tests/management/commands/shell_plus_tests/test_shell_plus.py"#"utils/tests/test_domain_substitution.py"#"tests/nn/chu_liu_edmonds_test.py"#"tests/test_objects.py"#"tests/forms_tests/field_tests/test_base.py"#"tests/management/commands/shell_plus_tests/test_shell_plus.py"#"tests/puzzle/test_transaction.py"#"tests/unit/resources/test_model.py"#"security_monkey/tests/core/test_auditor.py"#"scripts/linters/codeowner_linter_test.py"#"tests/unit/wallet/test_wallet.py"#"security_monkey/tests/core/test_auditor.py"#"gyp/pylib/gyp/input_test.py"#"tests/test_policy.py"#"gyp/pylib/gyp/input_test.py"
    relative_test_file_path = "/".join(relative_test_file.split("/")[:-1]) + "/" if len(
        relative_test_file.split("/")) > 1 else ""
    # print("relative_test_file_path: ",relative_test_file_path)
    file_name = relative_test_file.split("/")[-1]
    
    cmd_virtu = create_virtual_envi(pro_path,
                                    v)  # "".join(["cd ", pro_path," && python3.9 -m venv venv_test && . ./venv_test/bin/activate"])
    cmd_pip_pack = pip_install(pro_path, v)

    # relative_test_file_path="gyp/pylib/gyp/"#"tests/"#"tests/forms_tests/field_tests/"#"gyp/pylib/gyp/"#"gyp/pylib/gyp/generator/"
    # file_name="input_test.py"#test_policy.py "tokenization_test.py"#"test_base.py"#"input_test.py"#"msvs_test.py" #test_util.py
    cmd_export_python = export_python_path(pro_path, relative_test_file_path)  # ":".join(init_module+all_own_modules)
    # cmd_pip_pack+= " && pip install tensorflow==1.11.0"
    fun_list = []
    # fun_list=["CodeownerLinterTests.test_missing_important_codeowner_path_from_list"]#类名.方法名
    # fun_list=[file_name[:-3]+".TokenizationTest.test_basic_tokenizer_lower",file_name[:-3]+".TokenizationTest.test_is_punctuation","optimization_test.OptimizationTest.test_adam"]
    # fun_list=" ".join(fun_list)

    cmd_test = make_pytest_test(pro_path, relative_test_file_path, file_name,v, fun_list)
    # cmd_test +=["python3.7 - m scripts.run_backend_tests --test_target = scripts.linters.codeowner_linter_test.CodeownerLinterTests.test_missing_important_codeowner_path_from_list;"]
    total_cmd = "".join([cmd_virtu, cmd_export_python, cmd_pip_pack, cmd_test])


    result = subprocess.run(total_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    std_out_res = result.stdout.decode("utf-8")
    print("std_out_res: \n", std_out_res)
    std_error = result.stderr.decode("utf-8") if result.stderr else ""
    std_args = result.args
    # print("\n".join(result.stdout.decode("utf-8").split("*************************test*************************")))

    print("std_error: \n", std_error)
    print("std_args: \n", std_args)
    '''
    '''
    re_install_cmd = rerun_pytest(
        std_out_res)  # ['pip3 install ', 'setuptools_rust', ' ', 'setuptools_rust', ' ', 'spacy', ' ', ';']#
    while re_install_cmd:

        total_cmd = ["cd ", pro_path, ";", ". ./venv_test_" + v + "/bin/activate;"] + re_install_cmd
        total_cmd.append(make_pytest_test(pro_path, relative_test_file_path, file_name, v,fun_list=[]))

        total_cmd = "".join(total_cmd)
        print(total_cmd)
        result = subprocess.run(total_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        std_out_res = result.stdout.decode("utf-8")
        print("std_out_res: ", std_out_res)
        std_error = result.stderr.decode("utf-8") if result.stderr else ""
        std_args = result.args
        # print("\n".join(result.stdout.decode("utf-8").split("*************************test*************************")))

        print("std_error: \n", std_error)
        print("std_args: \n", std_args)
        re_install_cmd_old = rerun_pytest(std_out_res)
        if re_install_cmd_old == re_install_cmd:
            break
        re_install_cmd = re_install_cmd_old
    '''