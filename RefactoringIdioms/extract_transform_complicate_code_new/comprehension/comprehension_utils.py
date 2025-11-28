import sys
import ast
import os
import tokenize
from tokenize import tokenize
from io import BytesIO

# ==========================================
# 路径修复
# ==========================================
current_file_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file_path))))
if project_root not in sys.path:
    sys.path.append(project_root)

package_dir = os.path.join(project_root, "RefactoringIdioms")
if package_dir not in sys.path:
    sys.path.append(package_dir)

# ==========================================
# 模块导入修复
# ==========================================
try:
    from RefactoringIdioms import complicated_code_util
    from RefactoringIdioms import util
    from RefactoringIdioms.extract_simp_cmpl_data import ast_util
except ImportError:
    try:
        import complicated_code_util
        import util
        from extract_simp_cmpl_data import ast_util
    except ImportError:
        pass

# ==========================================
# 全局变量初始化
# ==========================================
try:
    if 'util' in globals() and hasattr(util, 'data_root'):
        dict_repo_file_python = util.load_json(util.data_root, "python3_1000repos_files_info")
    else:
        dict_repo_file_python = {}
except Exception:
    dict_repo_file_python = {}

# ==========================================
# 辅助函数
# ==========================================
def safe_unparse(node):
    """兼容 Python < 3.9 的 unparse"""
    if hasattr(ast, 'unparse'):
        try:
            return ast.unparse(node)
        except:
            return ""
    else:
        try:
            if isinstance(node, ast.Name):
                return node.id
            elif isinstance(node, ast.Attribute):
                val = safe_unparse(node.value)
                return f"{val}.{node.attr}" if val else ""
            elif isinstance(node, ast.Constant):
                return str(node.value)
            elif isinstance(node, ast.Subscript):
                val = safe_unparse(node.value)
                sl = safe_unparse(node.slice)
                return f"{val}[{sl}]" if val else ""
            return ""
        except:
            return ""

def visit_single_vars(target, list_vars):
    """提取变量名"""
    if isinstance(target, ast.Name):
        list_vars.append(safe_unparse(target))
    elif isinstance(target, ast.Subscript):
        list_vars.append(safe_unparse(target))
        visit_single_vars(target.value, list_vars)
    elif isinstance(target, ast.Attribute):
        list_vars.append(safe_unparse(target))
        visit_single_vars(target.value, list_vars)

def get_time_var(vars_set):
    """获取变量及其所有引用形式"""
    all_var_list = []
    try:
        var_name = list(vars_set)[0]
        for ind, e_var in enumerate(ast.walk(ast.parse(var_name))):
            if safe_unparse(e_var) == var_name and isinstance(e_var, (ast.Subscript, ast.Attribute, ast.Name)):
                visit_single_vars(e_var, all_var_list)
                break
    except:
        pass
    
    if not all_var_list and vars_set:
        all_var_list.append(list(vars_set)[0])
    return all_var_list

def check_call_usage_in_tree(tree, fun_name, time_var_list):
    """检查全树中特定函数内是否使用了变量 (用于闭包检查)"""
    try:
        ana_py_fun = ast_util.Fun_Analyzer()
        ana_py_fun.visit(tree)
        for tree_fun, class_name in ana_py_fun.func_def_list:
            if hasattr(tree_fun, "name"):
                if tree_fun.name == fun_name:
                    for child in ast.walk(tree_fun):
                        if safe_unparse(child) in time_var_list:
                            return True
    except:
        pass
    return False

# ==========================================
# 核心逻辑函数
# ==========================================

def get_func_name(one_body):
    pre_name, call_name = None, None
    if isinstance(one_body, ast.Expr) and isinstance(one_body.value, ast.Call):
        call_front = one_body.value.func
        if isinstance(call_front, ast.Name):
            call_name = safe_unparse(call_front)
        elif isinstance(call_front, ast.Attribute):
            call_name = call_front.attr
            pre_name = safe_unparse(call_front.value)
        else:
            call_name = safe_unparse(call_front)
    elif isinstance(one_body, ast.Assign):
        if len(one_body.targets) == 1 and isinstance(one_body.targets[0], ast.Subscript):
            target = one_body.targets[0]
            pre_name = safe_unparse(target.value)
            call_name = "__setitem__"
    return pre_name, call_name

