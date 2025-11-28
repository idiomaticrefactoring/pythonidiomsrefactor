import sys
import ast
import os
import traceback

current_file_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file_path))))
if project_root not in sys.path:
    sys.path.append(project_root)

from RefactoringIdioms.extract_simp_cmpl_data import ast_util
from RefactoringIdioms.extract_transform_complicate_code_new.comprehension import comprehension_utils
from RefactoringIdioms.transform_c_s import transform_comprehension_dict_compli_to_simple



def get_dict_compreh(content, config=None):
    if config is None:
        config = {}
    refactor_with_if = config.get("refactor-with-if", True)
    code_pair_list = []

    try:
        file_tree = ast.parse(content)
        ana_py = ast_util.Fun_Analyzer()
        ana_py.visit(file_tree)

        for tree, class_name in ana_py.func_def_list:
            me_name = getattr(tree, "name", "")
            
            # [关键修改] 
            # 1. 传入 "dict()", "{}" 作为空初始化列表
            # 2. 传入 "__setitem__" 作为操作名，utils 会识别这是字典赋值
            new_code_list = comprehension_utils.get_complicated_for_comprehen_code_list(
                tree, 
                content, 
                const_empty_list=["dict()", "{}"], 
                const_func_name="__setitem__" 
            )
            
            for for_node, assign_node, remove_ass_flag in new_code_list:
                if not refactor_with_if and comprehension_utils.has_if_node(for_node):
                    continue

                new_code = transform_comprehension_dict_compli_to_simple.transform(for_node, assign_node)
                
                if remove_ass_flag:
                    complete_new_code = ast.unparse(new_code)
                else:
                    complete_new_code = ast.unparse(assign_node) + "\n" + ast.unparse(new_code)
                
                line_list = [
                    [assign_node.lineno, assign_node.end_lineno],
                    [for_node.lineno, for_node.end_lineno]
                ]
                
                old_code_str = ast.unparse(assign_node) + "\n" + ast.unparse(for_node)
                code_pair_list.append([
                    class_name, 
                    me_name, 
                    old_code_str, 
                    complete_new_code, 
                    line_list
                ])
        return code_pair_list

    except Exception:
        traceback.print_exc()
        return []

if __name__ == '__main__':
    code = '''
def test():
    d = {}
    for i in range(10):
        if i > 5:
            d[i] = i * 2
    '''
    print(get_dict_compreh(code))
    print("-----")
    print(get_dict_compreh(code, {"refactor-with-if": False}))




