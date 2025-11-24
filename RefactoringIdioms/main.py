import argparse,os,sys
abs_path=os.path.abspath(os.path.dirname(__file__))
# print("abs_path_1: ",abs_path)
pack_path="/".join(abs_path.split("/")[:-1])
# print(pack_path)
# sys.path.append(pack_path)
sys.path.append("/".join(abs_path.split("/")[:-1]))
# sys.path.append("/".join(abs_path.split("/")[:-2]))
from RefactoringIdioms.extract_transform_complicate_code_new import \
    transform_for_else_compli_to_simple_improve_copy_result_csv, extract_compli_var_unpack_for_target_improve_new, \
    extract_compli_multiple_assign_code_improve_complete_improve
from RefactoringIdioms.extract_transform_complicate_code_new.comprehension import \
    extract_compli_for_comprehension_only_one_stmt_improve, extract_compli_for_comprehension_dict_only_one_stmt_new, \
    extract_compli_for_comprehension_set_only_one_stmt
from RefactoringIdioms.extract_transform_complicate_code_new import extract_compli_var_unpack_star_call_improve, \
    extract_compli_truth_value_test_code_remove_is_isnot, transform_chained_comparison_compli_to_simple
import util
import CodeInfo
# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
def save_output(outputpath):
    result=dict()
    util.save_file_path(outputpath,result)
def format_code_list(filepath,code_pair_list,outputpath):
    format_code_list=[]
    print(f"************Result Summary of {filepath.split('/')[-1]}************")
    for  ind_idiom,(idiom,cl, me, oldcode, new_code,lineno_list) in enumerate(code_pair_list):
        code_info_cla = CodeInfo.CodeInfo(filepath, idiom,cl, me, oldcode, new_code,lineno_list)
        # print(code_info_cla.__dict__)
        print(f">>>Result{ind_idiom+1}",code_info_cla.full_info())
        format_code_list.append(code_info_cla.__dict__)
    print(f"************Result of {filepath.split('/')[-1]} End************")
    return format_code_list
    # return code_dict
def get_list_comprehension(code_frag):
    print(">>>>>>>>>Checking List Comprehension")
    code_pair_list = extract_compli_for_comprehension_only_one_stmt_improve.get_list_compreh(code_frag)
    for e in code_pair_list:
        e.insert(0, "List Comprehension")
    return code_pair_list

def get_set_comprehension(code_frag):
    print(">>>>>>>>>Checking Set Comprehension")
    code_pair_list = extract_compli_for_comprehension_set_only_one_stmt.get_set_compreh(code_frag)

    for e in code_pair_list:
        e.insert(0, "Set Comprehension")
    return code_pair_list
def get_dict_comprehension(code_frag):
    print(">>>>>>>>>Checking Dict Comprehension")

    code_pair_list = extract_compli_for_comprehension_dict_only_one_stmt_new.get_dict_compreh(code_frag)
    for e in code_pair_list:
        e.insert(0, "Dict Comprehension")
    return code_pair_list
def get_chain_compare(code_frag):
    print(">>>>>>>>>Checking Chain Comparison")
    code_pair_list_chain_compare = transform_chained_comparison_compli_to_simple.get_chain_compare(code_frag)
    # code_pair_list.extend([e.insert(0,"Chain Compare") for e in code_pair_list_chain_compare])
    for e in code_pair_list_chain_compare:
        e.insert(0, "Chain Compare")
    return code_pair_list_chain_compare

def get_truth_value_test(code_frag):
    print(">>>>>>>>>Checking Truth Value Test")
    code_pair_list_truth_value = extract_compli_truth_value_test_code_remove_is_isnot.get_truth_value_test_code(
        code_frag)
    # code_pair_list.extend([e.insert(0,"Truth Value Test") for e in code_pair_list_truth_value])
    for e in code_pair_list_truth_value:
        e.insert(0, "Truth Value Test")
    return code_pair_list_truth_value


def get_ass_multi_targets(code_frag):
    print(">>>>>>>>>Checking Assign Multiple Targets")

    code_pair_list_assign_multi_targets = extract_compli_multiple_assign_code_improve_complete_improve.transform_multiple_assign_code(
        code_frag)
    # code_pair_list.extend([e.insert(0,"Assign Multi Targets") for e in code_pair_list_assign_multi_targets])
    for e in code_pair_list_assign_multi_targets:
        e.insert(0, "Assign Multi Targets")
    return code_pair_list_assign_multi_targets


def get_for_multi_targets(code_frag):
    print(">>>>>>>>>Checking For Multiple Targets")

    code_pair_list_for_multi_target = extract_compli_var_unpack_for_target_improve_new.transform_for_multiple_targets_code(
        code_frag)
    # code_pair_list.extend([e.insert(0,"For Multi Targets") for e in code_pair_list_for_multi_target])
    for e in code_pair_list_for_multi_target:
        e.insert(0, "For Multi Targets")
    return code_pair_list_for_multi_target


def get_for_else(code_frag):
    print(">>>>>>>>>Checking For Else")

    code_pair_listfor_else = transform_for_else_compli_to_simple_improve_copy_result_csv.transform_for_else_code(
        code_frag)
    for e in code_pair_listfor_else:
        e.insert(0, "For Else")
        # code_pair_list.append(e)
    return code_pair_listfor_else


