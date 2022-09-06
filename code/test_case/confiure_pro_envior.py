import sys, ast, os, copy
import tokenize
import sys,shutil

sys.path.append("..")
sys.path.append("../../")
pro_root="/".join(os.path.abspath(__file__).split("/")[:-3])+"/"
sys.path.append(pro_root+"code/")

import time
import util, github_util
import subprocess
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
        if "requirements" in file and ".txt" in file:
            full_path = os.path.join(start, "", file)
            all_require.append(os.path.normpath(os.path.abspath(full_path)))
    return all_require


def create_virtual_envi(pro_path, v="9"):
    return "".join(
        ["cd ", pro_path, " ; python3.", v, " -m venv venv_test_", v, " ; . ./", "venv_test_", v, "/bin/activate;"])
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


def pip_install(pro_path, v="9"):
    # cmd_pip_pack = ""
    split_install = "*************************install*************************"
    # require_full_path = findfile(pro_path, "setup.py")
    # cmd_pip_pack = ["echo '", split_install, "' ;","pip3 install pytest; pipreqs ./ --savepath requirements_pipreqs_gen.txt;"]
    cmd_pip_pack = ["echo '", split_install, "' ;",
                    " pip3 install -e .; pip3 install pytest pytest-mock pytest-cov;"]
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


def make_pytest_test(pro_path, relative_test_file_path, file_name, fun_list=[]):
    split_test_str = "*************************test*************************"
    cmd_test = ["echo '", split_test_str, "' ; "]
    whether_same = relative_test_file_path.split("/")
    if 1:  # len(set(whether_same))==len(whether_same):

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
def configure_pro(pro_path,relative_test_file_path,v = "7"):
    ven_dir="".join([pro_path, "venv_test_", v])
    if not os.path.exists(ven_dir):

        cmd_virtu = create_virtual_envi(pro_path,
                                        v)  # "".join(["cd ", pro_path," && python3.9 -m venv venv_test && . ./venv_test/bin/activate"])
        cmd_pip_pack = pip_install(pro_path, v)
        cmd_export_python = export_python_path(pro_path,
                                               relative_test_file_path)  # ":".join(init_module+all_own_modules)

    else:
        def activate_virtual_envi(pro_path,v):
            return "".join(
                ["cd ", pro_path, " ; . ./", "venv_test_", v,
                 "/bin/activate;"])

        cmd_virtu =activate_virtual_envi(pro_path,v)
        cmd_pip_pack=""
        cmd_export_python = export_python_path(pro_path,
                                               relative_test_file_path)

    return cmd_virtu,cmd_pip_pack,cmd_export_python


def run_test_file(test_html, pro_path,v='7'):
    output = ""
    # "cloud-custodian/"#"django/"#node-gyp#bert#sentence-transformers
    relative_test_file = "/".join(test_html.replace("//", "/").split("/")[6:])

    relative_test_file_path = "/".join(relative_test_file.split("/")[:-1]) + "/" if len(
        relative_test_file.split("/")) > 1 else ""
    # print("relative_test_file_path: ",relative_test_file_path)

    file_name = relative_test_file.split("/")[-1]
    # '''
    cmd_virtu,cmd_pip_pack,cmd_export_python=configure_pro(pro_path, relative_test_file_path, v)

    fun_list = []

    cmd_test = make_pytest_test(pro_path, relative_test_file_path, file_name, fun_list)
    # cmd_test +=["python3.7 - m scripts.run_backend_tests --test_target = scripts.linters.codeowner_linter_test.CodeownerLinterTests.test_missing_important_codeowner_path_from_list;"]
    total_cmd = "".join([cmd_virtu, cmd_export_python, cmd_pip_pack, cmd_test, "deactivate;"])

    result = subprocess.run(total_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    std_out_res = result.stdout.decode("utf-8")
    print("std_out_res: \n", std_out_res)
    std_error = result.stderr.decode("utf-8") if result.stderr else ""
    std_args = result.args
    # print("\n".join(result.stdout.decode("utf-8").split("*************************test*************************")))

    print("std_error: \n", std_error)
    print("std_args: \n", std_args)
    output = "\n".join([std_out_res, std_error, std_args])
    return output

if __name__ == '__main__':
    dict_repo_file_python = util.load_json(util.data_root, "python3_1000repos_files_info")
    save_me_test_me_dir = util.data_root + "methods_test_method_pair/for_else/"
    csv_result=[]

    for repo_name in dict_repo_file_python:
        if not os.path.exists(save_me_test_me_dir+repo_name+".pkl"):
            continue
        v="7"
        pro_path = util.data_root + "python_star_2000repo/"
        pro_path+=repo_name+"/"
        ven_dir="".join([pro_path, "venv_test_", v])
        if os.path.exists(ven_dir):

            shutil.rmtree(ven_dir)
            print("remove the dir ",ven_dir)

        dict_me_test_me_pair = util.load_pkl(save_me_test_me_dir, repo_name)
        dict_all_test_html=dict()
        for file_html in dict_me_test_me_pair:
            dict_fullme_test_me_pair=dict_me_test_me_pair[file_html]
            for fullme in dict_fullme_test_me_pair:
                for test_html,cl,me in dict_fullme_test_me_pair[fullme]["test_pair"]:
                    if test_html in dict_all_test_html:
                        dict_all_test_html[test_html].add((cl,me))
                    else:
                        dict_all_test_html[test_html]=set([(cl, me)])
        for test_html in dict_all_test_html:
            run_test_result=run_test_file(test_html, pro_path, v)
            csv_result.append([repo_name,test_html,run_test_result])
    util.save_csv(util.data_root + "test_case_run_result_csv/for_else.csv", csv_result,
                  ["repo_name", "test_html", "run_test_result"])
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

    cmd_test = make_pytest_test(pro_path, relative_test_file_path, file_name, fun_list)
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
        total_cmd.append(make_pytest_test(pro_path, relative_test_file_path, file_name, fun_list=[]))

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