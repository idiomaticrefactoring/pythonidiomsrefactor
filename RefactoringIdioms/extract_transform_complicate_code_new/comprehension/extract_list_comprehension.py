import sys
import ast
import os
import traceback

# ==========================================
# 路径修复
# ==========================================
current_file_path = os.path.abspath(__file__)
# extract_compli_...py -> comprehension -> extract_transform... -> RefactoringIdioms -> ROOT
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file_path))))
if project_root not in sys.path:
    sys.path.append(project_root)

# ==========================================
# 模块导入
# ==========================================
from RefactoringIdioms.extract_simp_cmpl_data import ast_util
from RefactoringIdioms.extract_transform_complicate_code_new.comprehension import comprehension_utils
from RefactoringIdioms.transform_c_s import transform_list_comp

def has_if_node(node):
    """检查节点下是否包含 If 节点，用于配置过滤"""
    for child in ast.walk(node):
        if isinstance(child, ast.If):
            return True
    return False

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
        ana_py = ast_util.Fun_Analyzer()
        ana_py.visit(file_tree)

        for tree, class_name in ana_py.func_def_list:
            me_name = getattr(tree, "name", "")
            
            # 调用通用工具函数，查找列表构建模式
            # 关键参数: 
            # 1. const_empty_list=["[]", "list()"] : 识别空列表初始化
            # 2. const_func_name="append" : 识别 .append() 调用
            new_code_list = comprehension_utils.get_complicated_for_comprehen_code_list(
                tree, 
                content, 
                const_empty_list=["[]", "list()"], 
                const_func_name="append"
            )
            
            for for_node, assign_node, remove_ass_flag in new_code_list:
                
                # 检查配置：如果禁用了 refactor-with-if 且代码包含 if，则跳过
                if not refactor_with_if and has_if_node(for_node):
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
                    me_name, 
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
def test():
    a = []
    for i in range(10):
        if i > 5:
            a.append(i)
    '''
    print(get_list_compreh(code))