def get_star_call(code_frag):
    # code_pair_list.extend([e.insert(0,"For Else") for e in code_pair_listfor_else])
    print(">>>>>>>>>Checking Star in Function Call")

    code_pair_list_call_star = extract_compli_var_unpack_star_call_improve.transform_star_call_code(
        code_frag)
    for e in code_pair_list_call_star:
        e.insert(0, "Call Star")
        # code_pair_list.append(e)
    return code_pair_list_call_star

def get_refactoring(idiom,filepath,outputpath):
    print(f"************For File {filepath.split('/')[-1]}, begin to find refactorable non-idiomatic code with Python idioms************")


    code_frag=util.load_file_path(file_path=filepath)
    if idiom == 'List Comprehension':
        code_pair_list = get_list_comprehension(code_frag)
        if code_pair_list:
            pass
            # print("code_list: ",code_pair_list,jsonify(code_pair_list).json[0][0])

        # return jsonify(code_pair_list)

        pass
    elif idiom == 'Set Comprehension':

        code_pair_list = get_set_comprehension(code_frag)
        if code_pair_list:
            pass
            # print("code_list: ", code_pair_list, jsonify(code_pair_list).json[0][0])

        # return jsonify(code_pair_list)
        pass
    elif idiom == 'Dict Comprehension':

        code_pair_list = get_dict_comprehension(code_frag)
        # return jsonify(code_pair_list)
        pass
    elif idiom == 'Chain Comparison':

        code_pair_list =get_chain_compare(code_frag)
        # return jsonify(code_pair_list)
        pass
    elif idiom == 'Truth Value Test':

        code_pair_list = get_truth_value_test(code_frag)
        # return jsonify(code_pair_list)
        pass
    elif idiom == 'Assign Multiple Targets':

        code_pair_list = get_ass_multi_targets(
            code_frag)
        # return jsonify(code_pair_list)
        pass
    elif idiom == 'For Multiple Targets':

        code_pair_list = get_for_multi_targets(
            code_frag)
        # return jsonify(code_pair_list)
        pass
    elif idiom == 'For Else':

        code_pair_list = get_for_else(
            code_frag)
        # return jsonify(code_pair_list)
        pass
    elif idiom == 'Star in Call':

        code_pair_list = get_star_call(
            code_frag)
        # return jsonify(code_pair_list)

        pass
    elif idiom == 'All':
        # idioms = ['All','List Comprehension', 'Set Comprehension', 'Dict Comprehension','Chain Comparison',
        # 'Truth Value Test','Assign Multiple Targets','For Multiple Targets','For Else'
        # ,'Star in Call']
        code_pair_list = []
        # print("code_frag")
        # print(code_frag)
        code_pair_list_compre = get_list_comprehension(code_frag)
        code_pair_list.extend(code_pair_list_compre)

        code_pair_set_compre=get_set_comprehension(code_frag)
        code_pair_list.extend(code_pair_set_compre)

        code_pair_dict_compre=get_dict_comprehension(code_frag)
        code_pair_list.extend(code_pair_dict_compre)

        code_pair_chain_compare = get_chain_compare(code_frag)
        code_pair_list.extend(code_pair_chain_compare)

        code_pair_truth_test = get_truth_value_test(code_frag)
        code_pair_list.extend(code_pair_truth_test)

        code_pair_multi_ass = get_ass_multi_targets(code_frag)
        code_pair_list.extend(code_pair_multi_ass)

        code_pair_for_multi_target=get_for_multi_targets(code_frag)
        code_pair_list.extend(code_pair_for_multi_target)

        code_pair_for_else = get_for_else(code_frag)
        code_pair_list.extend(code_pair_for_else)

        code_pair_star_call = get_star_call(code_frag)
        code_pair_list.extend(code_pair_star_call)


    # print(code_pair_list)
    new_code_list=format_code_list(filepath, code_pair_list,outputpath)
    return new_code_list
# Press the green button in the gutter to run the script.
def main(args):
    # args = parser.parse_args()
    filepath = args.filepath
    idiom = args.idiom
    outputpath = args.outputpath
    format_code_list=[]
    a = []
    for i in range(1):
        a.append(i)
    # envname = args.envname
    if os.path.isdir(filepath):
        for path,dir_list,file_list in os.walk(filepath):
            for file_name in file_list:
                abs_path=os.path.join(path,file_name)
                if abs_path.endswith(".py"):
                    each_file_code_list=get_refactoring(idiom, abs_path, outputpath)
                    format_code_list.extend(each_file_code_list)
    else:
        format_code_list=get_refactoring(idiom, filepath, outputpath)
    print(f"************Result is saved in {outputpath}************", )
    util.save_json_file_path(outputpath, format_code_list)
    # print(args)
    # print("main.py main() finished!")
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='RefactoringIdioms')
    parser.add_argument('--envname', type=str,
                        help='envname', default="CartPole-v0")
    parser.add_argument('--filepath', type=str,
                        help='filepath', default=abs_path+"/file.py")
    parser.add_argument('--idiom', type=str,
                        help='idiom', default="All")
    parser.add_argument('--outputpath', type=str,
                        help='outputpath', default="result.json")

    args = parser.parse_args()
    print(args)
    main(args)
    filepath = args.filepath
    idiom = args.idiom
    outputpath = args.outputpath

    a=[]
    for i in range(1):
        a.append(i)
    # envname = args.envname
    # get_refactoring(idiom,filepath,outputpath)
    print(args)
    print("finished!")
    #    envname='MountainCar-v0'
    # env = gym.make(envname)
    # print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