def whether_fun_is_append(one_body, assign_block_list, const_func_name="append"):
    if isinstance(one_body, ast.Expr) and isinstance(one_body.value, ast.Call):
        call_front = one_body.value.func
        if isinstance(call_front, ast.Name):
            call_name = safe_unparse(call_front)
        elif isinstance(call_front, ast.Attribute):
            call_name = call_front.attr
        else:
            call_name = safe_unparse(call_front)
        
        if call_name == const_func_name:
            assign_block_list.append([one_body])
            return True
    elif isinstance(one_body, ast.Call):
        call_front = one_body.func
        call_name = ""
        if isinstance(call_front, ast.Name):
            call_name = safe_unparse(call_front)
        elif isinstance(call_front, ast.Attribute):
            call_name = call_front.attr
        else:
            call_name = safe_unparse(call_front)
        
        if call_name == const_func_name:
            assign_block_list.append([one_body])
            return True
    elif isinstance(one_body, ast.Assign) and const_func_name == "__setitem__":
        if len(one_body.targets) == 1 and isinstance(one_body.targets[0], ast.Subscript):
            assign_block_list.append([one_body])
            return True
    return False

def else_traverse(if_body, assign_block_list, const_func_name):
    else_body_list = if_body.orelse
    if len(else_body_list) > 1:
        return False
    elif not else_body_list:
        return False
    else:
        else_body_one = else_body_list[0]
        if isinstance(else_body_one, ast.If):
            return if_else_traverse(else_body_one, assign_block_list, const_func_name)
        return whether_fun_is_append(else_body_one, assign_block_list, const_func_name)

def if_else_traverse(if_body, assign_block_list, const_func_name):
    if_body_list = if_body.body
    if len(if_body_list) == 1:
        if_body_flag = whether_fun_is_append(if_body_list[0], assign_block_list, const_func_name)
    else:
        return False
    return if_body_flag and else_traverse(if_body, assign_block_list, const_func_name)

def if_traverse(one_body, assign_block_list, const_func_name):
    orelse = one_body.orelse
    if not orelse:
        return for_traverse(one_body, assign_block_list, const_func_name)
    else:
        return if_else_traverse(one_body, assign_block_list, const_func_name)

def for_traverse(node, assign_block_list, const_func_name):
    for_body_list = node.body
    if isinstance(node, ast.For) and node.orelse:
        return False
    if len(for_body_list) == 1:
        one_body = for_body_list[0]
        if isinstance(one_body, ast.For):
            return for_traverse(one_body, assign_block_list, const_func_name)
        elif isinstance(one_body, ast.If):
            return if_traverse(one_body, assign_block_list, const_func_name)
        elif isinstance(one_body, ast.Expr):
            return whether_fun_is_append(one_body, assign_block_list, const_func_name)
        elif isinstance(one_body, ast.Assign):
            return whether_fun_is_append(one_body, assign_block_list, const_func_name)
        else:
            return False
    else:
        return False

def filter_overlap(code_index_list):
    no_overlap_list = []
    if len(code_index_list) <= 1:
        return code_index_list
    for i in range(len(code_index_list)):
        code = code_index_list[i]
        beg = code[0].lineno
        end = code[0].end_lineno
        is_overlapped = False
        for j in range(len(code_index_list)):
            if i == j:
                continue
            fuzhu_beg = code_index_list[j][0].lineno
            fuzhu_end = code_index_list[j][0].end_lineno
            if beg >= fuzhu_beg and end <= fuzhu_end:
                is_overlapped = True
                break
        if not is_overlapped:
            no_overlap_list.append(code)
    return no_overlap_list

def is_use_var(next_child, vars):
    s = safe_unparse(next_child)
    if not s:
        return 0
    if s != list(vars)[0]:
        try:
            g = tokenize(BytesIO(s.encode('utf-8')).readline)
            for toknum, to_child, _, _, _ in g:
                if to_child.strip() == list(vars)[0]:
                    return 1
        except:
            pass
    return 0

