import sys, ast, os, copy
import tokenize
import sys
sys.path.append("..")
sys.path.append("../../")
pro_root="/".join(os.path.abspath(__file__).split("/")[:-3])+"/"
sys.path.append(pro_root+"code/")
sys.path.append(pro_root+"code/test_case")
sys.path.append(pro_root+"code/transform_c_s")
import time
import util,github_util
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
def create_virtual_envi(pro_path,v="9"):
    return "".join(["cd ", pro_path, " ; python3.",v," -m venv venv_test_",v, " ; . ./","venv_test_",v,"/bin/activate;"])
    # return "".join(["cd ", pro_path, "&& python2 -m pip install virtualenv && python2 -m virtualenv venv_test && . ./venv_test/bin/activate"])

def export_python_path(pro_path,relative_test_file_path):
    dir_up = os.path.dirname(pro_path + relative_test_file_path)
    # print("first dir: ",dir_up)
    init_module = ["export PYTHONPATH=" + dir_up]
    all_own_modules = []
    while dir_up != pro_path[:-1]:
        dir_upup = os.path.dirname(dir_up)
        all_own_modules.append(dir_upup)
        # print(dir_up, dir_upup)
        dir_up = dir_upup
    return ":".join(init_module+all_own_modules+[";"])
def pip_install(pro_path,v="9"):
    # cmd_pip_pack = ""
    split_install = "*************************install*************************"
    # require_full_path = findfile(pro_path, "setup.py")
    # cmd_pip_pack = ["echo '", split_install, "' ;","pip3 install pytest; pipreqs ./ --savepath requirements_pipreqs_gen.txt;"]
    cmd_pip_pack = ["echo '", split_install, "' ;","pip3 install pytest pytest-mock requests yarg pytest-cov; pip3 install .; python3 "+pro_root+"code/test_case/pipreqs.py; "]
    #pip3 install -r requirements_my_gen.txt;
    if os.path.exists(pro_path+"requirements_my_gen.txt"):
        print("yes>>>>>>>>")
        with open(pro_path+"requirements_my_gen.txt", "r") as file:
            pack_list=file.read().split("\n")
            for pack in pack_list:
                if not pack:
                    continue
                cmd_pip_pack+=["pip3 install ",pack,";"]

    # if require_full_path:#1!=1:#
    #     # cmd_pip_pack = "".join(["python2 ", require_full_path, " install "])
    #     cmd_pip_pack += ["python3.",v, " ",require_full_path, " install "," ;"]

    # require_txt_full_path = findreq(pro_path)
    # if require_txt_full_path:
    #         for require in require_txt_full_path:
    #             cmd_pip_pack += ["pip3.", v, " install -r ", require, " ;"]


    cmd_pip_pack = "".join(cmd_pip_pack+ ["echo '", split_install, "';"])
        # require_full_path = findfile(pro_path, "requirements.txt")
        # if require_full_path:
        #     cmd_pip_pack = "".join(["echo '",split_install,"' ; pip3.",v," install -r ", require_full_path," ; echo '",split_install,"'"])
    # if require_full_path or require_txt_full_path:
    #     return cmd_pip_pack
    return cmd_pip_pack
def make_cmd_test(pro_path,relative_test_file_path,file_name,fun_list=[]):
    split_test_str = "*************************test*************************"
    cmd_test = ["echo '", split_test_str, "' ; "]
    whether_same=relative_test_file_path.split("/")
    if 1:#len(set(whether_same))==len(whether_same):#may have the same module namehttps://github.com/nodejs/node-gyp/tree/master/gyp/pylib/gyp/input_test.py

        # file_name = ".".join(relative_test_file_path.split("/")) + file_name[:-3]
        # file_name = "/".join(relative_test_file_path.split("/")) + file_name
        file_name  =relative_test_file_path+file_name
        print("file_name: ",file_name)
        for ind, e in enumerate(fun_list):
            # print("fun: ", e,relative_test_file_path.split("/"))
            fun_list[ind] = file_name + "::" + e
            # print("fun_list[ind]: ",fun_list[ind])
        relative_test_file_path=""

    cmd_test += ["echo ","$PYTHONPATH;","cd ", pro_path + relative_test_file_path, " ;"]# echo '", split_test_str, "' ; "]
    if not fun_list:
        cmd_test += ["python3.", v, " -m pytest -v ", file_name," ;"]
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
            re_install_cmd=[]
            for modu in module_list:
                re_install_cmd += ["pip3 install ", modu, ";"]

            # print(re_install_cmd)
            return re_install_cmd
        return None
