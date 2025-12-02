import sys
import ast
import os
import traceback

# ==========================================
# 路径修复
# ==========================================
current_file_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
if project_root not in sys.path:
    sys.path.append(project_root)

# ==========================================
# 模块导入
# ==========================================
from RefactoringIdioms.extract_simp_cmpl_data import ast_util
from RefactoringIdioms.transform_c_s import transform_truth_value


# ==========================================
# 核心检测逻辑
# ==========================================

def decide_compare_complicate_truth_value(test):
    """
    判断比较操作是否为冗余的真值测试。
    例如: if x == True, if x != [], if x is not None
    """
    flag = 0
    ops = test.ops
    left = ast.unparse(test.left)
    
    # 确保有比较器
    if not test.comparators:
        return 0
        
    comp_str = ast.unparse(test.comparators[0])

    # 定义会被视为“冗余”的比较对象
    empty_list = [
        "None", "True", "False", 
        "0", "0.0", "0j", "Decimal(0)", "Fraction(0, 1)", 
        "''", '""', "()", "[]", "{}", "dict()", "set()", "range(0)"
    ]

    # 只有当操作符是 Eq(==), NotEq(!=) 时才认为是简单的真值冗余
    # 注意：Is/IsNot 在某些规范中建议显式使用（如 if x is None），但在某些简化场景下也可移除
    # 这里的逻辑继承自原代码，移除了 Is/IsNot 的直接简化，或者原文件名暗示了 "remove_is_isnot" 的意图
    if len(ops) == 1 and isinstance(ops[0], (ast.Eq, ast.NotEq)):
        if left in empty_list or comp_str in empty_list:
            flag = 1
            
    # 如果确实需要处理 is True / is False 这种写法（虽然 PEP8 推荐直接用 if x），
    # 可以根据需要放开 Is/IsNot 的限制，但要注意 None 的处理
    
    return flag

def get_truth_value_test(tree):
    """
    遍历 AST，寻找可简化的真值测试节点，并生成新节点。
    """
    code_list = []

    for node in ast.walk(tree):
        # 检查控制流语句的测试条件
        if isinstance(node, (ast.If, ast.While, ast.Assert)):
            test = node.test
            if isinstance(test, ast.Compare):
                if decide_compare_complicate_truth_value(test):
                    new_code = transform_truth_value.transform_c_s_truth_value_test(test)
                    code_list.append([test, new_code])

        # 检查布尔运算中的值 (例如: if x == True and y == False)
        elif isinstance(node, ast.BoolOp):
            for value in node.values:
                if isinstance(value, ast.Compare):
                    if decide_compare_complicate_truth_value(value):
                        new_code = transform_truth_value.transform_c_s_truth_value_test(value)
                        code_list.append([value, new_code])

    return code_list

# ==========================================
# 主入口函数 (适配 main.py)
# ==========================================

def get_truth_value_test_code(content, config=None):
    if config is None:
        config = {}
        
    code_pair_list = []
    try:
        file_tree = ast.parse(content)
        ana_py = ast_util.Fun_Analyzer()
        ana_py.visit(file_tree)

        search_targets = ana_py.func_def_list if ana_py.func_def_list else [(file_tree, "Module")]

        for tree, class_name in search_targets:
            me_name = getattr(tree, "name", "")
            if isinstance(tree, ast.Module): me_name = "Global"
            
            # 获取重构建议
            new_code_list = get_truth_value_test(tree)
            
            for old_node, new_node in new_code_list:
                line_list = [[old_node.lineno, old_node.end_lineno]] if hasattr(old_node, "lineno") else []
                
                code_pair_list.append([
                    class_name if class_name != "Module" else "",
                    me_name,
                    ast.unparse(old_node),
                    ast.unparse(new_node),
                    line_list
                ])
                
        return code_pair_list

    except Exception:
        traceback.print_exc()
        return []

if __name__ == '__main__':
    # 简单的测试用例
    code = """
def test():
    if x == True:
        pass
    if y != []:
        pass
    while z == 0:
        pass
    """
    print(get_truth_value_test_code(code))