def whether_first_var_is_empty_assign(tree, for_node, vars, const_func_name="append", const_empty_list=["[]"]):
    assign_stmt = None
    assign_stmt_lineno = None
    flag = 0

    time_var_list = get_time_var(vars)
    remove_ass_flag = 0
    
    def whether_contain_var(node, vars, time_var_list):
        count = 0
        s = safe_unparse(node)
        if not s:
            return 0
        if s != list(vars)[0]:
            try:
                g = tokenize(BytesIO(s.encode('utf-8')).readline)
                for toknum, child, _, _, _ in g:
                    if child in time_var_list:
                        count += 1
            except:
                pass
        return count

    time = whether_contain_var(for_node, vars, time_var_list)
    append_time = 0
    
    for child in ast.walk(for_node):
        # 1. 统计 append/add 调用
        if isinstance(child, ast.Call):
            a = []
            if whether_fun_is_append(child, a, const_func_name):
                append_time += 1
            
            # 检查函数调用参数是否使用了变量 (例如: func(a))
            try:
                fun_name = ""
                if hasattr(child.func, "attr"):
                    fun_name = child.func.attr
                elif hasattr(child.func, "id"):
                    fun_name = child.func.id
                else:
                    fun_name = safe_unparse(child.func).split(".")[-1]
                
                # 检查直接参数
                for arg in child.args:
                    if safe_unparse(arg) in time_var_list:
                        flag = 1
                        return flag, assign_stmt_lineno, assign_stmt, remove_ass_flag
                
                # 检查闭包/全局使用
                if check_call_usage_in_tree(tree, fun_name, time_var_list):
                    flag = 1
                    return flag, assign_stmt_lineno, assign_stmt, remove_ass_flag
            except:
                pass
        
        # 2. 统计字典赋值 (d[k] = v)
        elif isinstance(child, ast.Assign) and const_func_name == "__setitem__":
            a = []
            if whether_fun_is_append(child, a, const_func_name):
                append_time += 1

    if time - append_time > 0:
        flag = 1
        return flag, assign_stmt_lineno, assign_stmt, remove_ass_flag

    for_node_block_record = None
    for node in ast.walk(tree):
        if hasattr(node, "lineno") and node.lineno == for_node.lineno:
            break
        
        # 查找可能的父级块
        if hasattr(node, 'body') and isinstance(node.body, list):
            is_parent = False
            # 尝试判断 node 是否包裹了 for_node
            if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                if node.lineno < for_node.lineno <= node.end_lineno:
                    is_parent = True
            elif node.body and hasattr(node.body[0], 'lineno'):
                # 处理没有 lineno 的块 (如 Module)
                start = node.body[0].lineno
                end = node.body[-1].end_lineno if hasattr(node.body[-1], 'end_lineno') else 999999
                if start < for_node.lineno < end:
                    is_parent = True
            
            if is_parent or True: # 遍历所有可能的块寻找初始化
                for child in node.body:
                    if isinstance(child, ast.Assign):
                        try:
                            target_name = safe_unparse(child).strip().split("=")[0].strip()
                            value_str = safe_unparse(child.value)
                            
                            # 检查是否为目标变量的空初始化
                            if target_name == list(vars)[0]:
                                clean_val = value_str.replace(" ", "")
                                clean_consts = [x.replace(" ", "") for x in const_empty_list]
                                if clean_val in clean_consts:
                                    assign_stmt = child
                                    assign_stmt_lineno = child.lineno
                                    for_node_block_record = node
                                    flag = 2
                        except:
                            pass

    if for_node_block_record:
        for child in ast.iter_child_nodes(for_node_block_record):
            if child == for_node:
                remove_ass_flag = 1
        
        for node in ast.walk(for_node_block_record):
            if hasattr(node, "end_lineno") and hasattr(node, "lineno"):
                # 检查初始化和循环之间是否有干扰
                if node != assign_stmt and node.end_lineno < for_node.lineno and node.lineno > assign_stmt_lineno:
                    s = safe_unparse(node)
                    if s and s != list(vars)[0]:
                        try:
                            g = tokenize(BytesIO(s.encode('utf-8')).readline)
                            for toknum, child, _, _, _ in g:
                                if child.strip() in time_var_list:
                                    flag = 1
                                    return flag, assign_stmt_lineno, assign_stmt, remove_ass_flag
                        except:
                            pass
    
    return flag, assign_stmt_lineno, assign_stmt, remove_ass_flag

def get_complicated_for_comprehen_code_list(tree, content, const_empty_list=["[]"], const_func_name="append"):
    code_index_start_end_list = []
    if not hasattr(tree, 'body'):
        return []
    
    for ind_line, node in enumerate(ast.walk(tree)):
        if isinstance(node, ast.For):
            assign_block_list = []
            if for_traverse(node, assign_block_list, const_func_name):
                vars_set = set([])
                for each_block in assign_block_list:
                    pre_name, call_name = get_func_name(each_block[0])
                    if pre_name:
                        vars_set.add(pre_name)
                
                if len(vars_set) != 1:
                    continue
                
                flag, assign_stmt_lineno, assign_stmt, remove_ass_flag = whether_first_var_is_empty_assign(tree, node, vars_set, const_func_name, const_empty_list)
                
                if flag != 2:
                    continue
                
                code_index_start_end_list.append([node, assign_stmt, remove_ass_flag])

    code_index_start_end_list = filter_overlap(code_index_start_end_list)
    return code_index_start_end_list

def save_one_repo(repo_name, save_complicated_code_dir_pkl=None):
    pass 

if __name__ == '__main__':
    pass