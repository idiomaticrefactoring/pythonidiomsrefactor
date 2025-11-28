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
from RefactoringIdioms.transform_c_s import transform_set_comp



def get_set_compreh(content, config=None):
    """
    检测集合推导式重构的主入口函数。
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
            
            # 调用通用工具函数，查找集合构建模式
            # 关键参数: const_empty_list=["set()"], const_func_name="add"
            new_code_list = comprehension_utils.get_complicated_for_comprehen_code_list(
                tree, 
                content, 
                const_empty_list=["set()"], 
                const_func_name="add"
            )
            
            for for_node, assign_node, remove_ass_flag in new_code_list:
                
                # 检查配置：如果禁用了 refactor-with-if 且代码包含 if，则跳过
                if not refactor_with_if and comprehension_utils.has_if_node(for_node):
                    continue

                # 执行转换 (调用针对 Set 的 transform 模块)
                new_code = transform_set_comp.transform(for_node, assign_node)
                
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
        # 生产环境建议记录日志而不是打印堆栈
        # traceback.print_exc()
        return []

if __name__ == '__main__':
    # 简单的本地测试
    code = '''
def test():
    s = set()
    for i in range(10):
        if i > 5:
            s.add(i)
    
        '''
    print(get_set_compreh(code))
    print("-----"*10)
    print(get_set_compreh(code, config={"refactor-with-if": False}))







