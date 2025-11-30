import sys
import ast
import os
import traceback

# ==========================================
# 路径修复
# ==========================================
current_file_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file_path))))
if project_root not in sys.path:
    sys.path.append(project_root)

# ==========================================
# 模块导入
# ==========================================
from RefactoringIdioms.extract_simp_cmpl_data import ast_util
from RefactoringIdioms.extract_transform_complicate_code_new.comprehension import comprehension_utils
from RefactoringIdioms.transform_c_s import transform_list_comp



def get_list_compreh(content, config=None):
    """
    检测列表推导式重构的主入口函数。
    适配 main.py 接口，支持细粒度配置。
    """
    if config is None:
        config = {}
        
    refactor_with_if = config.get("refactor-with-if", True)
    code_pair_list = []

    try:
        file_tree = ast.parse(content)
        function_analyzer = ast_util.Fun_Analyzer()
        function_analyzer.visit(file_tree)

        for tree, class_name in function_analyzer.func_def_list:
            method_name = getattr(tree, "name", "")
            
            # 调用通用工具函数，查找列表构建模式
            # 关键参数: 
            # 1. const_empty_list=["[]", "list()"] : 识别空列表初始化
            # 2. const_func_name="append" : 识别 .append() 调用
            new_code_list = comprehension_utils.get_complicated_for_comprehen_code_list(
                tree, 
                const_empty_list=["[]", "list()"], 
                const_func_name="append"
            )
            
            for for_node, assign_node, remove_ass_flag in new_code_list:
                
                # 检查配置：如果禁用了 refactor-with-if 且代码包含 if，则跳过
                if not refactor_with_if and comprehension_utils.has_if_node(for_node):
                    continue

                # 执行转换 (调用针对 List 的 transform 模块)
                new_code = transform_list_comp.transform(for_node, assign_node)
                
                # 构建新代码字符串
                if remove_ass_flag:
                    complete_new_code = ast.unparse(new_code)
                else:
                    complete_new_code = ast.unparse(assign_node) + "\n" + ast.unparse(new_code)
                
                # 记录行号
                line_list = [
                    [assign_node.lineno, assign_node.end_lineno],
                    [for_node.lineno, for_node.end_lineno]
                ]
                
                old_code_str = ast.unparse(assign_node) + "\n" + ast.unparse(for_node)
                
                code_pair_list.append([
                    class_name, 
                    method_name, 
                    old_code_str, 
                    complete_new_code, 
                    line_list
                ])
                
        return code_pair_list

    except Exception:
        # traceback.print_exc()
        return []

if __name__ == '__main__':
    # 简单的本地测试
    code = '''
def main():
    a = []
    for i in range(10):
        if i > 5:
            a.append(i)
    
    b = []
    for j in range(5):
        b.append(j * 2)
    '''
    
    print("Testing with default config (should detect):")
    results1 = get_list_compreh(code)
    
    print("\nTesting with refactor-with-if=False (should be empty):")
    results2 = get_list_compreh(code, config={"refactor-with-if": False})
    
    # 将结果列表放入一个元组或列表进行遍历
    all_test_runs = [("Default Config", results1), ("No If Config", results2)]
    
    for config_name, results in all_test_runs:
        print(f"\n=== Results for {config_name} ===")
        if not results:
            print("No refactoring opportunities found.")
            continue
            
        for res in results:
            # res 是一个单独的重构项列表 [cl, me, old, new, lines]
            try:
                cl, me, oldcode, new_code, *rest = res
                lineno_list = rest[0] if rest else []
                
                # 为了演示，简单打印即可，不需要构建 CodeInfo (除非你导入了它)
                # 如果你一定要用 CodeInfo，确保已经正确 import
                print(f"Method: {me}")
                print(f"Old Code:\n{oldcode}")
                print(f"New Code:\n{new_code}")
                print("-" * 20)
            except ValueError as e:
                print(f"Error unpacking result: {e}, raw data: {res}")





