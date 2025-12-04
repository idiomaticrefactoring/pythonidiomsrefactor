import sys
import ast
import os
import traceback
import copy
from sympy import sympify

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
from RefactoringIdioms.transform_c_s import transform_var_unpack_call

# ==========================================
# 核心辅助函数 (保留原有逻辑)
# ==========================================

def whether_add_end(slice_list, each_seq, arg_seq, step, new_arg_same_list, beg, end):
    if end == len(slice_list[1:]) and end > beg:
        # arg_list, ind_list, call node, step
        new_arg_same_list.append(
            [each_seq[beg:end + 1], arg_seq[1][beg:end + 1], arg_seq[2], step])

def whether_add(each_seq, arg_seq, step, new_arg_same_list, beg, end):
    if end > beg:
        new_arg_same_list.append(
            [each_seq[beg:end + 1], arg_seq[1][beg:end + 1], arg_seq[2], step])

def get_func_call_by_args(tree):
    arg_same_list = []
    new_arg_same_list = []
    
    # 1. 第一次遍历：寻找连续的 Subscript 参数 (如 a[0], a[1])
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            args_list = node.args
            var_set = []
            ind_list = []
            arg_one_list = []
            
            for ind_elts, e in enumerate(args_list):
                if isinstance(e, ast.Subscript):
                    if isinstance(e.slice, ast.Slice):
                        if len(var_set) > 1:
                            arg_same_list.append([arg_one_list, ind_list, node])
                        var_set = []
                        ind_list = []
                        arg_one_list = []
                        continue
                        
                    e_value = e.value
                    value_str = ast.unparse(e_value)
                    
                    if not var_set:
                        var_set.append(e_value)
                        ind_list.append(ind_elts)
                        arg_one_list.append(e)
                    else:
                        if value_str == ast.unparse(var_set[-1]):
                            var_set.append(e_value)
                            ind_list.append(ind_elts)
                            arg_one_list.append(e)
                            if ind_elts == len(args_list) - 1:
                                arg_same_list.append([arg_one_list, ind_list, node])
                        else:
                            if len(var_set) > 1:
                                arg_same_list.append([arg_one_list, ind_list, node])
                            var_set = [e_value]
                            ind_list = [ind_elts]
                            arg_one_list = [e]
                else:
                    if len(var_set) > 1:
                        arg_same_list.append([arg_one_list, ind_list, node])
                    var_set = []
                    ind_list = []
                    arg_one_list = []

    # 2. 第二次遍历：验证下标是否构成等差数列 (使用 sympy)
    for arg_seq in arg_same_list:
        each_seq = arg_seq[0]
        slice_list = []
        
        # 检查是否为字典定义 (排除字典下标)
        is_dict_access = False
        for e_child in ast.walk(tree):
            if hasattr(e_child, 'lineno') and e_child.lineno < each_seq[0].lineno and isinstance(e_child, (ast.Assign, ast.AnnAssign)):
                targets = e_child.targets if isinstance(e_child, ast.Assign) else [e_child.target]
                for tar in targets:
                    try:
                        if ast.unparse(tar) == ast.unparse(each_seq[0].value) \
                            and hasattr(e_child, "value") \
                            and (ast.unparse(e_child.value).startswith("dict(") or ast.unparse(e_child.value).startswith("{")):
                            is_dict_access = True
                            break
                    except:
                        continue
                if is_dict_access: break
        
        if is_dict_access:
            continue

        # 提取切片
        for arg in each_seq:
            slice_list.append(arg.slice)

        # 计算步长 (Step)
        step = None
        beg = 0
        end = 0
        
        for ind, e_node in enumerate(slice_list[1:]):
            pre_var_str = ast.unparse(slice_list[ind])
            e_str = ast.unparse(e_node)

            if not step:
                try:
                    step_val = str(sympify(f"{e_str}-({pre_var_str})"))
                except:
                    step_val = "None"

                if not step_val.isdigit() or (step_val.isdigit() and int(step_val) == 0):
                    whether_add(each_seq, arg_seq, step, new_arg_same_list, beg, end)
                    step = None
                    end += 1
                    beg = end
                else:
                    step = int(step_val)
                    end += 1
                    whether_add_end(slice_list, each_seq, arg_seq, step, new_arg_same_list, beg, end)
            else:
                try:
                    new_step = str(sympify(f"{e_str}-({pre_var_str})"))
                except:
                    new_step = "None"
                
                if new_step.isdigit() and int(new_step) == step:
                    end += 1
                    whether_add_end(slice_list, each_seq, arg_seq, step, new_arg_same_list, beg, end)
                else:
                    whether_add(each_seq, arg_seq, step, new_arg_same_list, beg, end)
                    step = None
                    end += 1
                    beg = end

    return new_arg_same_list

# ==========================================
# 主入口函数 (适配 main.py)
# ==========================================

def transform_star_call_code(content, config=None):
    """
    检测并重构函数调用中的参数解包。
    """
    if config is None:
        config = {}
        
    # [关键修改] 读取配置：最大解包元素数量限制
    # 配置文件: max-elements-to-unpack = false (表示不限制) 或 int
    max_limit = config.get("max-elements-to-unpack", False)
    
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
            
            # 获取候选列表
            new_arg_same_list = get_func_call_by_args(tree)

            for ind, arg_info_list in enumerate(new_arg_same_list):
                # arg_info_list 结构: [arg_nodes, ind_list, call_node, step]
                arg_nodes = arg_info_list[0]

                # [关键修改] 应用细粒度规则过滤
                # 如果设置了限制，且当前参数数量超过限制，则跳过
                if max_limit and isinstance(max_limit, int):
                    if len(arg_nodes) > max_limit:
                        continue

                if transform_var_unpack_call:
                    copy_arg_info_list = copy.deepcopy(arg_info_list)
                    # 调用转换模块生成 Starred 节点 (如 *a[i:i+3])
                    star_node = transform_var_unpack_call.transform_var_unpack_call_each_args(copy_arg_info_list)
                    
                    arg_str_list = [ast.unparse(arg) for arg in arg_nodes]
                    
                    # 记录行号
                    start_line = arg_nodes[0].lineno
                    end_line = arg_nodes[-1].end_lineno
                    line_list = [[start_line, end_line]]
                    
                    code_pair_list.append([
                        class_name if class_name != "Module" else "",
                        me_name,
                        ", ".join(arg_str_list), # 旧代码 (参数列表)
                        ast.unparse(star_node),  # 新代码 (解包语法)
                        line_list
                    ])

        return code_pair_list

    except Exception:
        # traceback.print_exc()
        return []

if __name__ == '__main__':
    # 简单测试
    code = "func(a[i], a[i+1], a[i+2])"
    print(transform_star_call_code(code)) 
    print(transform_star_call_code(code, config={"max-elements-to-unpack": 2}))
    print(transform_star_call_code(code, config={"max-elements-to-unpack": 3}))  