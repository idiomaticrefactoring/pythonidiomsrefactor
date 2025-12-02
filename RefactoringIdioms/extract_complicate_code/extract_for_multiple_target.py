import sys
import ast
import os
import copy
import traceback

# ==========================================
# 路径修复
# ==========================================
current_file_path = os.path.abspath(__file__)
# extract_transform... -> RefactoringIdioms -> Root
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
if project_root not in sys.path:
    sys.path.append(project_root)

# ==========================================
# 模块导入
# ==========================================
from RefactoringIdioms.extract_simp_cmpl_data import ast_util
from RefactoringIdioms.transform_c_s import transform_for_multiple_target


# ==========================================
# 核心检测逻辑
# ==========================================

def whether_slice_is_constant(slice, var):
    """判断切片是否为常量"""
    if isinstance(slice, ast.Constant):
        slice_value = slice.value
        if isinstance(slice_value, int):
           return True
        else:
            return False
    elif isinstance(slice, ast.Slice):
        if slice.lower:
            if not isinstance(slice.lower, ast.Constant):
                return False
        if slice.upper:
            if not isinstance(slice.upper, ast.Constant):
                return False
        if slice.step:
            if isinstance(slice.step, ast.Constant):
                if not (isinstance(slice.step.value, int) and slice.step.value == 1):
                    return False
            else:
                return False
    return False

def is_var_subscript(node, var):
    if isinstance(node, ast.Subscript):
        value = node.value
        if ast.unparse(value) == var:
            slice = node.slice
            return whether_slice_is_constant(slice, var)
        elif isinstance(value, ast.Subscript):
            return is_var_subscript(value, var)
    return False

def is_var(node, var_ast):
    if isinstance(node, type(var_ast)) and ast.unparse(node) == ast.unparse(var_ast):
        return True
    return False

def whether_var_subscript(node, target, var_list):
    var = ast.unparse(target)
    if is_var_subscript(node, var):
        var_list.add(node)
        return True
    elif is_var(node, target):
        return False
    else:
        for e in ast.iter_child_nodes(node):
            if not whether_var_subscript(e, target, var_list):
                return False
        return True

def get_for_target(tree, max_unpack=False):
    """
    获取可重构的 For 循环目标
    :param max_unpack: 最大允许解包的元素数量限制
    """
    code_list = []

    for node in ast.walk(tree):
        if isinstance(node, ast.For):
            var_list = set([])
            target = node.target
            var = ast.unparse(target)
            
            count_obj = ast_util.get_basic_count(target)
            if count_obj == 1:
                # 1. 检查循环体中是否有对 target 的写操作 (如果有则不能重构)
                has_write = False
                for e_body in ast.walk(node):
                    if isinstance(e_body, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                        targets = e_body.targets if hasattr(e_body, 'targets') else [e_body.target]
                        for left_e in targets:
                            if ast.unparse(left_e) == var:
                                has_write = True
                                break
                            # 深度遍历左值
                            for ass_e in ast.walk(left_e):
                                if ast.unparse(ass_e) == var:
                                    has_write = True
                                    break
                            if has_write: break
                        if has_write: break
                if has_write: continue

                # 2. 检查循环体中是否有对 target 的使用
                has_use = False
                for stmt in node.body:
                    for e in ast.walk(stmt):
                        if is_var(e, target):
                            has_use = True
                            break
                    if has_use: break
                
                if has_use:
                    # 3. 检查所有使用是否都是下标访问 (var[0])
                    all_subscript = True
                    for stmt in node.body:
                        if not whether_var_subscript(stmt, target, var_list):
                            all_subscript = False
                            break
                    
                    if all_subscript:
                        var_list_real = list(var_list)
                        
                        # 去重逻辑: ['val[1]', 'val[1][0]'] -> 保留最外层
                        for i, var1 in enumerate(var_list):
                            for j, var2 in enumerate(var_list):
                                if ast.unparse(var1) in ast.unparse(var2) and ast.unparse(var1) != ast.unparse(var2):
                                    if var2 in var_list_real:
                                        var_list_real.remove(var2)
                        
                        # [细粒度规则] 检查解包数量限制
                        # 如果 var_list_real 长度超过限制，则跳过
                        if max_unpack and isinstance(max_unpack, int):
                            if len(var_list_real) > max_unpack:
                                continue

                        Map_var = dict()
                        node_copy = copy.deepcopy(node)
                        
                        if transform_for_multiple_target:
                            new_code = transform_for_multiple_target.transform_for_node_var_unpack(
                                node_copy, var_list_real, Map_var
                            )
                            if new_code:
                                code_list.append([node, new_code])
                            else:
                                # 转换失败的情况
                                pass
    return code_list

# ==========================================
# 主入口函数 (适配 main.py)
# ==========================================

def transform_for_multiple_targets_code(content, config=None):
    if config is None:
        config = {}
        
    # 获取细粒度配置
    max_unpack = config.get("max-elements-to-unpack", False)
    
    code_pair_list = []
    try:
        file_tree = ast.parse(content)
        ana_py = ast_util.Fun_Analyzer()
        ana_py.visit(file_tree)
        
        # 兼容模块级代码
        search_targets = ana_py.func_def_list if ana_py.func_def_list else [(file_tree, "Module")]

        for tree, class_name in search_targets:
            try:
                me_name = getattr(tree, "name", "")
            except:
                me_name = ""
            
            # 传入配置限制
            new_code_list = get_for_target(tree, max_unpack=max_unpack)

            for e in new_code_list:
                if len(e) < 2:
                    continue
                
                old_node = e[0]
                new_node = e[1]
                
                line_list = [[old_node.lineno, old_node.end_lineno]]
                
                code_pair_list.append([
                    class_name if class_name != "Module" else "",
                    me_name,
                    ast.unparse(old_node), 
                    ast.unparse(new_node),
                    line_list
                ])

        return code_pair_list

    except Exception:
        # traceback.print_exc()
        return []

if __name__ == '__main__':
    # 简单测试
    code = '''
for T in a:
    c = 1
    e = T[0] + T[1]
    '''
    print(transform_for_multiple_targets_code(code,config={"max-elements-to-unpack": 2}))