if __name__ == '__main__':
    pro_path=util.data_root+"python_star_2000repo/"#"cloud-custodian/"#"django/"#node-gyp#bert#sentence-transformers
    pro_path+="oppia/"#"ansible/"#"sentry/"#"security_monkey/"#"elastalert/"#"boto3/"#"cloud-custodian/"#"poetry/"#"sentence-transformers/"#"bert/"#"rasa/"#"node-gyp/"#"rtv/"#"django-extensions/"#"ungoogled-chromium/"##"allennlp/"#"django/"#"django-extensions/"#"cd/"#"boto3/"#"security_monkey/"#"oppia/"#"lbry-sdk/"#"node-gyp/"#"cloud-custodian/"#"security_monkey/"
    v="7"
    #"gyp/pylib/gyp/input_test.py"#"tests/puzzle/test_transaction.py"#"tests/unit/resources/test_model.py"#"security_monkey/tests/core/test_auditor.py"#"scripts/linters/codeowner_linter_test.py"#"tests/unit/wallet/test_wallet.py"#"security_monkey/tests/core/test_auditor.py"#"gyp/pylib/gyp/input_test.py"#"tests/test_policy.py"#"gyp/pylib/gyp/input_test.py"

    relative_test_file="scripts/linters/codeowner_linter_test.py"#"test/units/plugins/connection/test_local.py"#"tests/sentry/eventstore/test_base.py"#"security_monkey/tests/core/test_auditor.py"#"tests/alerts_test.py"#"tests/unit/resources/test_model.py"#"tests/test_policy.py"#"tests/puzzle/test_transaction.py"#"tokenization_test.py"#"tests/core/policies/test_unexpected_intent_policy.py"#"gyp/pylib/gyp/input_test.py"#"tests/test_objects.py"#"tests/management/commands/shell_plus_tests/test_shell_plus.py"#"utils/tests/test_domain_substitution.py"#"tests/nn/chu_liu_edmonds_test.py"#"tests/test_objects.py"#"tests/forms_tests/field_tests/test_base.py"#"tests/management/commands/shell_plus_tests/test_shell_plus.py"#"tests/puzzle/test_transaction.py"#"tests/unit/resources/test_model.py"#"security_monkey/tests/core/test_auditor.py"#"scripts/linters/codeowner_linter_test.py"#"tests/unit/wallet/test_wallet.py"#"security_monkey/tests/core/test_auditor.py"#"gyp/pylib/gyp/input_test.py"#"tests/test_policy.py"#"gyp/pylib/gyp/input_test.py"
    relative_test_file_path = "/".join(relative_test_file.split("/")[:-1]) + "/" if len(relative_test_file.split("/"))>1 else ""
    # print("relative_test_file_path: ",relative_test_file_path)
    file_name = relative_test_file.split("/")[-1]
    #'''
    cmd_virtu=create_virtual_envi(pro_path,v)#"".join(["cd ", pro_path," && python3.9 -m venv venv_test && . ./venv_test/bin/activate"])
    cmd_pip_pack = pip_install(pro_path,v)

    
    # relative_test_file_path="gyp/pylib/gyp/"#"tests/"#"tests/forms_tests/field_tests/"#"gyp/pylib/gyp/"#"gyp/pylib/gyp/generator/"
    # file_name="input_test.py"#test_policy.py "tokenization_test.py"#"test_base.py"#"input_test.py"#"msvs_test.py" #test_util.py
    cmd_export_python=export_python_path(pro_path,relative_test_file_path)#":".join(init_module+all_own_modules)
    # cmd_pip_pack+= " && pip install tensorflow==1.11.0"
    fun_list = []
    # fun_list=["CodeownerLinterTests.test_missing_important_codeowner_path_from_list"]
    # fun_list=[file_name[:-3]+".TokenizationTest.test_basic_tokenizer_lower",file_name[:-3]+".TokenizationTest.test_is_punctuation","optimization_test.OptimizationTest.test_adam"]
    # fun_list=" ".join(fun_list)

    cmd_test =make_cmd_test(pro_path, relative_test_file_path, file_name,fun_list)
    # cmd_test +=["python3.7 - m scripts.run_backend_tests --test_target = scripts.linters.codeowner_linter_test.CodeownerLinterTests.test_missing_important_codeowner_path_from_list;"]


    if cmd_pip_pack:
        print("it has requirements: ",cmd_pip_pack)
        total_cmd="".join([cmd_virtu,cmd_export_python,cmd_pip_pack,cmd_test])#,cmd_test
    else:
        print("it does not have requirements: ")
        total_cmd = "".join([cmd_virtu,cmd_export_python, cmd_test])#, cmd_test

    # print("*************************prepare install dependency and set up self-defined path*************************")
    # with os.popen(total_cmd) as process:
    #     content = process.read()
    #     print(content)
    
    result = subprocess.run(total_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    std_out_res=result.stdout.decode("utf-8")
    print("std_out_res: \n", std_out_res)
    std_error = result.stderr.decode("utf-8") if result.stderr else ""
    std_args = result.args
    # print("\n".join(result.stdout.decode("utf-8").split("*************************test*************************")))

    print("std_error: \n", std_error)
    print("std_args: \n", std_args)


    #'''
    re_install_cmd=rerun_pytest(std_out_res)#['pip3 install ', 'setuptools_rust', ' ', 'setuptools_rust', ' ', 'spacy', ' ', ';']#
    while re_install_cmd:

        total_cmd = ["cd ",pro_path,";", ". ./venv_test_"+v+"/bin/activate;"]+re_install_cmd
        total_cmd.append(make_cmd_test(pro_path, relative_test_file_path, file_name, fun_list=[]))

        total_cmd = "".join(total_cmd)
        print(total_cmd)
        result = subprocess.run(total_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        std_out_res = result.stdout.decode("utf-8")
        print("std_out_res: ",std_out_res)
        std_error = result.stderr.decode("utf-8") if result.stderr else ""
        std_args = result.args
        # print("\n".join(result.stdout.decode("utf-8").split("*************************test*************************")))

        print("std_error: \n", std_error)
        print("std_args: \n", std_args)
        re_install_cmd_old = rerun_pytest(std_out_res)
        if re_install_cmd_old==re_install_cmd:
            break
        re_install_cmd=re_install_cmd_old
    # if "No module named" in std_out_res:

    # std_out_res=result.stdout.decode("utf-8").split("*************************test*************************")
    # if len(std_out_res)==3:
    #     test_res=std_out_res[1]
    #     print("test_result: \n",test_res)


#CompletedProcess(args='echo Hello ; echo World', returncode=0, stdout=b'Hello\nWorld\n')
#
# a=subprocess.Popen("'''"+total_cmd+"'''",shell=True)
#
# print(a)
# print("*************************begin test the method*************************")
# with os.popen(cmd_test) as process:
#     content = process.read()
#     print(content)
# print("*************************begin test the method*************************")
# '''